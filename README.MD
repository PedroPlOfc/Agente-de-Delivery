# 🌿 Cana — Agente de IA para Delivery (Varejo & Supermercados)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-8E44AD?logo=googlegemini&logoColor=white)
![Evolution API](https://img.shields.io/badge/Evolution%20API-v2.1.0-0052CC?logo=whatsapp&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white)

O **Cana** é um agente de inteligência artificial desenvolvido em Python com **FastAPI**, **Google Gemini (`google-genai` / LangChain)**, **PostgreSQL** e **Evolution API v2.1.0**. O sistema recebe mensagens em linguagem natural enviadas via **WhatsApp** (ou pelo simulador web integrado), interpreta pedidos de supermercado em texto livre, gerencia a sacola de compras de forma persistente no banco de dados e conduz todo o fechamento da entrega de maneira automatizada.

---

## 🎯 Problema vs. Solução

- **Problema:** Clientes enviam pedidos sem padrão formal (ex: *"meio quilo de cebola roxa"*, *"1 dúzia de ovos"*, *"tira uma Coca e troca a banana por batata"*). A triagem manual gera gargalos no atendimento, erros na separação por setor e retrabalho para calcular valores e troco.
- **Solução:** O Cana intercepta as mensagens via webhook, consulta o catálogo no **PostgreSQL** via *Function Calling*, converte medidas e frações automaticamente, mantém o estado da sacola ao longo da conversa, extrai endereço e forma de pagamento e responde ao cliente com o resumo atualizado em tempo real.

---

## 🏗️ Arquitetura da Solução

```text
 ┌──────────────────────┐       ┌──────────────────────┐       ┌────────────────────────────────┐
 │ Cliente (WhatsApp)   │ ────> │ Evolution API v2.1.0 │ ────> │ FastAPI Backend                │
 │ ou Simulador Web     │       │ (Docker + Redis)     │       │ (POST /webhook/mercado)        │
 └──────────────────────┘       └──────────────────────┘       └────────────────────────────────┘
            ▲                                                                   │
            │                                                                   ▼
 ┌──────────────────────┐       ┌──────────────────────┐       ┌────────────────────────────────┐
 │ Resposta / Sacola    │ <──── │ PostgreSQL           │ <───> │ Camada de IA & Contingência    │
 │ Atualizada em Tempo  │       │ (Catálogo e Pedidos) │       │ Gemini -> Fallback -> Local    │
 └──────────────────────┘       └──────────────────────┘       └────────────────────────────────┘
```

---

## ✨ Principais Funcionalidades

- **Extração Estruturada (`Structured Outputs`):** Converte textos informais em objetos tipados com **Pydantic v2**, separando nome do produto, quantidade, unidade (`kg`, `g`, `un`, `pct`, `cx`), preferência de marca e observações de preparo.
- **Conversão Inteligente de Medidas:** Traduz expressões cotidianas como *"meio quilo"* (`0.5 kg`) ou *"1 dúzia"* (`12 un`) e categoriza cada item por departamento (*Hortifruti, Mercearia, Laticínios, Bebidas, Açougue*).
- **Memória Persistente da Sacola:** Armazena o carrinho no **PostgreSQL**, permitindo adicionar, remover, alterar quantidades ou substituir itens em mensagens subsequentes sem perder o histórico.
- **Fechamento Logístico Completo:** Extrai endereço de entrega, complementos, ponto de referência, forma de pagamento e calcula necessidade de troco.
- **Resiliência em Camadas (Multi-Fallback):** Opera com modelo principal do Google Gemini, fallback automático para um segundo modelo Gemini/OpenAI em caso de instabilidade (`503`/`504`) e motor local determinístico de contingência para garantir que o cliente nunca fique sem resposta.
- **Painel Web de Testes (`index.html`):** Interface visual de chat conectada ao backend que permite simular conversas e acompanhar a atualização da sacola de compras em tempo real sem depender de um chip ativo.

---

## 📁 Estrutura do Projeto

```text
├── app/
│   ├── config.py          # Carregamento de variáveis de ambiente, CORS e parâmetros dos modelos
│   └── services.py        # Lógica do agente Cana, prompts, tools do banco e cadeia de fallback
├── index.html             # Interface web de simulação de chat e visualização da sacola
├── main.py                # Servidor FastAPI, rotas de webhook, QR Code e servir arquivos estáticos
├── docker-compose.yml     # Orquestração da Evolution API v2.1.0, PostgreSQL e Redis
├── init_db.sql            # Script SQL de criação das tabelas e catálogo inicial de produtos
├── listar_modelos.py      # Utilitário para verificar modelos disponíveis na chave Gemini
├── requirements.txt       # Dependências Python do projeto
└── .env                   # Variáveis de ambiente locais (não versionado)
```

---

## 🚀 Como Rodar Localmente

### Pré-requisitos

- **Python 3.10+**
- **Docker** e **Docker Compose** (Docker Desktop no Windows/macOS)
- Chave de API do **Google AI Studio (Gemini)**

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/Agente-de-Delivery.git
cd Agente-de-Delivery
```

### 2. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com base no modelo abaixo e preencha com suas próprias credenciais:

```env
# Inteligência Artificial
GEMINI_API_KEY=sua_chave_api_gemini_aqui
GEMINI_MODEL=gemini-3.6-flash
GEMINI_FALLBACK_MODEL=gemini-3.5-flash

# Fallback Opcional (OpenAI)
OPENAI_API_KEY=sua_chave_api_openai_opcional

# Banco de Dados (PostgreSQL)
DATABASE_URL=postgresql://evolution:sua_senha_segura@localhost:5432/evolution

# Evolution API (WhatsApp)
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua_chave_global_evolution
INSTANCE_NAME=cana_delivery
```

> **Importante:** Certifique-se de que a senha definida em `DATABASE_URL` seja a mesma configurada no serviço `postgres` do seu `docker-compose.yml`.

### 3. Suba a infraestrutura Docker e inicialize o banco

Inicie os containers da Evolution API, PostgreSQL e Redis em segundo plano:

```bash
docker compose up -d
```

Aguarde alguns segundos até o PostgreSQL inicializar e aplique o script `init_db.sql` para criar as tabelas do catálogo e dos pedidos:

* **Linux / macOS:**
  ```bash
  cat init_db.sql | docker exec -i evolution_postgres psql -U evolution -d evolution
  ```
* **Windows (PowerShell):**
  ```powershell
  Get-Content .\init_db.sql -Raw -Encoding UTF8 | docker exec -i evolution_postgres psql -U evolution -d evolution
  ```

### 4. Instale as dependências Python e inicie o servidor

Crie e ative o ambiente virtual:

* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

Instale os pacotes e inicie a aplicação FastAPI:

```bash
pip install -r requirements.txt
python main.py
```

---

## 🧪 Testando o Agente

- **Pelo Simulador Web:** Acesse **`http://127.0.0.1:8000`** no navegador (ou abra o `index.html` via Live Server na porta `5500`) e envie uma lista de compras livre no chat para acompanhar a extração automática na sacola.
- **Pelo WhatsApp:** Acesse **`http://127.0.0.1:8000/qrcode`** (ou o painel da Evolution API em `http://localhost:8080`) para escanear o QR Code com o aparelho que receberá os pedidos.

---

## 🛠️ Comandos Úteis

- **Pausar os containers sem perder os dados:** `docker compose stop`
- **Retomar os containers já configurados:** `docker compose start`
- **Verificar modelos Gemini liberados na sua chave:** `python listar_modelos.py`