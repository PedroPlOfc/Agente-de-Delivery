# 🛒 Agente de IA para Delivery — Varejo e Supermercados

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-8E44AD?logo=googlegemini&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)

API desenvolvida em Python com **FastAPI** e **Google Gemini API** que interpreta pedidos de compras em linguagem natural enviados por clientes e os converte em uma lista estruturada, categorizada e pronta para a equipe de logística/pickers de supermercados.

---

## 🎯 Problema vs. Solução

* **Problema:** Clientes enviam listas de compras em texto livre por mensagens de voz ou texto sem padrão (ex: *"10 reais de queijo"*, *"meio quilo de carne moída"*, *"fubá coringa"*). A triagem manual desse pedido é demorada, suscetível a erros e atrasa a separação nos corredores do mercado.
* **Solução:** O agente de IA processa o texto, identifica marcas, quantidades, converte frações/valores monetários, categoriza os itens por setor do mercado (Açougue, Hortifruti, Mercearia, Laticínios, etc.) e sinaliza dúvidas/ambiguidades para confirmação rápida com o cliente.

---

## 🏗️ Arquitetura do Fluxo

```text
  [ Cliente ] 
      │ (Texto em linguagem natural via WhatsApp/Chat)
      ▼
┌────────────────────────────────────────────────────────┐
│ FastAPI Webhook (/webhook/mercado)                     │
│  ├─ Validação de Entrada (Pydantic)                    │
│  ├─ Chamada Resiliente ao Gemini API (Tenacity Retry)  │
│  └─ Enforcement de Schema Estruturado (TypedDict)      │
└────────────────────────────────────────────────────────┘
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ Resposta Estruturada (JSON Validado)                   │
│  ├─ Itens divididos por Setor / Categoria              │
│  ├─ Quantidades, Unidades e Marcas Preferidas          │
│  └─ Flag de Ambiguidade + Mensagem de Resposta         │
└────────────────────────────────────────────────────────┘
      │
      ▼
  [ Equipe de Separação / ERP / CRM ]

🚀 Tecnologias Utilizadas
Python 3.10+: Linguagem de programação principal utilizada no desenvolvimento.

FastAPI: Framework web assíncrono moderno e de alta performance para a criação da API HTTP.

Uvicorn: Servidor ASGI de alta velocidade para execução da aplicação FastAPI.

Google Generative AI SDK (google-generativeai): Biblioteca oficial do Google para integração com os modelos LLM do Gemini (models/gemini-3.8-flash / models/gemini-flash-lite-latest).

Pydantic: Biblioteca para validação de dados, tipagem estática e parsing automático dos esquemas JSON de entrada e saída.

Tenacity: Mecanismo de Exponential Backoff & Retry para garantir resiliência contra falhas temporárias de rede e limites de taxa (Rate Limit 429/503).

python-dotenv: Gerenciamento seguro de credenciais e variáveis de ambiente através de arquivos .env.

📦 Como Instalar e Rodar o Projeto
1. Clonar o repositório
git clone [https://github.com/PedroPlOfc/Agente-de-Delivery.git](https://github.com/PedroPlOfc/Agente-de-Delivery.git)
cd "Agente-de-Ia-para-Delivery"

2. Instalar as dependências
Bash
pip install -r requirements.txt

3. Executar o Servidor
Bash
python -m uvicorn main:app --reload

🧪 Como Testar no Swagger (Documentação Interativa)
Assim que o servidor estiver rodando, abra o seu navegador e acesse a documentação interativa automática fornecida pelo FastAPI:

👉 http://localhost:8000/docs

Passo a passo para testar a API:
Na interface do Swagger UI, localize e expanda a rota POST /webhook/mercado.

Clique no botão "Try it out" localizado no canto superior direito do bloco do endpoint.

No campo de texto Request body, insira um JSON contendo uma mensagem de compra em linguagem natural, conforme o exemplo abaixo:

JSON
{
  "telefone": "+5581995270425",
  "mensagem": "Bom dia! Gostaria de pedir 3 pacotes de Fubá Coringa de 1kg, 10 reais de queijo coalho, 8 reais de mortadela, 2kg de macarrão espaguete e 1kg de arroz parboilizado."
}
Clique no botão azul "Execute" para disparar a requisição para o agente de IA.

📤 Exemplo de Resposta Retornada pela API (200 OK):
JSON
{
  "status": "sucesso",
  "cliente": "+5581995270425",
  "lista_separacao": {
    "nome_cliente": null,
    "endereco_entrega": null,
    "itens": [
      {
        "produto": "Fubá",
        "marca_preferida": "Coringa",
        "quantidade": 3,
        "unidade_medida": "kg",
        "categoria": "Mercearia",
        "aceita_substituicao": true,
        "observacao": null
      },
      {
        "produto": "Queijo coalho",
        "marca_preferida": null,
        "quantidade": 10,
        "unidade_medida": "reais",
        "categoria": "Laticínios",
        "aceita_substituicao": true,
        "observacao": null
      },
      {
        "produto": "Mortadela",
        "marca_preferida": null,
        "quantidade": 8,
        "unidade_medida": "reais",
        "categoria": "Açougue",
        "aceita_substituicao": true,
        "observacao": null
      },
      {
        "produto": "Macarrão",
        "marca_preferida": null,
        "quantidade": 2,
        "unidade_medida": "kg",
        "categoria": "Mercearia",
        "aceita_substituicao": true,
        "observacao": "Espaguete"
      },
      {
        "produto": "Arroz",
        "marca_preferida": null,
        "quantidade": 1,
        "unidade_medida": "kg",
        "categoria": "Mercearia",
        "aceita_substituicao": true,
        "observacao": "Parboilizado"
      }
    ],
    "duvida_ou_incompleto": false,
    "mensagem_resposta": "Lista de compras recebida com sucesso! Separaremos seus itens agora mesmo."
  }
}
