from unittest.mock import patch
from app.schemas import ListaSeparacaoMercado


def test_endpoint_webhook_mercado_sucesso(client, exemplo_payload_valido, exemplo_resposta_gemini_valida):
    lista_mock = ListaSeparacaoMercado(**exemplo_resposta_gemini_valida).model_dump()

    with patch("main.carregar_carrinho", return_value=[]), \
         patch("main.salvar_carrinho") as mock_salvar, \
         patch("main.chamar_gemini", return_value=lista_mock) as mock_gemini:
        response = client.post("/webhook/mercado", json=exemplo_payload_valido)

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"
    assert json_resp["cliente"] == "+5581999999999"
    assert len(json_resp["lista_separacao"]["itens"]) == 2
    mock_gemini.assert_called_once_with(exemplo_payload_valido["mensagem"], [])
    mock_salvar.assert_called_once()


def test_endpoint_webhook_mercado_payload_invalido(client):
    response = client.post("/webhook/mercado", json={"telefone": "+5581999999999"})
    assert response.status_code == 422


def test_endpoint_webhook_whatsapp_ignora_propria_mensagem(client):
    payload_whatsapp = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "fromMe": True,
                "remoteJid": "5581999999999@s.whatsapp.net",
            }
        },
    }
    response = client.post("/webhook/whatsapp", json=payload_whatsapp)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}


def test_endpoint_webhook_mercado_retorna_503_quando_java_fica_indisponivel(client, exemplo_payload_valido):
    from app.java_api import JavaApiError

    with patch("main.carregar_carrinho", side_effect=JavaApiError("Java fora do ar")):
        response = client.post("/webhook/mercado", json=exemplo_payload_valido)

    assert response.status_code == 503
    assert "indisponível" in response.json()["detail"]
