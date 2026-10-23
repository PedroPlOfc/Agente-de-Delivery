## 📁 `app/schemas.py` — _Contratos e Tipagem (Pydantic)_

Define a estrutura exata de dados do pedido:
- **`ItemMercado`**: Modelo de item individual (produto, quantidade, unidade de medida, marca preferida, categoria).
    
- **`ListaSeparacaoMercado`**: Contrato principal retornado pela IA, agrupando a sacola do cliente, endereço de entrega, forma de pagamento e a mensagem de resposta.
    
- **`MensagemEntrada`**: Modelo do payload recebido via webhook (`telefone`, `mensagem` e `itens_atuais`).
## ### 📁 `app/repositories/` — _Camada de Dados (Repository Pattern)_

Decoupla a origem dos dados da aplicação, permitindo transição transparente entre o banco local e o ERP da loja:
- **`base.py` (`AbstractProductRepository`)**: Classe abstrata/interface que define o contrato obrigatório (`buscar_por_nome`, `buscar_por_codigo_barras`, `verificar_estoque`).
    
- **`postgres_mock.py` (`PostgresMockRepository`)**: Implementação conectada ao PostgreSQL local via `psycopg2`, realizando consultas com `ILIKE` em produtos, categorias e saldos de estoque.
    
- **`syspdv_api.py` (`SysPDVApiRepository`)**: Estrutura preparada para consumir a API REST do ERP SysPDV em produção sem alterar as regras de IA.
    
- **`factory.py` (`get_product_repository`)**: Fábrica de injeção de dependência que chaveia o repositório ativo baseado na variável `DATA_SOURCE_PROVIDER` do `.env`.
## 📁 `app/services.py` — _O Motor de Inteligência & Persistência (Cana)_

Responsável por interpretar a mensagem do cliente, consultar o banco e formatar a sacola:
- **Prompt do Cana**: Instrução do sistema configurada para a persona verde e sustentável, reforçando com amabilidade a entrega em sacolas retornáveis.
    
- **`consultar_produto_banco()` / `corrigir_produto_fuzzy()`**: Consulta os produtos primeiro na tabela do banco relacional ativado via Repository Pattern e, como fallback, recorre ao catálogo local.
    
- **`chamar_gemini()`**: Processa a mensagem via LangChain (`gemini-3.8-flash` com fallbacks para `gemini-1.5-flash` ou `gpt-4o-mini`).
    
- **`fallback_local_adaptado()`**: Engine local baseada em Regex para garantir disponibilidade total caso a API de IA fique indisponível.
## 📁 `main.py` — _O Servidor FastAPI_
Servidor HTTP e manipulador de webhooks:
- **`@app.get("/")`**: Servidor da interface web (`templates/index.html`).
    
- **`@app.post("/webhook/mercado")`**: Endpoint consumido pela interface do simulador web.
    
- **`@app.post("/webhook/whatsapp")`**: Webhook assíncrono (usando `BackgroundTasks`) integrado à Evolution API para responder aos clientes do WhatsApp.
### 📁 `templates/index.html` — _Painel de Atendimento (Frontend)_
Interface com estética **Eco-Friendly** em verde (`emerald`):

- **Simulador de WhatsApp**: Chat com a identidade do **Cana** e informações de contato do cliente.
    
- **Painel Lateral da Sacola**: Renderização em tempo real dos itens extraídos, marcas preferidas, unidades e categorias puxadas do banco de dados.
## 📁 `app/whatsapp.py` — _A Integração de Envio Externo_
Contém a função auxiliar para realizar chamadas HTTP (`requests.post`) para a API do WhatsApp/Evolution, enviando o texto contido em `mensagem_resposta` diretamente para o celular do cliente.
## 📁 `.env` & `requirements.txt` — _Configurações e Dependências_
- **`.env`**: Guarda a chave de API do Google (`GEMINI_API_KEY`) com segurança sem expor credenciais no código do GitHub.
    
- **`requirements.txt`**: Lista os pacotes Python essenciais para rodar o projeto (`fastapi`, `uvicorn`, `google-genai`, `pydantic`, `tenacity`, `python-dotenv`).
## 📁 `init_db.sql` & `docker-compose.yml` — _Infraestrutura de Banco_
- **`docker-compose.yml`**: Configura o container PostgreSQL 15 (`evolution_postgres`).
    
- **`init_db.sql`**: Script DDL/DML que cria a estrutura relacional (`categorias`, `produtos`, `estoque`, `pedidos`, `itens_pedido`) e insere os dados de teste do Sacolão da Economia.