from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.schemas import MensagemEntrada, ListaSeparacaoMercado
from app.services import chamar_gemini
from app.whatsapp import enviar_mensagem_whatsapp

app = FastAPI(title="Projeto Hermes - Agente de Delivery")

# --- HABILITAÇÃO DO CORS PARA O LIVE SERVER E PAINEL ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def limpar_resposta_json(texto_raw: str) -> str:
    """Remove marcações de código Markdown (```json ... ```) se existirem na resposta da IA."""
    texto = texto_raw.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[-1]
        if texto.endswith("```"):
            texto = texto.rsplit("```", 1)[0]
    return texto.strip()

# --- PAINEL WEB DE TESTES PARA A APRESENTAÇÃO ---
@app.get("/", response_class=HTMLResponse)
async def carregar_painel():
    caminho_template = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if not os.path.exists(caminho_template):
        caminho_template = os.path.join("templates", "index.html")
        
    try:
        with open(caminho_template, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail="Arquivo templates/index.html não encontrado. Verifique a estrutura de pastas."
        )

# --- ENDPOINT DIRETO (UTILIZADO PELO PAINEL E SWAGGER) ---
@app.post("/webhook/mercado")
async def processar_lista_mercado(dados: MensagemEntrada):
    try:
        json_resposta = chamar_gemini(dados.mensagem)
        json_limpo = limpar_resposta_json(json_resposta)
        lista_validada = ListaSeparacaoMercado.model_validate_json(json_limpo)

        return {
            "status": "sucesso",
            "cliente": dados.telefone,
            "lista_separacao": lista_validada
        }
    except Exception as e:
        print(f"❌ Erro no endpoint /webhook/mercado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- WEBHOOK PARA EVENTOS ENTRANTES DO WHATSAPP ---
@app.post("/webhook/whatsapp")
async def webhook_whatsapp(request: Request):
    data = await request.json()
    
    try:
        event = data.get("event")
        if event == "messages.upsert":
            message_data = data.get("data", {})
            key = message_data.get("key", {})
            
            if key.get("fromMe"):
                return {"status": "ignored"}
                
            remote_jid = key.get("remoteJid", "")
            numero_cliente = remote_jid.split("@")[0]
            
            mensagem_texto = (
                message_data.get("message", {}).get("conversation") or
                message_data.get("message", {}).get("extendedTextMessage", {}).get("text")
            )
            
            if mensagem_texto:
                json_resposta = chamar_gemini(mensagem_texto)
                json_limpo = limpar_resposta_json(json_resposta)
                lista_validada = ListaSeparacaoMercado.model_validate_json(json_limpo)
                enviar_mensagem_whatsapp(numero_cliente, lista_validada.mensagem_resposta)
                
        return {"status": "processed"}
    except Exception as e:
        print(f"Erro no webhook do WhatsApp: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)