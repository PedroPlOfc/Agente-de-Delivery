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
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    itens = []

    mapeamento_categorias = {
        "arroz": "Mercearia",
        "feijão": "Mercearia",
        "feijao": "Mercearia",
        "macarrão": "Mercearia",
        "macarrao": "Mercearia",
        "queijo": "Laticínios e Frios",
        "presunto": "Laticínios e Frios",
        "leite": "Laticínios e Frios",
        "coca": "Bebidas",
        "cerveja": "Bebidas",
        "refrigerante": "Bebidas",
        "carne": "Açougue",
        "frango": "Açougue",
        "detergente": "Limpeza e Higiene",
        "sabão": "Limpeza e Higiene",
    }

    for linha in linhas:
        linha_lower = linha.lower()
        
        # 1. Extrai a quantidade numérica (ex: 2, 10, 1.5)
        qtd_match = re.search(r'(\d+(?:[\.,]\d+)?)', linha)
        qtd = float(qtd_match.group(1).replace(',', '.')) if qtd_match else 1.0

        # 2. Captura dinamicamente a unidade mesmo grudada no número (ex: 2kg, 10reais)
        unid_match = re.search(r'(kg|k|g|fardos|fardo|reais|real|pacotes|pacote|caixas|caixa|unidades|un)', linha_lower)
        if unid_match:
            unid_encontrada = unid_match.group(1)
            if unid_encontrada in ['k', 'kg']:
                unid_encontrada = 'kg'
            elif unid_encontrada in ['real', 'reais']:
                unid_encontrada = 'reais'
            elif unid_encontrada in ['fardos', 'fardo']:
                unid_encontrada = 'fardos'
            elif unid_encontrada in ['pacotes', 'pacote']:
                unid_encontrada = 'pacote'
        else:
            unid_encontrada = "un"

        # 3. Mapeia a categoria correspondente ao produto
        cat_encontrada = "Outros"
        for palavra_chave, cat in mapeamento_categorias.items():
            if palavra_chave in linha_lower:
                cat_encontrada = cat
                break

        # 4. Limpa o nome do produto removendo a quantidade, unidade e preposição do início
        nome_produto = re.sub(
            r'^\d+\s*(?:kg|k|g|fardos|fardo|reais|real|un|pacotes|pacote|caixas|caixa)?\s*(?:de)?\s*', 
            '', 
            linha, 
            flags=re.IGNORECASE
        ).strip()
        
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
    """Função importada pelo main.py para processar o pedido via Gemini ou Fallback Local."""
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