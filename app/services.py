import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_INSTRUCTION = """
Você é o Hermes, um assistente virtual de inteligência artificial para um supermercado.
Analise o pedido do cliente e extraia os itens rigorosamente no formato JSON.
Categorias permitidas: Açougue, Laticínios e Frios, Hortifruti, Mercearia, Bebidas, Limpeza e Higiene, Outros.
"""

def extrair_itens_inteligente(texto: str) -> list:
    """Parser regex resiliente para extrair produtos, quantidades e categorias localmente."""
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    itens = []

    mapeamento_categorias = {
        "arroz": ("Mercearia", "kg"),
        "feijão": ("Mercearia", "kg"),
        "feijao": ("Mercearia", "kg"),
        "macarrão": ("Mercearia", "pacote"),
        "macarrao": ("Mercearia", "pacote"),
        "queijo": ("Laticínios e Frios", "g"),
        "presunto": ("Laticínios e Frios", "g"),
        "leite": ("Laticínios e Frios", "caixa"),
        "coca": ("Bebidas", "fardo"),
        "cerveja": ("Bebidas", "fardo"),
        "refrigerante": ("Bebidas", "unidade"),
        "carne": ("Açougue", "kg"),
        "frango": ("Açougue", "kg"),
        "detergente": ("Limpeza e Higiene", "unidade"),
        "sabão": ("Limpeza e Higiene", "unidade"),
    }

    for linha in linhas:
        linha_lower = linha.lower()
        
        # Tenta extrair quantidade (ex: 2kg, 2k, 10 reais, 2 fardos)
        qtd_match = re.search(r'(\d+(?:[\.,]\d+)?)', linha)
        qtd = float(qtd_match.group(1).replace(',', '.')) if qtd_match else 1.0

        # Identifica categoria e unidade padrão baseada no produto
        cat_encontrada = "Mercearia"
        unid_encontrada = "un"
        
        for palavra_chave, (cat, unid) in mapeamento_categorias.items():
            if palavra_chave in linha_lower:
                cat_encontrada = cat
                unid_encontrada = unid
                break

        # Limpa o nome do produto removendo a quantidade do início
        nome_produto = re.sub(r'^\d+\s*(?:kg|k|g|fardos|fardo|reais|un|pacotes)?\s*(?:de)?\s*', '', linha, flags=re.IGNORECASE).strip()
        if not nome_produto:
            nome_produto = linha

        itens.append({
            "produto": nome_produto.capitalize(),
            "marca_preferida": None,
            "quantidade": qtd,
            "unidade_medida": unid_encontrada,
            "categoria": cat_encontrada,
            "aceita_substituicao": True,
            "observacao": ""
        })

    return itens if itens else [{
        "produto": texto[:30],
        "marca_preferida": None,
        "quantidade": 1.0,
        "unidade_medida": "un",
        "categoria": "Outros",
        "aceita_substituicao": True,
        "observacao": ""
    }]


def gerar_resposta_local(texto_mensagem: str) -> str:
    """Monta a payload do Hermes garantindo o formato do Pydantic sem depender da nuvem."""
    itens = extrair_itens_inteligente(texto_mensagem)
    mock_data = {
        "nome_cliente": "Cliente Hermes",
        "endereco_entrega": None,
        "itens": itens,
        "duvida_ou_incompleto": False,
        "mensagem_resposta": f"Olá! Recebi seu pedido com {len(itens)} item(ns) e já enviei para a equipe de separação do mercado!"
    }
    return json.dumps(mock_data, ensure_ascii=False)


def chamar_gemini(texto_mensagem: str) -> str:
    """Tenta executar na API do Gemini. Em caso de 503/429/404, aciona o Fallback Local."""
    if not client:
        return gerar_resposta_local(texto_mensagem)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json"
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"Extraia a lista de compras: {texto_mensagem}",
            config=config
        )
        return response.text
    except Exception as e:
        print(f"⚠️ API externa indisponível ({e}). Executando via Engine Local Hermes...")
        return gerar_resposta_local(texto_mensagem)