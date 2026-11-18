import logging
import secrets
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import config
from app.java_api import JavaApiError, admin_call, admin_login, verificar_saude
from app.estado import carregar_carrinho, salvar_carrinho
from app.schemas import MensagemEntrada
from app.services import chamar_gemini
from app.whatsapp import enviar_mensagem_whatsapp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("cana")

app = FastAPI(title="CANA — Assistente de Delivery 🌿", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["Content-Type", "Accept"],
)

templates = Jinja2Templates(directory="templates")

_LIMITE, _JANELA = 30, 60
_acessos: dict = defaultdict(deque)

def _checar_rate_limit(ip: str) -> None:
    agora = time.monotonic()
    fila = _acessos[ip]
    while fila and agora - fila[0] > _JANELA:
        fila.popleft()
    if len(fila) >= _LIMITE:
        raise HTTPException(status_code=429, detail="Muitas requisições. Aguarde um instante.")
    fila.append(agora)

_vistos: deque = deque(maxlen=500)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_home(request: Request):
    """Painel administrativo; toda persistência continua no serviço Java."""
    return templates.TemplateResponse(request, "admin.html")


def _admin_token(request: Request) -> str:
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer ") or not authorization[7:].strip():
        raise HTTPException(status_code=401, detail="Faça login no CANA Admin.")
    return authorization[7:].strip()


def _admin_proxy(method: str, path: str, request: Request, *, params=None, payload=None):
    try:
        return admin_call(method, path, _admin_token(request), params=params, payload=payload)
    except JavaApiError as exc:
        message = str(exc)
        status = 401 if "HTTP 401" in message else (403 if "HTTP 403" in message else (400 if "HTTP 400" in message else 502))
        raise HTTPException(status_code=status, detail=message) from exc


@app.post("/admin/api/login")
async def admin_login_proxy(payload: dict, request: Request):
    _checar_rate_limit(request.client.host if request.client else "desconhecido")
    try:
        return admin_login(str(payload.get("username", "")), str(payload.get("password", "")))
    except JavaApiError as exc:
        message = str(exc)
        status = 401 if "HTTP 401" in message else 502
        raise HTTPException(status_code=status, detail=message) from exc


@app.get("/admin/api/dashboard")
def admin_dashboard(request: Request):
    return _admin_proxy("GET", "/api/admin/dashboard", request)


@app.get("/admin/api/products")
def admin_products(request: Request, query: str = ""):
    return _admin_proxy("GET", "/api/admin/products", request, params={"query": query})


@app.post("/admin/api/products")
def admin_create_product(payload: dict, request: Request):
    return _admin_proxy("POST", "/api/admin/products", request, payload=payload)


@app.put("/admin/api/products/{product_id}")
def admin_update_product(product_id: int, payload: dict, request: Request):
    return _admin_proxy("PUT", f"/api/admin/products/{product_id}", request, payload=payload)


@app.post("/admin/api/products/{product_id}/stock-movements")
def admin_stock_movement(product_id: int, payload: dict, request: Request):
    return _admin_proxy("POST", f"/api/admin/products/{product_id}/stock-movements", request, payload=payload)


@app.get("/admin/api/stock-movements")
def admin_stock_history(request: Request):
    return _admin_proxy("GET", "/api/admin/stock-movements", request)


@app.get("/admin/api/orders")
def admin_orders(request: Request):
    return _admin_proxy("GET", "/api/admin/orders", request)


@app.patch("/admin/api/orders/{order_id}/status")
def admin_update_order_status(order_id: int, payload: dict, request: Request):
    return _admin_proxy("PATCH", f"/api/admin/orders/{order_id}/status", request, payload=payload)


@app.get("/health")
def health():
    """Liveness do serviço Python (não depende do backend Java)."""
    return {"status": "ok", "service": "cana-python"}


@app.get("/ready")
def ready():
    """Readiness: confirma que o serviço Java está acessível."""
    if not verificar_saude():
        raise HTTPException(status_code=503, detail="Backend Java indisponível.")
    return {"status": "ready", "python": "ok", "java": "ok"}

@app.post("/webhook/mercado")
def webhook_mercado(payload: MensagemEntrada, request: Request):
    _checar_rate_limit(request.client.host if request.client else "desconhecido")

    try:
        itens = payload.itens_atuais if payload.itens_atuais is not None else carregar_carrinho(payload.telefone)
        lista = chamar_gemini(payload.mensagem, itens)
        salvar_carrinho(payload.telefone, lista["itens"])
        return {"status": "success", "cliente": payload.telefone, "lista_separacao": lista}
    except JavaApiError as exc:
        log.error("Backend Java indisponível durante processamento: %s", exc)
        raise HTTPException(status_code=503, detail="O serviço de dados está temporariamente indisponível.") from exc

def _extrair_texto(message: dict) -> str:
    if not isinstance(message, dict):
        return ""
    return (
        message.get("conversation")
        or (message.get("extendedTextMessage") or {}).get("text")
        or ""
    )

def _processar_mensagem_whatsapp(telefone: str, texto: str) -> None:
    try:
        itens = carregar_carrinho(telefone)
        lista = chamar_gemini(texto, itens)
        salvar_carrinho(telefone, lista["itens"])
        enviar_mensagem_whatsapp(telefone, lista["mensagem_resposta"])
    except Exception:  # noqa: BLE001
        log.exception("Erro ao processar mensagem no WhatsApp via Cana")

@app.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request, background: BackgroundTasks, token: Optional[str] = None):
    if config.WEBHOOK_TOKEN and not secrets.compare_digest(token or "", config.WEBHOOK_TOKEN):
        raise HTTPException(status_code=401, detail="Token inválido")

    try:
        corpo = await request.json()
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="JSON inválido")

    evento = str(corpo.get("event", "")).lower().replace("_", ".")
    if evento != "messages.upsert":
        return {"status": "ignored"}

    data = corpo.get("data") or {}
    if isinstance(data, list):
        data = data[0] if data else {}
    key = data.get("key") or {}
    jid = key.get("remoteJid", "")

    if key.get("fromMe") or not jid or jid.endswith("@g.us") or jid.startswith("status@"):
        return {"status": "ignored"}

    texto = _extrair_texto(data.get("message", {})).strip()
    if not texto:
        return {"status": "ignored"}

    msg_id = key.get("id")
    if msg_id:
        if msg_id in _vistos:
            return {"status": "ignored"}
        _vistos.append(msg_id)

    telefone = jid.split("@")[0]
    background.add_task(_processar_mensagem_whatsapp, telefone, texto[: config.MAX_TAMANHO_MENSAGEM])
    return {"status": "accepted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)