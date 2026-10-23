### Pró-requisitos

- **Python 3.10+** instalado
    
- Uma chave de API do Gemini (`GEMINI_API_KEY`) obtida no [Google AI Studio](https://aistudio.google.com/)
    (Para quem for trabalhar no projeto, a pasta .env será passada no privado, obviamente)

### Passo 1: Clonar o Repositório

Abra o terminal ou Git Bash no diretório desejado e execute:

Bash

```
git clone https://github.com/PedroPlOfc/Agente-de-Delivery.git
cd "Agente de Ia para Delivery"
```

### Passo 2: Criar e Ativar o Ambiente Virtual (`venv`)

- **Windows (PowerShell / Command Prompt):**
    
    Bash
    
    ```
    python -m venv venv
    .\venv\Scripts\activate
    ```
    
- **Linux / macOS / Git Bash:**
    
    Bash
    
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
    

### Passo 3: Instalar as Dependências

Com o ambiente virtual ativado, instale as bibliotecas listadas no `requirements.txt`:

Bash

```
pip install -r requirements.txt 
# Ou se estiver usando o gerenciador uv:
uv pip install -r requirements.txt
```

### Passo 4: Configurar a Chave da API (`.env`)

Crie um arquivo chamado `.env` na raiz do projeto e adicione a sua chave do Gemini:

Snippet de código

```
# --- IA --- GEMINI_API_KEY=sua_chave_gemini_aqui GEMINI_MODEL=gemini-3.8-flash GEMINI_FALLBACK_MODEL=gemini-1.5-flash
# --- Evolution API (WhatsApp) --- EVOLUTION_API_URL=http://localhost:8080 EVOLUTION_INSTANCE=sacolao_cana EVOLUTION_API_KEY=sua_chave_evolution_aqui 
# --- Repositório & Banco de Dados (PostgreSQL Local) --- DATA_SOURCE_PROVIDER=POSTGRES_MOCK POSTGRES_PASSWORD=sua_senha_postgres_aqui DATABASE_URL=postgresql://evolution:sua_senha_postgres_aqui@localhost:5432/evolution 
# --- Futura Integração SysPDV --- SYSPDV_API_URL= SYSPDV_TOKEN=
```
### Passo 5: Inicializar o Banco de Dados PostgreSQL (Docker)

1. Certifique-se de que o **Docker Desktop** está rodando.
    
2. Suba o container do PostgreSQL: 
```
docker compose up -d postgres
```
3. Execute o script de inicialização `init_db.sql` para criar as tabelas e popular os dados de teste do **Sacolão da Economia**:

- Powershell
```
Get-Content init_db.sql | docker exec -i evolution_postgres psql -U evolution -d evolution
```

- Git Bash / Linux / macOS
```
Iniciar o Servidor Backend (FastAPI)
```

### Passo 6: Iniciar o Servidor Backend (FastAPI): Execute o arquivo principal para subir o servidor local na porta `8000`:

Bash

```
python main.py
```

> O terminal exibirá mensagens de inicialização do `uvicorn` indicando que o servidor está rodando em `[http://0.0.0.0:8000](http://0.0.0.0:8000)`.

### Passo 7: Acessar a Interface do Cana

Abra o navegador em `http://127.0.0.1:8000` para interagir com o **Cana**, simular o atendimento do Sacolão da Economia e testar a extração de itens e consulta de estoque em tempo real.
