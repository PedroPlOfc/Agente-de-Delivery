from fastapi import FastAPI, HTTPException, Request
from app.schemas import MensagemEntrada, ListaSeparacaoMercado
from app.services import chamar_gemini
from app.whatsapp import enviar_mensagem_whatsapp

app = FastAPI(title="Agente de Delivery - Varejo e Supermercados")

# --- ENDPOINT DIRETO (SWAGGER / INTERNO) ---
@app.post("/webhook/mercado")
async def processar_lista_mercado(dados: MensagemEntrada):
    try:
        json_resposta = chamar_gemini(dados.mensagem)
        lista_validada = ListaSeparacaoMercado.model_validate_json(json_resposta)

        return {
            "status": "sucesso",
            "cliente": dados.telefone,
            "lista_separacao": lista_validada
        }
    except Exception as e:
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
            
            # Descarta mensagens enviadas pelo próprio robô
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
                lista_validada = ListaSeparacaoMercado.model_validate_json(json_resposta)
                
                # Envia a resposta amigável de volta para o cliente
                enviar_mensagem_whatsapp(numero_cliente, lista_validada.mensagem_resposta)
                
        return {"status": "processed"}
    except Exception as e:
        print(f"Erro no webhook do WhatsApp: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)