import os
import json
import re
import time
import difflib
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

CATALOGO_PRODUTOS = [
    "Arroz", "Feijão", "Feijão macassar", "Feijão preto", 
    "Macarrão", "Cuscuz", "Queijo", "Queijo coalho", "Presunto", "Leite", 
    "Coca-Cola", "Guaraná", "Miojo galinha caipira", "Detergente",
    "Carne", "Frango", "Refrigerante", "Cerveja"
]

SYSTEM_INSTRUCTION = """
Você é o Hermes, um assistente virtual inteligente para um supermercado.
Sua missão é manter e atualizar a lista de compras em conversas de delivery no WhatsApp.

REGRAS DE ATUALIZAÇÃO E EXTRAÇÃO:
1. GERENCIAMENTO DE ESTADO: O usuário enviará a mensagem atual acompanhada do contexto dos "itens_atuais" da lista.
   - Se o usuário disser "mudar o item 1 para 3kg de arroz" ou "trocar o 1...", substitua o item no índice 1 por 3kg de arroz na lista final.
   - Se o usuário pedir para remover (ex: "remover o item 2" ou "tirar o feijão"), remova o item da lista.
   - Se o usuário pedir novos itens (ex: "adicione 2kg de açúcar"), acrescente à lista existente.
   - Se o item já existir e o usuário pedir mais quantidade sem especificar substituição, some/atualize a quantidade.

2. CORREÇÃO MALEÁVEL / CONTEXTUAL: Corrija automaticamente erros de digitação nos nomes dos produtos (Ex: "feijo" -> "Feijão", "arros" -> "Arroz", "miojo galinha caipiria" -> "Miojo galinha caipira").
3. ISOLAMENTO DE MARCA: NUNCA inclua saudações, intenções ou termos como "da marca X" no nome do produto.
4. NORMALIZAÇÃO DE UNIDADES:
   - '2k', '2kg', '2 kilos', '2 kg' -> quantidade: 2.0, unidade_medida: 'kg'
   - '10 reais' -> quantidade: 10.0, unidade_medida: 'reais'
   - '2 pacotes', '2 pct' -> quantidade: 2.0, unidade_medida: 'pct'
   - '2 fardos' -> quantidade: 2.0, unidade_medida: 'fardo'
   - '2 unidades', '2 un' -> quantidade: 2.0, unidade_medida: 'un'

5. MENSAGEM AO CLIENTE: Retorne a lista resultante NUMERADA (1, 2, 3...) na mensagem_resposta.

SAÍDA OBRIGATÓRIA (JSON):
{
  "nome_cliente": null,
  "endereco_entrega": null,
  "itens": [
    {
      "produto": "Nome Corrigido",
      "marca_preferida": null,
      "quantidade": 1.0,
      "unidade_medida": "un",
      "categoria": "Mercearia",
      "aceita_substituicao": true,
      "observacao": ""
    }
  ],
  "forma_pagamento": "A definir",
  "duvida_ou_incompleto": false,
  "mensagem_resposta": "Mensagem formatada com itens numerados para o cliente"
}
"""

def corrigir_produto_fuzzy(termo_digitado: str) -> str:
    termo_clean = termo_digitado.strip().capitalize()
    correspondencias = difflib.get_close_matches(termo_clean, CATALOGO_PRODUTOS, n=1, cutoff=0.55)
    return correspondencias[0] if correspondencias else termo_clean


