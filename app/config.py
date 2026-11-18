import os
from dotenv import load_dotenv

load_dotenv()


def _lista(valor: str) -> list[str]:
    return [v.strip() for v in valor.split(",") if v.strip()]


# IA: a ausência de chave mantém o motor local determinístico disponível.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Comunicação com o backend Java. Python não acessa banco de dados diretamente.
JAVA_API_URL = os.getenv("JAVA_API_URL", "http://localhost:8081").rstrip("/")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")
try:
    JAVA_API_TIMEOUT = float(os.getenv("JAVA_API_TIMEOUT", "8"))
except ValueError:
    JAVA_API_TIMEOUT = 8.0

# WhatsApp (Evolution API)
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080").rstrip("/")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "cana_delivery")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_API_VERSION = os.getenv("EVOLUTION_API_VERSION", "2")

# Segurança e CORS
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "")
CORS_ORIGINS = _lista(
    os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5500",
    )
)
MAX_TAMANHO_MENSAGEM = 1000
