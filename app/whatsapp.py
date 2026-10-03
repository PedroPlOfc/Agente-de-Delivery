import requests
from app.config import EVOLUTION_API_URL, EVOLUTION_INSTANCE, EVOLUTION_API_KEY

def enviar_mensagem_whatsapp(numero: str, texto: str) -> bool:
    """Dispara a mensagem formatada de volta ao WhatsApp do cliente."""
    if not EVOLUTION_API_KEY or not EVOLUTION_API_URL:
        print("⚠️ Configurações da Evolution API não encontradas no .env. Envio ignorado.")
        return False

    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Mantém apenas os números (ex: +55 (81) 99999-9999 -> 5581999999999)
    numero_limpo = "".join(filter(str.isdigit, str(numero)))

    payload = {
        "number": numero_limpo,
        "options": {
            "delay": 1200, 
            "presence": "composing"
        },
        "textMessage": {
            "text": texto
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ Mensagem enviada com sucesso para {numero_limpo}!")
            return True
        else:
            print(f"❌ Erro na Evolution API ({response.status_code}): {response.text}")
            return False

    except Exception as e:
        print(f"⚠️ Erro de conexão ao enviar mensagem via WhatsApp: {e}")
        return False