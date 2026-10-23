## 📍 Dia 1: Estruturação Inicial e Backend Base
- **Criação do Ponto de Entrada (`main.py`)**: Configuração do servidor web assíncrono com **FastAPI** e servidor **Uvicorn** rodando na porta `8000`.
    
- **Modelagem de Dados (`app/schemas.py`)**:
    
    - Criação dos modelos **Pydantic** (`ItemMercado` e `ListaSeparacaoMercado`).
        
    - Definição do contrato de dados rigoroso em JSON para mapear produtos, marcas preferidas, quantidades, unidades de medida e categorias.
        
- **Módulo de Integração com IA (`app/services.py`)**:
    
    - Implementação da chamada inicial ao SDK do Google Gemini com instruções de sistema (`SYSTEM_INSTRUCTION`).
        
    - Mapeamento das categorias permitidas: _Açougue, Laticínios e Frios, Hortifruti, Mercearia, Bebidas, Limpeza e Higiene, Outros_.
        
## 📍 Dia 2: Resiliência, Tratamento de Erros e Fallback Engine
- **Tratamento de Limites da API do Gemini (Erros 503 e 429)**:
    
    - Implementação do pacote `tenacity` com estratégia de retentativas e tempo de espera exponencial (`wait_exponential`).
        
    - Resolução de conflitos de versões e migração para os modelos ativos (`gemini-3.8-flash`).
        
- **Criação da Engine Local de Fallback (Regex Inteligente)**:
    
    - Desenvolvimento do parser local `extrair_itens_inteligente()` para garantir **100% de disponibilidade do sistema** (zero downtime) caso a API do Gemini atinja o limite de quota ou fique instável.
        
- **Tratamento Dinâmico de Unidades e Quantidades**:
    
    - Implementação de expressões regulares para interpretar números colados a unidades (ex: `2kg`, `2k`).
        
    - Mapeamento de valores monetários (ex: `10 reais de queijo`).
        
    - Padronização automática para formas abreviadas:
        
        - `unidades` / `unidade` $\rightarrow$ `un`
            
        - `pacotes` / `pacote` $\rightarrow$ `pct`
            
        - `caixas` / `caixa` $\rightarrow$ `cx`
            
        - `fardos` / `fardo` $\rightarrow$ `fardo`
            
        - `kg` / `k` $\rightarrow$ `kg`
            
        - `reais` / `real` $\rightarrow$ `reais`
            
## 📍 Dia 3: Frontend, Comunicação CORS e Refinamento do Painel
- **Desenvolvimento da Interface (`templates/index.html`)**:
    
    - Construção do painel de testes interativo utilizando **Tailwind CSS**.
        
    - Criação de cartões para simulação do pedido e visualização da lista de separação categorizada em tempo real.
        
- **Resolução de Conectividade Cross-Origin (CORS) e Live Server**:
    
    - Ajuste na função JavaScript `enviarPedido()` utilizando `window.location.hostname` para resolução dinâmica de IP/domínio.
        
    - Permissão para que a aplicação seja acedida via **Live Server** (porta `5500`), **FastAPI** (`8000`) ou por outros dispositivos na mesma rede local sem necessidade de alterar o código.
        
- **Formatação de Exibição do Frontend**:
    
    - Ajuste no consumo da chave `item.unidade_medida`.
        
    - Formatação visual especial para valores monetários (`R$ 10.00`) e quantidades por peso/embalagem.
        
## 📍 Dia 4: Finalização, Documentação e Organização do Git
- **Ajustes no Repositório e Ficheiros de Configuração**:
    
    - Atualização do `requirements.txt` com todas as dependências do ambiente virtual (`google-genai`, `fastapi`, `uvicorn`, `pydantic`, `tenacity`, `python-dotenv`).
        
    - Ajuste fino do ficheiro `.gitignore` para ignorar a pasta `.obsidian/` e ambientes virtuais, mantendo a proteção de chaves sensíveis no `.env` e preservando o ficheiro `templates/index.html`.
        
- **Documentação Técnica e Guia de Início**:
    
    - Mapeamento detalhado da arquitetura e responsabilidade de cada ficheiro do projeto.
        
    - Passo a passo completo de instalação e execução para apresentação pública e avaliação.
## 📍 Dia 5: Estruturação Inicial e Backend Base
- Configuração do servidor **FastAPI** e servidor Uvicorn rodando na porta `8000`.
    
- Criação dos contratos Pydantic (`ItemMercado`, `ListaSeparacaoMercado`) em `app/schemas.py`.
    
- Integração inicial com a API do Gemini e definição das regras de separação.
## 📍 Dia 6: Resiliência, Fallback Engine e Interface Inicial
- Criação da engine de fallback via Regex (`extrair_itens_inteligente()`) para zero downtime.
    
- Suporte a unidades dinâmicas (`kg`, `pct`, `cx`, `reais`, `un`).
    
- Construção da primeira versão do dashboard de testes no frontend (`templates/index.html`).
## 📍 Dia 7: Rebranding para "Cana" e Transição de Marca
- Transição da persona do bot de "Hermes" para **Cana (Sacolão da Economia)**.
    
- Redesign do frontend com paleta verde sustentável (`emerald`), novo mascote e mensagens focadas no uso de sacolas retornáveis e consumo consciente.
    
- Atualização do prompt do sistema em `app/services.py`.
## 📍 Dia 8: Arquitetura com Repository Pattern e PostgreSQL
- Criação do banco de dados relacional local no PostgreSQL 15 via Docker (`docker-compose.yml` e `init_db.sql`).
    
- Modelagem das tabelas relativas a produtos, categorias e saldos em estoque.
    
- Implementação do **Repository Pattern** (`app/repositories/`):
    
    - Interface abstrata `AbstractProductRepository`.
        
    - Implementação `PostgresMockRepository` com integração `psycopg2-binary`.
        
    - Stub `SysPDVApiRepository` preparado para integração futura com o ERP comercial.
        
    - Fábrica de injeção de dependência em `factory.py`.
        
- Conexão entre a camada de extração de IA em `app/services.py` e as consultas do repositório relacional.