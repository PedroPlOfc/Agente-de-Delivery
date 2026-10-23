import os
from dotenv import load_dotenv

load_dotenv()

def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]

# IA (a ausência da chave NÃO derruba a aplicação: usa-se o motor local)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# WhatsApp (Evolution API)
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080").rstrip("/")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "mercado_central")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_API_VERSION = os.getenv("EVOLUTION_API_VERSION", "2")

# Segurança
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
CORS_ORIGINS = _lista(
    os.getenv("CORS_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5500")
)
MAX_TAMANHO_MENSAGEM = 1000

# Estado
REDIS_URL = os.getenv("REDIS_URL", "")
