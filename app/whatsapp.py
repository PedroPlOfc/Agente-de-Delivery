import logging

import requests

from app import config

log = logging.getLogger("cana.whatsapp")


def enviar_mensagem_whatsapp(numero: str, texto: str) -> bool:
    """Envia o texto ao cliente pela Evolution API (v1 ou v2, conforme EVOLUTION_API_VERSION)."""
    if not config.EVOLUTION_API_KEY or not config.EVOLUTION_API_URL:
        log.warning("Evolution API não configurada. Envio ignorado.")
        return False

    url = f"{config.EVOLUTION_API_URL}/message/sendText/{config.EVOLUTION_INSTANCE}"
    headers = {"apikey": config.EVOLUTION_API_KEY, "Content-Type": "application/json"}
    numero_limpo = "".join(filter(str.isdigit, str(numero)))

    if config.EVOLUTION_API_VERSION.startswith("1"):
        payload = {"number": numero_limpo, "options": {"delay": 1200, "presence": "composing"},
                   "textMessage": {"text": texto}}
    else:
        payload = {"number": numero_limpo, "text": texto, "delay": 1200}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code in (200, 201):
            return True
        log.error("Evolution API respondeu %s: %s", resp.status_code, resp.text[:300])
    except requests.RequestException as e:
        log.error("Erro de conexão com a Evolution API: %s", e)
    return False
