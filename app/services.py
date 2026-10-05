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

# Modelo primário e secundários para cascata de resiliência
MODELO_PRIMARIO = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MODELOS_CASCATA = [MODELO_PRIMARIO, "gemini-2.0-flash", "gemini-1.5-flash"]

client = genai.Client(api_key=API_KEY) if API_KEY else None

CATALOGO_PRODUTOS = [
    "Arroz", "Feijão", "Feijão macassar", "Feijão preto", 
    "Macarrão", "Cuscuz", "Queijo", "Queijo coalho", "Presunto", "Leite", 
    "Coca-Cola", "Guaraná", "Miojo galinha caipira", "Detergente",
    "Carne", "Frango", "Refrigerante", "Cerveja"
]

SYSTEM_INSTRUCTION = """
Você é o Hermes, o assistente inteligente de delivery de um supermercado.
Sua única função é gerenciar e atualizar a lista de compras (carrinho) do cliente a partir das mensagens enviadas.

SUAS DIRETRIZES DE RACIOCÍNIO ADAPTÁVEL:

1. MANIPULAÇÃO DO CARRINHO (ESTADO):
   - Você receberá a lista de itens atuais do carrinho e a nova mensagem do cliente.
   - ADICIONAR: Acrescente novos produtos mantendo os anteriores intactos na lista.
   - SUBSTITUIR/EDITAR (POR ÍNDICE OU NOME): Se o cliente disser "mudar o item 1 para 3kg de arroz" ou "trocar o 2 por feijão preto", atualize diretamente aquele item no carrinho.
   - REMOVER (POR ÍNDICE OU NOME): Se o cliente disser "remover o item 7", "tirar o 7" ou "apagar o guaraná", REMOVA o item correspondente da lista final. NUNCA crie produtos contendo palavras como "remover" ou "tirar".

2. REGRAS DE MARCA PREFERIDA:
   - Defina `marca_preferida` APENAS quando o cliente especificar uma marca para um produto genérico (Ex: produto: "Miojo galinha caipira", marca_preferida: "Vitarella").
   - NUNCA repita o nome do produto na marca se o produto já for o próprio nome comercial/marca (Ex: produto: "Coca-Cola" -> marca_preferida: null; produto: "Nutella" -> marca_preferida: null).

3. CORREÇÃO ORTOGRÁFICA E NORMALIZAÇÃO:
   - Corrija automaticamente gírias, erros de digitação e termos incompletos (Ex: "feijo" -> "Feijão", "arros" -> "Arroz", "macarao" -> "Macarrão", "2k" -> 2kg).
   - Limpe o nome do produto retirando saudações, quantidades, unidades e verbos ("gostaria de", "2kg de").
   - Quantidades inteiras devem ser salvas como inteiros (Ex: 3 e não 3.0).

4. MENSAGEM DE RESPOSTA AO CLIENTE:
   - Retorne uma mensagem amigável no campo `mensagem_resposta` contendo a lista resultante devidamente NUMERADA (1., 2., 3...).

SAÍDA OBRIGATÓRIA (JSON PURO):
{
  "nome_cliente": null,
  "endereco_entrega": null,
  "itens": [
    {
      "produto": "Nome do Produto Corrigido",
      "marca_preferida": null,
      "quantidade": 1,
      "unidade_medida": "un",
      "categoria": "Mercearia",
      "aceita_substituicao": true,
      "observacao": ""
    }
  ],
  "forma_pagamento": "A definir",
  "duvida_ou_incompleto": false,
  "mensagem_resposta": "Mensagem formatada para o WhatsApp"
}
"""

def limpar_resposta_json(texto: str) -> str:
    """Remove marcações de código markdown caso o modelo retorne dentro de ```json ... ```."""
    texto_limpo = texto.strip()
    if texto_limpo.startswith("```"):
        texto_limpo = re.sub(r'^```(?:json)?\s*', '', texto_limpo, flags=re.IGNORECASE)
        texto_limpo = re.sub(r'\s*```$', '', texto_limpo)
    return texto_limpo.strip()

def corrigir_produto_fuzzy(termo_digitado: str) -> str:
    termo_clean = termo_digitado.strip().capitalize()
    correspondencias = difflib.get_close_matches(termo_clean, CATALOGO_PRODUTOS, n=1, cutoff=0.55)
    return correspondencias[0] if correspondencias else termo_clean

def formatar_quantidade(valor: float):
    return int(valor) if valor.is_integer() else valor

