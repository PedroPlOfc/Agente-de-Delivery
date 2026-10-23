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
from app.estado import carregar_carrinho, salvar_carrinho
from app.schemas import MensagemEntrada
from app.services import chamar_gemini
from app.whatsapp import enviar_mensagem_whatsapp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("cana")

app = FastAPI(title="Sacolão da Economia — Assistente Cana 🌿")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook/mercado")
def webhook_mercado(payload: MensagemEntrada, request: Request):
    _checar_rate_limit(request.client.host if request.client else "desconhecido")

    itens = payload.itens_atuais if payload.itens_atuais is not None else carregar_carrinho(payload.telefone)
    lista = chamar_gemini(payload.mensagem, itens)
    salvar_carrinho(payload.telefone, lista["itens"])
    return {"status": "success", "cliente": payload.telefone, "lista_separacao": lista}

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