import os
import json
import re
import difflib
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.schemas import ListaSeparacaoMercado

load_dotenv()

# --- CATALOGO DE PRODUTOS PARA FALLBACK LOCAL ---
CATALOGO_PRODUTOS = [
    "Arroz", "Feijão", "Feijão macassar", "Feijão preto", 
    "Macarrão", "Cuscuz", "Queijo", "Queijo coalho", "Presunto", "Leite", 
    "Coca-Cola", "Guaraná", "Miojo galinha caipira", "Detergente",
    "Carne", "Frango", "Refrigerante", "Cerveja"
]

SYSTEM_INSTRUCTION = """
...
4. MENSAGEM DE RESPOSTA AO CLIENTE:
   - Retorne uma mensagem amigável no campo `mensagem_resposta`.
   - A lista de itens DEVE obrigatoriamente ser formatada com quebras de linha (\\n) entre cada item numerado, para que apareça em tópicos verticais.
   
Exemplo do formato desejado em mensagem_resposta:
Bom dia! Adicionei os seguintes itens ao seu carrinho:

1. Arroz (2 kg)
2. Feijão (2 kg)
3. Macarrão (2 pacotes)
4. Queijo coalho (R$ 10,00)
5. Coca-Cola (2 fardos)

Deseja adicionar mais algum produto ou podemos prosseguir para a entrega?
...
"""

def inicializar_modelo_langchain():
    """Configura o Gemini como principal e a OpenAI como 2ª opção (fallback)."""
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not gemini_key:
        print("⚠️ GEMINI_API_KEY não encontrada. O sistema usará o motor local.")
        return None

    # 1ª Opção: Gemini 2.5 Flash
    model_primary = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        google_api_key=gemini_key,
        temperature=0.1,
        max_retries=2
    ).with_structured_output(ListaSeparacaoMercado)

    fallbacks = []

    # 2ª Opção (Fallback Primário): OpenAI GPT-4o-mini
    if openai_key:
        model_openai = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_key,
            temperature=0.1,
            max_retries=2
        ).with_structured_output(ListaSeparacaoMercado)
        fallbacks.append(model_openai)

    # 3ª Opção (Fallback Secundário): Gemini 1.5 Flash
    model_gemini_15 = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=gemini_key,
        temperature=0.1,
        max_retries=2
    ).with_structured_output(ListaSeparacaoMercado)
    fallbacks.append(model_gemini_15)

    return model_primary.with_fallbacks(fallbacks)


# Inicializa a chain
chain_llm = inicializar_modelo_langchain()

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_INSTRUCTION),
    ("user", """
ESTADO ATUAL DO CARRINHO DO CLIENTE:
{itens_existentes}

MENSAGEM RECEBIDA DO CLIENTE:
"{texto_mensagem}"

Processe a intenção do cliente, atualize o carrinho e retorne o objeto final completo.
""")
])


# --- FUNÇÕES AUXILIARES DE FALLBACK LOCAL ---

def corrigir_produto_fuzzy(termo_digitado: str) -> str:
    termo_clean = termo_digitado.strip().capitalize()
    correspondencias = difflib.get_close_matches(termo_clean, CATALOGO_PRODUTOS, n=1, cutoff=0.55)
    return correspondencias[0] if correspondencias else termo_clean

def formatar_quantidade(valor: float):
    return int(valor) if valor.is_integer() else valor

def extrair_itens_inteligente(texto: str, itens_existentes: list = None) -> list:
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


# --- FUNÇÃO IMPORTADA PELO MAIN.PY ---

def chamar_gemini(texto_mensagem: str, itens_existentes: list = None) -> str:
    """Função invocada pela rota da FastAPI (main.py)."""
    if itens_existentes is None:
        itens_existentes = []

    if not chain_llm:
        return fallback_local_adaptado(texto_mensagem, itens_existentes)

    try:
        messages = prompt_template.format_messages(
            itens_existentes=json.dumps(itens_existentes, ensure_ascii=False),
            texto_mensagem=texto_mensagem
        )
        
        resultado_pydantic: ListaSeparacaoMercado = chain_llm.invoke(messages)
        
        # --- REFORMATANDO A MENSAGEM DE RESPOSTA COM QUEBRAS DE LINHA (VERTICAL) ---
        if resultado_pydantic.itens:
            linhas_itens = []
            for idx, item in enumerate(resultado_pydantic.itens, start=1):
                unid = f" {item.unidade_medida}" if item.unidade_medida else ""
                linhas_itens.append(f"{idx}. {item.produto} ({formatar_quantidade(item.quantidade)}{unid})")
            
            lista_vertical = "\n".join(linhas_itens)
            
            resultado_pydantic.mensagem_resposta = (
                f"Bom dia! Aqui está a sua lista atualizada:\n\n"
                f"{lista_vertical}\n\n"
                f"Deseja adicionar mais algum produto ou podemos prosseguir para a entrega?"
            )

        return resultado_pydantic.model_dump_json(by_alias=True)

    except Exception as e:
        print(f"⚠️ Erro ao processar via LangChain ({e}). Executando motor de fallback local...")
        return fallback_local_adaptado(texto_mensagem, itens_existentes)