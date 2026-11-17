---
date: 2026-11-17T19:06
tags:
  - Projetos
  - inteligênciaArtificial
  - agente
cssclasses:
  - code
---

# 🛠️ Arquitetura e Stack Técnica — Cana

O **Cana** é estruturado em camadas desacopladas que combinam desenvolvimento backend assíncrono, inteligência artificial generativa com saídas estruturadas, persistência relacional e mensageria via containers.

## 1. Linguagens de Programação, Marcação e Dados

- **Python (3.10+):** Linguagem principal do projeto. Controla o servidor web, a orquestração dos modelos de IA, as regras de negócio, a persistência no banco de dados e o motor local de contingência (`main.py`, `app/config.py`, `app/services.py`, `listar_modelos.py`).

- **SQL (PostgreSQL):** Empregado no script `init_db.sql` e nas operações internas do backend para criação de esquemas (`CREATE TABLE`), carga inicial do catálogo de produtos (`INSERT`), consulta de preços, atualização da sacola e manutenção de registros.

- **HTML5, CSS3 e JavaScript (Vanilla JS):** Compõem a interface web de testes (`index.html`), responsáveis pelo layout responsivo, envio assíncrono das mensagens (`fetch` para `POST /webhook/mercado`) e renderização dinâmica da _Sacola de Compras_.

- **YAML:** Utilizado no `docker-compose.yml` para declarar e orquestrar os serviços, redes internas, mapeamento de portas e volumes persistentes dos containers.

## 2. Backend, API e Bibliotecas Python

- **FastAPI:** Framework web assíncrono de alta performance que expõe os endpoints da aplicação (como `/webhook/mercado` e `/qrcode`), gerencia políticas de **CORS** e serve os arquivos estáticos do frontend.

- **Uvicorn:** Servidor ASGI responsável por executar a aplicação FastAPI em ambiente local ou de produção.

- **Pydantic (v2):** Biblioteca de validação e tipagem utilizada para definir os esquemas de **Structured Outputs**, garantindo que a IA retorne cada item do pedido com campos padronizados (nome, quantidade, unidade de medida, marca e departamento).

- **python-dotenv:** Carrega as variáveis de ambiente e configurações locais do arquivo `.env` para dentro da aplicação (`app/config.py`).

- **Expressões Regulares (`re`):** Núcleo do **motor local determinístico** em Python puro, capaz de extrair produtos e quantidades por padrões textuais caso todas as APIs externas de IA estejam indisponíveis.


## 3. Inteligência Artificial e Cadeia de Resiliência (Fallback)

- **Google Gemini API (`google-genai` SDK):** Motor cognitivo principal do agente:
    
    - **Modelo Principal (`gemini-3.6-flash`):** Interpreta mensagens informais, converte unidades cotidianas (ex.: _"meio quilo"_ para `0.50 kg`, _"1 dúzia"_ para `12 un`), separa preferências de marca e classifica itens por setor.
    
    - **Modelo Reserva (`gemini-3.5-flash`):** Acionado automaticamente caso o modelo principal apresente instabilidade (`503 Service Unavailable`) ou exceda o tempo limite (`504 Gateway Timeout`).
    
    - **Automatic Function Calling (AFC):** Mecanismo ativado (com limite de chamadas remotas por turno) que permite ao Gemini consultar o PostgreSQL durante o raciocínio para validar produtos e preços.
    
- **LangChain (`langchain-google-genai`):** Camada de orquestração (`ChatGoogleGenerativeAI`) que controla _timeouts_ (`45s`), retentativas (`max_retries`) e o encadeamento entre o modelo principal e as camadas reservas.

- **OpenAI API (`openai` + `httpx`):** Segunda camada de reserva externa, acionada automaticamente caso os modelos do Google fiquem temporariamente indisponíveis.

- **HTTPX:** Cliente HTTP assíncrono utilizado pelos SDKs de IA para realizar requisições REST de baixa latência.


## 4. Banco de Dados e Cache

- **PostgreSQL (Container `evolution_postgres`):** Banco de dados relacional central que hospeda dois conjuntos de tabelas isolados logicamente no mesmo banco:
    
    - **Tabelas da Evolution API:** Gerenciadas automaticamente via migrations (`Chat`, `Contact`, `EvolutionBot`, `_prisma_migrations`) para controle das sessões e instâncias do WhatsApp.
    
    - **Tabelas do Cana (`init_db.sql`):** Armazenam o catálogo de itens do mercado, preços e o estado persistente da sacola de compras de cada cliente ao longo da conversa.
    
- **psycopg2 (`psycopg2-binary`):** Driver de conexão Python–PostgreSQL que executa as consultas SQL a partir da string de conexão `DATABASE_URL`.

- **Redis:** Banco de dados em memória executado em container Docker, utilizado pela Evolution API para cache rápido, filas de mensagens e controle de estado das conexões.


## 5. Mensageria e Infraestrutura

- **Evolution API (v2.1.0):** Gateway de integração com o WhatsApp rodando em container Docker. Gera o QR Code de pareamento, recebe as mensagens enviadas pelos clientes no WhatsApp e dispara os payloads JSON para o webhook do FastAPI.

- **Docker & Docker Compose:** Isolam e orquestram toda a stack de infraestrutura (`evolution-api`, `evolution_postgres` e `redis`) com persistência de dados em volumes locais.


## 6. Interface Web e Funcionalidades Visuais (`index.html`)

- **Simulador de Chat:** Emula o fluxo de conversa do WhatsApp conectado diretamente ao backend FastAPI, permitindo validar cenários completos sem depender de um aparelho pareado.

- **Sacola de Compras em Tempo Real:** Painel lateral sincronizado com o banco de dados a cada turno, exibindo quantidades normalizadas (`kg`, `g`, `un`, `pct`), tags de marca, etiquetas de setor (_Hortifruti_, _Mercearia_, _Laticínios_, _Bebidas_, _Açougue_, _Outros_) e o status atualizado da forma de pagamento.


## 7. Ferramentas de Desenvolvimento e Diagnóstico

- **Ambiente Virtual Python (`venv`) + PowerShell:** Isolamento de dependências e automação de comandos de execução no ambiente local.

- **Git & GitHub:** Controle de versão do código-fonte com `.gitignore` configurado para proteger arquivos sensíveis (`.env`) e o ambiente virtual.

- **Utilitário de Diagnóstico (`listar_modelos.py`):** Script auxiliar em Python para consultar e filtrar quais modelos da API do Google estão ativos e disponíveis na chave configurada.