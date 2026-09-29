import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import GEMINI_API_KEY
from app.schemas import ListaSeparacaoMercadoSchema

# Configura a chave global do Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

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

model = genai.GenerativeModel(
    model_name="models/gemini-3.8-flash",
    system_instruction=SYSTEM_PROMPT_MERCADO,
)

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=6),
    reraise=True
)
def chamar_gemini(mensagem: str) -> str:
    response = model.generate_content(
        mensagem,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ListaSeparacaoMercadoSchema,
            temperature=0.1,
        ),
    )
    return response.text