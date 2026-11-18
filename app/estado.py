"""Persistência do carrinho delegada integralmente ao backend Java/PostgreSQL."""
from typing import Any
from app.java_api import carregar_carrinho as _carregar
from app.java_api import salvar_carrinho as _salvar
from app.java_api import limpar_carrinho as _limpar


def carregar_carrinho(telefone: str) -> list[dict[str, Any]]:
    return _carregar(telefone)


def salvar_carrinho(telefone: str, itens: list[dict[str, Any]]) -> None:
    _salvar(telefone, itens)


def limpar_carrinho(telefone: str) -> None:
    _limpar(telefone)
