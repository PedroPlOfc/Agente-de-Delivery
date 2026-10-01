import httpx
import webbrowser
import os

BASE_URL = "https://evolution-api-delivery.onrender.com"
API_KEY = "d8k1m6v1n2845j1z98c1f4b9x1h3b9a"
INSTANCE_NAME = "mercado_central"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

# Configuração de timeout estendido para o Render (60 segundos)
timeout_config = httpx.Timeout(60.0, connect=60.0)

# 1. Tenta criar/verificar a instância
print("1. Acordando o servidor no Render e verificando a instância (pode levar até 40s se estiver em repouso)...")
payload_create = {
    "instanceName": INSTANCE_NAME,
    "token": API_KEY,
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

try:
    res_create = httpx.post(
        f"{BASE_URL}/instance/create", 
        json=payload_create, 
        headers=headers, 
        timeout=timeout_config
    )
    print("Status da criação:", res_create.status_code)
except Exception as e:
    print("Aviso na criação (o servidor pode ter demorado a responder ou a instância já existe):", e)

# 2. Busca o QR Code de conexão
print("\n2. Solicitando QR Code de conexão...")
try:
    res_connect = httpx.get(
        f"{BASE_URL}/instance/connect/{INSTANCE_NAME}", 
        headers=headers, 
        timeout=timeout_config
    )

    if res_connect.status_code in [200, 201]:
        data = res_connect.json()
        base64_qr = data.get("base64") or data.get("qrcode", {}).get("base64")
        
        if base64_qr:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>QR Code - Evolution API</title>
                <style>
                    body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; background: #f0f2f5; }}
                    .card {{ background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; }}
                    img {{ width: 300px; height: 300px; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>Escaneie o QR Code no WhatsApp</h2>
                    <img src="{base64_qr}" alt="QR Code WhatsApp" />
                    <p>Abra o WhatsApp > Dispositivos Conectados > Conectar Dispositivo</p>
                </div>
            </body>
            </html>
            """
            
            with open("qrcode_view.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            print("\n✅ QR Code gerado com sucesso!")
            print("Abrindo no navegador...")
            webbrowser.open("file://" + os.path.abspath("qrcode_view.html"))
        else:
            print("❌ O QR Code não veio na resposta. É provável que o WhatsApp já esteja conectado!")
            print("Resposta da API:", data)
    else:
        print(f"❌ Erro ao buscar QR Code ({res_connect.status_code}):", res_connect.text)

except Exception as e:
    print("Erro na conexão com o Render:", e)