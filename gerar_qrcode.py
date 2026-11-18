"""Cria (quando necessário) a instância e abre o QR Code da Evolution API local."""
import base64
import json
import os
import webbrowser
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

# Este script roda no Windows/host, então usa localhost, não o DNS interno do Docker.
BASE_URL = os.getenv("EVOLUTION_LOCAL_API_URL", "http://localhost:8080").rstrip("/")
API_KEY = os.getenv("EVOLUTION_API_KEY", "")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE", "cana_delivery")

if not API_KEY:
    raise SystemExit("Configure EVOLUTION_API_KEY no arquivo .env antes de gerar o QR Code.")

headers = {"apikey": API_KEY, "Content-Type": "application/json"}
timeout = httpx.Timeout(60.0, connect=15.0)

print(f"Verificando a instância '{INSTANCE_NAME}' em {BASE_URL}...")
try:
    create_response = httpx.post(
        f"{BASE_URL}/instance/create",
        json={
            "instanceName": INSTANCE_NAME,
            "token": API_KEY,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
        },
        headers=headers,
        timeout=timeout,
    )
    if create_response.status_code not in (200, 201, 409):
        print(f"Aviso ao criar/verificar instância: HTTP {create_response.status_code}")
        print(create_response.text[:500])
except httpx.RequestError as exc:
    raise SystemExit(
        "Não foi possível acessar a Evolution API. Confirme se o Docker Desktop e o serviço estão ativos."
    ) from exc

print("Solicitando QR Code...")
try:
    response = httpx.get(
        f"{BASE_URL}/instance/connect/{INSTANCE_NAME}",
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
except httpx.HTTPError as exc:
    raise SystemExit(f"Falha ao solicitar o QR Code: {exc}") from exc

data = response.json()
qr_data = data.get("qrcode") or {}
base64_qr = data.get("base64") or qr_data.get("base64")
qr_text = data.get("code") or qr_data.get("code")

if base64_qr:
    if not base64_qr.startswith("data:image"):
        base64_qr = f"data:image/png;base64,{base64_qr}"
    qr_markup = f'<img src="{base64_qr}" alt="QR Code de conexão do WhatsApp">'
elif qr_text:
    qr_markup = (
        '<div id="qrcode"></div>'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>'
        f'<script>new QRCode(document.getElementById("qrcode"), '
        f'{{text: {json.dumps(qr_text)}, width: 300, height: 300}});</script>'
    )
else:
    print("A Evolution API não retornou o QR Code. A instância pode já estar conectada.")
    print("Estado retornado:", data.get("instance", {}).get("state", "não informado"))
    raise SystemExit(0)

html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conectar WhatsApp ao CANA</title>
  <style>
    body {{ min-height: 100vh; margin: 0; display: grid; place-items: center; background: #f1f5f9; font-family: Arial, sans-serif; color: #172554; }}
    main {{ max-width: 420px; margin: 24px; padding: 28px; border-radius: 18px; background: white; text-align: center; box-shadow: 0 12px 40px #0f172a18; }}
    img {{ width: min(300px, 80vw); height: auto; }}
    p {{ line-height: 1.55; color: #475569; }}
  </style>
</head>
<body>
  <main>
    <h1>Conecte o WhatsApp ao CANA 🌿</h1>
    {qr_markup}
    <p>No WhatsApp, abra <strong>Dispositivos conectados</strong> e escolha <strong>Conectar dispositivo</strong>.</p>
    <p>Depois de parear, execute <code>configurar-webhook.ps1</code> para ligar as mensagens ao CANA.</p>
  </main>
</body>
</html>"""

output = Path(__file__).resolve().with_name("qrcode_view.html")
output.write_text(html, encoding="utf-8")
webbrowser.open(output.as_uri())
print(f"QR Code salvo em {output} e aberto no navegador.")
