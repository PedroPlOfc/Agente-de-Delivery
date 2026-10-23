projeto-cana/
├── app/
│   ├── repositories/             # Camada de Dados (Repository Pattern)
│   │   ├── __init__.py
│   │   ├── base.py               # Interface Abstrata (AbstractProductRepository)
│   │   ├── postgres_mock.py      # Repositório do PostgreSQL Local
│   │   ├── syspdv_api.py         # Repositório do ERP SysPDV (Futuro)
│   │   └── factory.py            # Injeção de Dependência da Fonte de Dados
│   ├── schemas.py                # Contratos Pydantic (Validação e Tipagem)
│   ├── services.py               # Motor de IA (LangChain/Gemini) e Fallback Local
│   ├── estado.py                 # Gerenciamento de Sessão/Carrinho (Redis / Memória)
│   ├── config.py                 # Carregamento de Variáveis de Ambiente
│   └── whatsapp.py               # Envio de Mensagens para Evolution API
├── templates/
│   └── index.html                # Dashboard do Cana (HTML5 + Tailwind CSS Emerald)
├── .env                          # Chaves e Configurações de Conexão
├── .gitignore                    # Regras do Git (.env, venv, .obsidian)
├── docker-compose.yml            # Infraestrutura de Containers (PostgreSQL / Redis)
├── init_db.sql                   # Script SQL com Estrutura e Mock Data do Sacolão
├── main.py                       # Servidor Backend FastAPI
└── requirements.txt              # Dependências Python