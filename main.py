from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

from app.services import chamar_gemini

app = FastAPI(title="Projeto Hermes — Fast Delivery")

# Permite requisições do frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/webhook/mercado")
async def webhook_mercado(request: Request):
    data = await request.json()
    mensagem = data.get("mensagem", "")
    itens_atuais = data.get("itens_atuais", [])
    
    # Processa o pedido passando o contexto atual dos itens
    resposta_json_str = chamar_gemini(mensagem, itens_atuais)
    
    return {
        "status": "success",
        "lista_separacao": resposta_json_str
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)