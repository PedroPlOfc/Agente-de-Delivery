from unittest.mock import patch
from app.schemas import ListaSeparacaoMercado

def test_endpoint_webhook_mercado_sucesso(client, exemplo_payload_valido, exemplo_resposta_gemini_valida):
    """Testa a rota /webhook/mercado simulando o retorno do Gemini via Mock."""
    # Instancia o schema validado para simular o retorno do Pydantic
    lista_mock = ListaSeparacaoMercado(**exemplo_resposta_gemini_valida)
    
    # Substitui a chamada real do chamar_gemini pelo mock
    with patch("main.chamar_gemini") as mock_gemini:
        # Define que o mock retornará o JSON da lista
        mock_gemini.return_value = lista_mock.model_dump_json()
        
        response = client.post("/webhook/mercado", json=exemplo_payload_valido)
        
        assert response.status_code == 200
        json_resp = response.json()
        assert json_resp["status"] == "sucesso"
        assert json_resp["cliente"] == "+5581999999999"
        assert len(json_resp["lista_separacao"]["itens"]) == 2
        
        # Garante que a função mockada foi chamada exatamente 1 vez
        mock_gemini.assert_called_once_with(exemplo_payload_valido["mensagem"])

def test_endpoint_webhook_mercado_payload_invalido(client):
    """Testa a reação do endpoint quando enviam um JSON malformatado."""
    payload_invalido = {"telefone": "+5581999999999"}  # Sem o campo 'mensagem'
    response = client.post("/webhook/mercado", json=payload_invalido)
    assert response.status_code == 422  # Unprocessable Entity (Erro de validação do Pydantic)

def test_endpoint_webhook_whatsapp_ignora_propria_mensagem(client):
    """Garante que o webhook do WhatsApp ignora mensagens enviadas pelo próprio robô (fromMe=True)."""
    payload_whatsapp = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "fromMe": True,
                "remoteJid": "5581999999999@s.whatsapp.net"
            }
        }
    }
    response = client.post("/webhook/whatsapp", json=payload_whatsapp)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}