def extrair_itens_inteligente(texto: str, itens_existentes: list = None) -> list:
    if itens_existentes is None:
        itens_existentes = []

    lista_resultado = [dict(item) for item in itens_existentes]
    texto_processado = re.sub(r'(\d+(?:[\.,]\d+)?)\s*(?:kg|kilos|kilo|k)\b', r'\1 kg', texto, flags=re.IGNORECASE)

    # Detecta comando de troca/substituição por índice (Ex: "mudar o item 1 para 3kg de arroz")
    match_troca = re.search(r'(?:trocar|mudar|alterar)\s+(?:o\s+)?(?:item\s+)?(\d+)\s+(?:para|por)?\s*(.*)', texto_processado, re.IGNORECASE)
    
    if match_troca and lista_resultado:
        idx_alvo = int(match_troca.group(1)) - 1
        conteudo_novo = match_troca.group(2).strip()

        if 0 <= idx_alvo < len(lista_resultado) and conteudo_novo:
            qtd_m = re.search(r'(\d+(?:[\.,]\d+)?)', conteudo_novo)
            qtd = float(qtd_m.group(1).replace(',', '.')) if qtd_m else 1.0
            
            unid_m = re.search(r'\b(kg|g|reais|fardos|fardo|pacotes|pct|caixas|cx|unidades|un)\b', conteudo_novo, re.IGNORECASE)
            unid = unid_m.group(1).lower() if unid_m else "un"
            if unid in ["kilos", "kilo", "k"]: unid = "kg"
            if unid in ["pacotes", "pacote"]: unid = "pct"

            prod_nome = re.sub(r'^\d+(?:[\.,]\d+)?\s*(?:kg|g|reais|fardos|fardo|pct|un)?\s*(?:de)?\s*', '', conteudo_novo, flags=re.IGNORECASE).strip()
            prod_nome = corrigir_produto_fuzzy(prod_nome) if prod_nome else lista_resultado[idx_alvo]["produto"]

            lista_resultado[idx_alvo] = {
                "produto": prod_nome,
                "marca_preferida": lista_resultado[idx_alvo].get("marca_preferida"),
                "quantidade": qtd,
                "unidade_medida": unid,
                "categoria": lista_resultado[idx_alvo].get("categoria", "Mercearia"),
                "aceita_substituicao": True,
                "observacao": ""
            }
            return lista_resultado

    # Se não for comando de troca direta, processa extração padrão
    linhas_brutas = texto_processado.split("\n")
    clausulas = []
    for linha in linhas_brutas:
        if not linha.strip(): continue
        partes = re.split(r'[,;]|\salém de\s|\se também\s|\se ainda\s|\se\s', linha, flags=re.IGNORECASE)
        clausulas.extend([p.strip() for p in partes if p.strip()])

    depara_unidades = {"kg": "kg", "g": "g", "reais": "reais", "fardos": "fardo", "fardo": "fardo", "pacotes": "pct", "pct": "pct", "unidades": "un", "un": "un"}

    for trecho in clausulas:
        trecho_limpo = re.sub(r'^(?:bom dia|boa tarde|boa noite|eu gostaria de|gostaria de|gostaria|quero|por favor)?\s*', '', trecho, flags=re.IGNORECASE).strip()
        qtd_match = re.search(r'(\d+(?:[\.,]\d+)?)', trecho_limpo)
        if not qtd_match: continue
        
        qtd = float(qtd_match.group(1).replace(',', '.'))
        unid_match = re.search(r'\b(kg|g|reais|real|fardos|fardo|pacotes|pct|unidades|un)\b', trecho_limpo.lower())
        unid_encontrada = depara_unidades.get(unid_match.group(1), "un") if unid_match else "un"

        nome_prod = re.sub(r'^\d+(?:[\.,]\d+)?\s*(?:kg|g|reais|fardos|fardo|pct|un)?\s*(?:de)?\s*', '', trecho_limpo, flags=re.IGNORECASE).strip()
        nome_prod = re.sub(r'^(?:de|da|do)\s+', '', nome_prod, flags=re.IGNORECASE).strip()
        nome_prod = corrigir_produto_fuzzy(nome_prod) if nome_prod else ""

        if not nome_prod: continue

        # Atualiza se já existe ou adiciona novo
        idx_existente = next((i for i, item in enumerate(lista_resultado) if item["produto"].lower() == nome_prod.lower()), -1)
        novo_obj = {
            "produto": nome_prod,
            "marca_preferida": None,
            "quantidade": qtd,
            "unidade_medida": unid_encontrada,
            "categoria": "Mercearia",
            "aceita_substituicao": True,
            "observacao": ""
        }
        if idx_existente != -1:
            lista_resultado[idx_existente] = novo_obj
        else:
            lista_resultado.append(novo_obj)

    return lista_resultado


def gerar_resposta_local(texto_mensagem: str, itens_existentes: list = None) -> str:
    itens = extrair_itens_inteligente(texto_mensagem, itens_existentes)
    
    lista_formatada = "\n".join([
        f"{idx + 1}. {item['quantidade']} {item['unidade_medida']} de {item['produto']}" 
        for idx, item in enumerate(itens)
    ])

    mensagem_whatsapp = (
        f"Olá! Aqui está a sua lista atualizada:\n\n"
        f"{lista_formatada}\n\n"
        f"1️⃣ Está tudo certinho com a sua lista ou gostaria de alterar algo?\n"
        f"2️⃣ Qual será a forma de pagamento?"
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


def chamar_gemini(texto_mensagem: str, itens_existentes: list = None) -> str:
    if itens_existentes is None:
        itens_existentes = []

    if not client:
        return gerar_resposta_local(texto_mensagem, itens_existentes)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json"
    )
    
    prompt = f"""
    Lista de itens atuais do cliente no carrinho:
    {json.dumps(itens_existentes, ensure_ascii=False)}

    Nova mensagem do cliente:
    "{texto_mensagem}"

    Atualize a lista de compras de acordo com o pedido do cliente e retorne a lista final completa no JSON.
    """

    modelo_ativo = "gemini-3.8-flash"
    max_tentativas = 3
    tempo_espera = 1.5

    for tentativa in range(1, max_tentativas + 1):
        try:
            response = client.models.generate_content(
                model=modelo_ativo,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            erro_str = str(e)
            if "503" in erro_str or "UNAVAILABLE" in erro_str:
                if tentativa < max_tentativas:
                    time.sleep(tempo_espera)
                    tempo_espera *= 1.5
                    continue
            break

    return gerar_resposta_local(texto_mensagem, itens_existentes)