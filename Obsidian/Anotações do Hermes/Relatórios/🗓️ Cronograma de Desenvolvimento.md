### 📍 Dia 1: Estruturação Inicial e Backend Base

- **Criação do Ponto de Entrada (`main.py`)**: Configuração do servidor web assíncrono com **FastAPI** e servidor **Uvicorn** rodando na porta `8000`.
    
- **Modelagem de Dados (`app/schemas.py`)**:
    
    - Criação dos modelos **Pydantic** (`ItemMercado` e `ListaSeparacaoMercado`).
        
    - Definição do contrato de dados rigoroso em JSON para mapear produtos, marcas preferidas, quantidades, unidades de medida e categorias.
        
- **Módulo de Integração com IA (`app/services.py`)**:
    
    - Implementação da chamada inicial ao SDK do Google Gemini com instruções de sistema (`SYSTEM_INSTRUCTION`).
        
    - Mapeamento das categorias permitidas: _Açougue, Laticínios e Frios, Hortifruti, Mercearia, Bebidas, Limpeza e Higiene, Outros_.
        

### 📍 Dia 2: Resiliência, Tratamento de Erros e Fallback Engine

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
            

### 📍 Dia 3: Frontend, Comunicação CORS e Refinamento do Painel

- **Desenvolvimento da Interface (`templates/index.html`)**:
    
    - Construção do painel de testes interativo utilizando **Tailwind CSS**.
        
    - Criação de cartões para simulação do pedido e visualização da lista de separação categorizada em tempo real.
        
- **Resolução de Conectividade Cross-Origin (CORS) e Live Server**:
    
    - Ajuste na função JavaScript `enviarPedido()` utilizando `window.location.hostname` para resolução dinâmica de IP/domínio.
        
    - Permissão para que a aplicação seja acedida via **Live Server** (porta `5500`), **FastAPI** (`8000`) ou por outros dispositivos na mesma rede local sem necessidade de alterar o código.
        
- **Formatação de Exibição do Frontend**:
    
    - Ajuste no consumo da chave `item.unidade_medida`.
        
    - Formatação visual especial para valores monetários (`R$ 10.00`) e quantidades por peso/embalagem.
        

### 📍 Dia 4: Finalização, Documentação e Organização do Git

- **Ajustes no Repositório e Ficheiros de Configuração**:
    
    - Atualização do `requirements.txt` com todas as dependências do ambiente virtual (`google-genai`, `fastapi`, `uvicorn`, `pydantic`, `tenacity`, `python-dotenv`).
        
    - Ajuste fino do ficheiro `.gitignore` para ignorar a pasta `.obsidian/` e ambientes virtuais, mantendo a proteção de chaves sensíveis no `.env` e preservando o ficheiro `templates/index.html`.
        
- **Documentação Técnica e Guia de Início**:
    
    - Mapeamento detalhado da arquitetura e responsabilidade de cada ficheiro do projeto.
        
    - Passo a passo completo de instalação e execução para apresentação pública e avaliação.