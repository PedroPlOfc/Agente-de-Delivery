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
```

### Passo 4: Configurar a Chave da API (`.env`)

Crie um arquivo chamado `.env` na raiz do projeto e adicione a sua chave do Gemini:

Snippet de código

```
GEMINI_API_KEY=sua_chave_api_aqui
```

O .env também possui uma segunda chave, usada para quando o bot for ser testado em um whatsapp usando a Evolution API.

```
EVOLUTION_API_KEY=sua_chave_api_aqui
```
### Passo 5: Iniciar o Servidor Backend (FastAPI)

Execute o arquivo principal para subir o servidor local na porta `8000`:

Bash

```
python main.py
```

> O terminal exibirá mensagens de inicialização do `uvicorn` indicando que o servidor está rodando em `[http://0.0.0.0:8000](http://0.0.0.0:8000)`.

### Passo 6: Acessar o Painel de Testes

Você pode abrir o painel de duas formas:

1. **Pelo próprio FastAPI (Recomendado):** Acesse no navegador:
    
    Plaintext
    
    ```
    http://127.0.0.1:8000
    ```
    
2. **Via Live Server (VS Code):** Abra o arquivo `templates/index.html` e clique em **Go Live** no VS Code. O painel se conectará automaticamente à porta `8000` do backend!