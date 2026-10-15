## 📁 `app/schemas.py` — _A Regra do Negócio (Tipagem e Contratos)_

Este arquivo define a estrutura exata dos dados que trafegam na aplicação usando **Pydantic** e **TypedDict**.

- **`ItemMercado`**: Modelo de um item individual do pedido. Define os campos com valores padrão de segurança (`produto`, `quantidade`, `unidade_medida`, `categoria`, `aceita_substituicao`, etc.).
    
- **`ListaSeparacaoMercado`**: O contrato principal de saída da IA. Agrupa a lista de itens, o nome do cliente, endereço e a mensagem que será enviada para o WhatsApp.
    
- **`MensagemEntrada`**: O modelo de entrada da requisição vinda do painel web ou webhook (`telefone` e `mensagem`).
    

## 📁 `app/services.py` — _O Cérebro da Inteligência (IA + Fallback Engine)_

Responsável por pegar o texto digitado pelo cliente e transformá-lo na estrutura JSON. Possui uma arquitetura híbrida de alta disponibilidade:

- **`chamar_gemini()`**: Tenta enviar a mensagem para a API oficial do Gemini (`gemini-3.8-flash`) solicitando uma resposta formatada em JSON.
    
- **`gerar_resposta_local()` / `extrair_itens_inteligente()`**: Se a API do Gemini estiver fora do ar ou sem cota (erros 503/429), o sistema aciona instantaneamente este parser local regex. Ele lê linha a linha, ajusta as quantidades, mapeia unidades dinâmicas (`2kg` $\rightarrow$ `kg`, `2 pacotes` $\rightarrow$ `pct`, `10 reais` $\rightarrow$ `reais`) e categoriza o produto sem deixar a aplicação falhar.
    

## 📁 `main.py` — _O Servidor HTTP (FastAPI)_

É o ponto de entrada da aplicação backend:

- **Configuração e CORS**: Libera acessos de qualquer origem (`allow_origins=["*"]`) para que o painel funcione via Live Server (porta 5500), localhost (8000) ou outros dispositivos da rede.
    
- **`@app.get("/")`**: Serve a interface web carregando o `templates/index.html`.
    
- **`@app.post("/webhook/mercado")`**: Endpoint consumido pelo painel de testes. Recebe a mensagem, chama o `app/services.py`, faz a limpeza de markdown (```json) e valida o resultado final com o `ListaSeparacaoMercado` do Pydantic.
    
- **`@app.post("/webhook/whatsapp")`**: Webhook preparado para receber eventos reais da API do WhatsApp (ex: Evolution API / Z-API), ignorando mensagens enviadas por você mesmo (`fromMe`) e respondendo aos clientes automaticamente.
    

## 📁 `templates/index.html` — _O Dashboard da Apresentação (Frontend)_

Interface gráfica construída com HTML5, Tailwind CSS e JavaScript:

- **Layout responsivo**: Dividido em dois cards (Simular Pedido de Cliente e Resultado da IA).
    
- **`enviarPedido()` (JS Dinâmico)**: Usa `window.location.hostname` para detectar dinamicamente de onde a página foi aberta (seja no Live Server, no FastAPI ou pelo IP na rede local) e redireciona as chamadas automaticamente para a porta `8000`.
    
- **Renderização de Unidades**: Trata o JSON recebido, exibindo itens com destaque para valores em dinheiro (`R$ 10.00`), pesos (`2 kg`), pacotes (`2 pct`) e fardos.
    

## 📁 `app/whatsapp.py` — _A Integração de Envio Externo_

Contém a função auxiliar para realizar chamadas HTTP (`requests.post`) para a API do WhatsApp/Evolution, enviando o texto contido em `mensagem_resposta` diretamente para o celular do cliente.

## 📁 `.env` & `requirements.txt` — _Configurações e Dependências_

- **`.env`**: Guarda a chave de API do Google (`GEMINI_API_KEY`) com segurança sem expor credenciais no código do GitHub.
    
- **`requirements.txt`**: Lista os pacotes Python essenciais para rodar o projeto (`fastapi`, `uvicorn`, `google-genai`, `pydantic`, `tenacity`, `python-dotenv`).