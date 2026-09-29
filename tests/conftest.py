import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Retorna um TestClient do FastAPI para simular chamadas HTTP aos endpoints."""
    return TestClient(app)

@pytest.fixture
def exemplo_payload_valido():
    """Payload de mensagem simulando um pedido real de cliente."""
    return {
        "telefone": "+5581999999999",
        "mensagem": "Quero 2kg de arroz, 1 pacote de macarrão e 10 reais de queijo coalho."
    }

@pytest.fixture
def exemplo_resposta_gemini_valida():
    """Simula um JSON retornado do Gemini no formato da ListaSeparacaoMercado."""
    return {
        "nome_cliente": None,
        "endereco_entrega": None,
        "itens": [
            {
                "produto": "Arroz",
                "marca_preferida": None,
                "quantidade": 2.0,
                "unidade_medida": "kg",
                "categoria": "Mercearia",
                "aceita_substituicao": True,
                "observacao": ""
            },
            {
                "produto": "Queijo coalho",
                "marca_preferida": None,
                "quantidade": 10.0,
                "unidade_medida": "reais",
                "categoria": "Laticínios",
                "aceita_substituicao": True,
                "observacao": ""
            }
        ],
        "duvida_ou_incompleto": False,
        "mensagem_resposta": "Pedido recebido com sucesso!"
    }