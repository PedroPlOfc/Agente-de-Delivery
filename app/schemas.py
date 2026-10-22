from typing import List, Optional

from pydantic import BaseModel, Field


class ItemMercado(BaseModel):
    produto: str
    marca_preferida: Optional[str] = None
    quantidade: float = 1.0
    unidade_medida: str = "un"
    categoria: Optional[str] = "Outros"
    aceita_substituicao: bool = True
    observacao: Optional[str] = ""


class ListaSeparacaoMercado(BaseModel):
    nome_cliente: Optional[str] = None
    endereco_entrega: Optional[str] = None
    itens: List[ItemMercado] = Field(default_factory=list)
    forma_pagamento: Optional[str] = "A definir"
    duvida_ou_incompleto: bool = False
    mensagem_resposta: str = ""


class MensagemEntrada(BaseModel):
    """Payload do painel de testes / integrações HTTP."""

    telefone: str = Field(min_length=1, max_length=40)
    mensagem: str = Field(min_length=1, max_length=1000)
    # Se omitido, o carrinho é recuperado do estado salvo para o telefone.
    itens_atuais: Optional[List[dict]] = None
