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
Você é o Hermes, um assistente virtual inteligente e atencioso para um supermercado.
Sua missão é realizar o atendimento de pedidos via WhatsApp de forma clara e objetiva.

REGRAS DE CONDUÇÃO DA CONVERSA:

1. PRIMEIRA INTERAÇÃO (Recebimento da Lista):
   - Confirme o recebimento dos itens extraídos.
   - Apresente a lista organizada ao cliente e pergunte se está tudo certo ou se ele deseja adicionar/remover algo.

2. SEGUNDA INTERAÇÃO (Confirmação dos Itens):
   - Assim que o cliente confirmar a lista, pergunte sobre a forma de pagamento:
     "Como prefere realizar o pagamento?"
     Option A: Pelo aplicativo (Online/PIX).
     Option B: Na entrega (Maquininha de Cartão ou Espécie/Dinheiro).
   - Se for em Espécie/Dinheiro na entrega, pergunte se precisará de troco e para qual valor (ex: "Troco para R$ 100,00?").

3. IDENTIFICAÇÃO DO CLIENTE:
   - Extraia e utilize o nome informado pelo cliente se ele disser. O telefone já é identificado automaticamente pelo sistema.

SAÍDA OBRIGATÓRIA (JSON):
Retorne estritamente um JSON com a estrutura:
{
  "nome_cliente": "Nome do cliente se informado ou null",
  "endereco_entrega": "Endereço se informado ou null",
  "itens": [
    {
      "produto": "Nome do produto",
      "marca_preferida": null,
      "quantidade": 1.0,
      "unidade_medida": "un",
      "categoria": "Mercearia",
      "aceita_substituicao": true,
      "observacao": ""
    }
  ],
  "forma_pagamento": "PIX / Cartão na entrega / Espécie (Troco para R$ X) / Pelo aplicativo / A definir",
  "duvida_ou_incompleto": false,
  "mensagem_resposta": "Texto amigável formatado para envio no WhatsApp"
}
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

    # Dicionário de padronização de unidades
    depara_unidades = {
        "kg": "kg",
        "k": "kg",
        "g": "g",
        "reais": "reais",
        "real": "reais",
        "fardos": "fardo",
        "fardo": "fardo",
        "pacotes": "pct",
        "pacote": "pct",
        "pct": "pct",
        "caixas": "cx",
        "caixa": "cx",
        "unidades": "un",
        "unidade": "un",
        "un": "un",
    }

    for linha in linhas:
        linha_lower = linha.lower()
        
        # 1. Extrai a quantidade numérica (ex: 2, 10, 1.5)
        qtd_match = re.search(r'(\d+(?:[\.,]\d+)?)', linha)
        qtd = float(qtd_match.group(1).replace(',', '.')) if qtd_match else 1.0

        # 2. Captura a unidade mesmo grudada no número (ex: 2kg, 3pacotes, 5unidades)
        unid_match = re.search(r'(kg|k|g|fardos|fardo|reais|real|pacotes|pacote|pct|caixas|caixa|unidades|unidade|un)', linha_lower)
        if unid_match:
            termo_encontrado = unid_match.group(1)
            unid_encontrada = depara_unidades.get(termo_encontrado, "un")
        else:
            unid_encontrada = "un"

        # 3. Mapeia a categoria do produto
        cat_encontrada = "Outros"
        for palavra_chave, cat in mapeamento_categorias.items():
            if palavra_chave in linha_lower:
                cat_encontrada = cat
                break

        # 4. Limpa o nome do produto removendo a quantidade e a unidade do início
        nome_produto = re.sub(
            r'^\d+\s*(?:kg|k|g|fardos|fardo|reais|real|un|unidades|unidade|pacotes|pacote|pct|caixas|caixa)?\s*(?:de)?\s*', 
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
    
    # Formata a lista de itens para a mensagem de confirmação do WhatsApp
    lista_formatada = "\n".join([
        f"• {item['quantidade']} {item['unidade_medida']} de {item['produto']}" 
        for item in itens
    ])

    mensagem_whatsapp = (
        f"Olá! Recebi o seu pedido:\n\n"
        f"{lista_formatada}\n\n"
        f"1️⃣ Está tudo certinho com a sua lista ou gostaria de alterar algo?\n"
        f"2️⃣ Qual será a forma de pagamento? (Pelo aplicativo ou na entrega em cartão/espécie com troco?)"
    )

    mock_data = {
        "nome_cliente": None,
        "endereco_entrega": None,
        "itens": itens,
        "forma_pagamento": "A definir",
        "duvida_ou_incompleto": False,
        "mensagem_resposta": mensagem_whatsapp
    }
    return json.dumps(mock_data, ensure_ascii=False)


def chamar_gemini(texto_mensagem: str) -> str:
    """Processa o pedido via API Gemini ou via Engine Local do Hermes em caso de falha."""
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