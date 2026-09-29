import pytest
from pydantic import ValidationError
from app.schemas import MensagemEntrada, ItemMercado, ListaSeparacaoMercado

def test_validacao_mensagem_entrada_sucesso():
    """Valida a criação de um payload correto de entrada."""
    dados = {"telefone": "+5581999999999", "mensagem": "Quero 1kg de feijão"}
    modelo = MensagemEntrada(**dados)
    assert modelo.telefone == "+5581999999999"
    assert modelo.mensagem == "Quero 1kg de feijão"

def test_validacao_mensagem_entrada_erro():
    """Garante erro de validação quando campos obrigatórios estão ausentes."""
    with pytest.raises(ValidationError):
        MensagemEntrada(telefone="+5581999999999")  # Faltando campo 'mensagem'

def test_validacao_item_mercado_valores_padrao():
    """Garante que os valores padrão de aceita_substituicao e observacao são aplicados."""
    item_dados = {
        "produto": "Leite Integral",
        "quantidade": 2.0,
        "unidade_medida": "litros"
    }
    item = ItemMercado(**item_dados)
    assert item.produto == "Leite Integral"
    assert item.aceita_substituicao is True
    assert item.observacao == ""
    assert item.marca_preferida is None

def test_validacao_lista_separacao_completa(exemplo_resposta_gemini_valida):
    """Valida a desserialização de uma lista completa vinda da resposta do modelo."""
    lista = ListaSeparacaoMercado(**exemplo_resposta_gemini_valida)
    assert len(lista.itens) == 2
    assert lista.itens[0].produto == "Arroz"
    assert lista.itens[1].categoria == "Laticínios"
    assert lista.duvida_ou_incompleto is False