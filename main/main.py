import os
from typing import List, Optional, TypedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Carrega as variáveis do arquivo .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A variável GEMINI_API_KEY não foi encontrada no arquivo .env")

genai.configure(api_key=api_key)

app = FastAPI(title="Agente de Delivery - Varejo e Supermercados")

# --- SCHEMA TYPEDDICT PARA COMPATIBILIDADE COM A SDK DO GEMINI ---
class ItemMercadoSchema(TypedDict):
    produto: str
    marca_preferida: Optional[str]
    quantidade: float
    unidade_medida: str
    categoria: Optional[str]
    aceita_substituicao: bool
    observacao: Optional[str]

class ListaSeparacaoMercadoSchema(TypedDict):
    nome_cliente: Optional[str]
    endereco_entrega: Optional[str]
    itens: List[ItemMercadoSchema]
    duvida_ou_incompleto: bool
    mensagem_resposta: str

# --- MODELOS PYDANTIC PARA VALIDAÇÃO DA RESPOSTA E FASTAPI ---
class ItemMercado(BaseModel):
    produto: str
    marca_preferida: Optional[str] = None
    quantidade: float
    unidade_medida: str
    categoria: Optional[str] = None
    aceita_substituicao: bool = True
    observacao: Optional[str] = ""

class ListaSeparacaoMercado(BaseModel):
    nome_cliente: Optional[str] = None
    endereco_entrega: Optional[str] = None
    itens: List[ItemMercado]
    duvida_ou_incompleto: bool
    mensagem_resposta: str

class MensagemEntrada(BaseModel):
    telefone: str
    mensagem: str

# --- SYSTEM PROMPT FOCADO EM VAREJO ---
SYSTEM_PROMPT_MERCADO = """
Você é o assistente virtual de delivery do 'Supermercado Central'. 
Sua função é interpretar listas de compras em linguagem natural enviadas por clientes e transformá-las em uma lista técnica organizada para a equipe de separação (pickers) do mercado.

REGRAS DE INTERPRETAÇÃO:
1. Identifique produto, quantidade, unidade de medida e marca (se houver).
2. Se o cliente pedir por valor em dinheiro (ex: '10 reais de queijo'), defina quantidade=10.0 e unidade_medida='reais'.
3. Se o cliente pedir por peso sem especificar a unidade exata (ex: 'meio quilo de queijo'), converta para quantidade=0.5 e unidade_medida='kg'.
4. Classifique cada item na categoria correta de setor do mercado ('Hortifruti', 'Açougue', 'Limpeza', 'Mercearia', 'Laticínios', 'Padaria', 'Bebidas').
5. Se o produto for muito vago (ex: 'quero carne' ou 'traga sabão'), marque 'duvida_ou_incompleto' como True e pergunte na 'mensagem_resposta' qual o tipo de corte/produto desejado.
6. Identifique observações sobre o estado do produto (ex: frutos maduros/verdes, cortes de carne).
"""

# --- INICIALIZAÇÃO COM O MODELO CONFIRMADO DA SUA LISTA ---
model = genai.GenerativeModel(
    model_name="models/gemini-flash-lite-latest",
    system_instruction=SYSTEM_PROMPT_MERCADO,
)

# --- CHAMADA COM RETENTATIVA AUTOMÁTICA EM CASO DE PICOS ---
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=2, min=10, max=30),  # Espera mais tempo se der 429/503
    reraise=True
)
def chamar_gemini(mensagem: str):
    response = model.generate_content(
        mensagem,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ListaSeparacaoMercadoSchema,
            temperature=0.1,
        ),
    )
    return response.text

# --- ENDPOINT DA API ---
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)