def extrair_itens_inteligente(texto: str, itens_existentes: list = None) -> list:
    """Motor local resiliente (fallback)."""
    if itens_existentes is None:
        itens_existentes = []

    lista_resultado = [dict(item) for item in itens_existentes]
    texto_processado = re.sub(r'(\d+(?:[\.,]\d+)?)\s*(?:kg|kilos|kilo|k)\b', r'\1 kg', texto, flags=re.IGNORECASE)

    # 1. Remoção por Índice
    match_remocao_idx = re.search(r'(?:remover|tirar|deletar|excluir|cancelar|apagar)\s+(?:o\s+)?(?:item\s+)?(\d+)', texto_processado, re.IGNORECASE)
    if match_remocao_idx and lista_resultado:
        idx_remover = int(match_remocao_idx.group(1)) - 1
        if 0 <= idx_remover < len(lista_resultado):
            lista_resultado.pop(idx_remover)
            return lista_resultado

    # 2. Troca por Índice
    match_troca = re.search(r'(?:trocar|mudar|alterar)\s+(?:o\s+)?(?:item\s+)?(\d+)\s+(?:para|por)?\s*(.*)', texto_processado, re.IGNORECASE)
    if match_troca and lista_resultado:
        idx_alvo = int(match_troca.group(1)) - 1
        conteudo_novo = match_troca.group(2).strip()

        if 0 <= idx_alvo < len(lista_resultado) and conteudo_novo:
            qtd_m = re.search(r'(\d+(?:[\.,]\d+)?)', conteudo_novo)
            qtd = formatar_quantidade(float(qtd_m.group(1).replace(',', '.'))) if qtd_m else 1
            
            unid_m = re.search(r'\b(kg|g|reais|fardos|fardo|pacotes|pct|caixas|cx|unidades|un)\b', conteudo_novo, re.IGNORECASE)
            unid = unid_m.group(1).lower() if unid_m else "un"
            if unid in ["kilos", "kilo", "k"]: unid = "kg"
            if unid in ["pacotes", "pacote"]: unid = "pct"

            prod_nome = re.sub(r'^\d+(?:[\.,]\d+)?\s*(?:kg|g|reais|fardos|fardo|pct|un)?\s*(?:de)?\s*', '', conteudo_novo, flags=re.IGNORECASE).strip()
            prod_nome = re.sub(r'^(?:também|adicionar|acrescentar|de)\s+', '', prod_nome, flags=re.IGNORECASE).strip()
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

    # 3. Extração padrão de novos itens
    linhas_brutas = texto_processado.split("\n")
    clausulas = []
    for linha in linhas_brutas:
        if not linha.strip(): continue
        partes = re.split(r'[,;]|\salém de\s|\se também\s|\se ainda\s|\se\s', linha, flags=re.IGNORECASE)
        clausulas.extend([p.strip() for p in partes if p.strip()])

    depara_unidades = {"kg": "kg", "g": "g", "reais": "reais", "fardos": "fardo", "fardo": "fardo", "pacotes": "pct", "pct": "pct", "unidades": "un", "un": "un"}

    for trecho in clausulas:
        if re.search(r'\b(remover|tirar|deletar|excluir|cancelar|apagar)\b', trecho, re.IGNORECASE): continue

        trecho_limpo = re.sub(r'^(?:bom dia|boa tarde|boa noite|eu gostaria de|gostaria de|gostaria também de|também de|adicionar|gostaria|quero|por favor)?\s*', '', trecho, flags=re.IGNORECASE).strip()
        qtd_match = re.search(r'(\d+(?:[\.,]\d+)?)', trecho_limpo)
        if not qtd_match: continue
        
        qtd = formatar_quantidade(float(qtd_match.group(1).replace(',', '.')))
        unid_match = re.search(r'\b(kg|g|reais|real|fardos|fardo|pacotes|pct|unidades|un)\b', trecho_limpo.lower())
        unid_encontrada = depara_unidades.get(unid_match.group(1), "un") if unid_match else "un"

        nome_prod = re.sub(r'^\d+(?:[\.,]\d+)?\s*(?:kg|g|reais|fardos|fardo|pct|un)?\s*(?:de)?\s*', '', trecho_limpo, flags=re.IGNORECASE).strip()
        nome_prod = re.sub(r'^(?:de|da|do|também de|adicionar)\s+', '', nome_prod, flags=re.IGNORECASE).strip()
        nome_prod = corrigir_produto_fuzzy(nome_prod) if nome_prod else ""

        if not nome_prod or len(nome_prod) < 2: continue

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

def fallback_local_adaptado(texto_mensagem: str, itens_existentes: list = None) -> str:
    """Executa o processamento inteligente localmente quando a API Gemini falhar."""
    itens = extrair_itens_inteligente(texto_mensagem, itens_existentes)
    
    lista_formatada = "\n".join([
        f"{idx + 1}. {formatar_quantidade(float(item['quantidade']))} {item['unidade_medida']} de {item['produto']}" 
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
        return fallback_local_adaptado(texto_mensagem, itens_existentes)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json"
    )
    
    prompt = f"""
    ESTADO ATUAL DO CARRINHO DO CLIENTE:
    {json.dumps(itens_existentes, ensure_ascii=False)}

    MENSAGEM RECEBIDA DO CLIENTE:
    "{texto_mensagem}"

    Processe a intenção do cliente, atualize o carrinho e retorne o JSON final completo.
    """

    # Tenta cascata de modelos com re-tentativas automáticas para erros 503/UNAVAILABLE
    for modelo in MODELOS_CASCATA:
        max_retries = 3
        backoff_sec = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=config
                )
                if response.text:
                    json_limpo = limpar_resposta_json(response.text)
                    json.loads(json_limpo)
                    return json_limpo
            except Exception as e:
                erro_msg = str(e)
                # Trata erros temporários de sobrecarga (503 / UNAVAILABLE)
                if "503" in erro_msg or "UNAVAILABLE" in erro_msg:
                    print(f"⚠️ Modelo {modelo} indisponível (503). Tentativa {attempt}/{max_retries} aguardando {backoff_sec}s...")
                    time.sleep(backoff_sec)
                    backoff_sec *= 2.0
                else:
                    print(f"⚠️ Erro no modelo {modelo}: {e}. Alternando modelo...")
                    break

    print("⚠️ Todos os modelos de IA falharam/estão indisponíveis. Executando via motor de fallback local...")
    return fallback_local_adaptado(texto_mensagem, itens_existentes)