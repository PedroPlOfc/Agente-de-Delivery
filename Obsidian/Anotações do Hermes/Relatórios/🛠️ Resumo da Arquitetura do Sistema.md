projeto-hermes/ 
├── app/ │ 
	├── schemas.py # Contratos Pydantic (Validação e Tipagem) │ 
	├── services.py # Motor IA (Gemini API + Engine Local Regex) 
	└── whatsapp.py # Módulo de envio de mensagens externas 
├── templates/ │ 
	└── index.html # Painel de testes (HTML5 + Tailwind + JS Dinâmico) 
├── .env # Variáveis de ambiente (GEMINI_API_KEY) 
├── .gitignore # Regras do Git (.env, venv, .obsidian) 
├── main.py # Servidor Backend FastAPI & Endpoints 
└── requirements.txt # Lista de dependências Python