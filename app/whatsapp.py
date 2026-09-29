import requests
from app.config import EVOLUTION_API_URL, EVOLUTION_INSTANCE, EVOLUTION_API_KEY

def enviar_mensagem_whatsapp(numero: str, texto: str) -> None:
    """Dispara a mensagem formatada de volta ao WhatsApp do cliente."""
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": numero,
        "options": {"delay": 1200, "presence": "composing"},
        "textMessage": {"text": texto}
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem via WhatsApp: {e}")