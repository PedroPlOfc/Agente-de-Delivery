"""Lista os modelos disponíveis para a chave configurada no Gemini API."""
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    raise SystemExit("Configure GEMINI_API_KEY no arquivo .env antes de listar os modelos.")

try:
    from google import genai
except ImportError as exc:
    raise SystemExit("SDK google-genai ausente. Execute: pip install -r requirements.txt") from exc

client = genai.Client(api_key=api_key)
print("Modelos que anunciam suporte a geração de conteúdo:")
for model in client.models.list():
    supported_actions = getattr(model, "supported_actions", None) or []
    if not supported_actions or "generateContent" in supported_actions:
        print(f"- {model.name}")
