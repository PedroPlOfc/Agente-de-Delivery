"""Cliente HTTP do backend Java.

Este módulo é a única ponte entre o serviço Python e os dados de negócio.
Python não abre conexão com PostgreSQL nem Redis: toda persistência passa pelo Java.
"""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import httpx

from app import config

log = logging.getLogger("cana.java_api")


class JavaApiError(RuntimeError):
    """O backend Java não respondeu ou rejeitou uma operação."""


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if config.INTERNAL_API_TOKEN:
        headers["X-Internal-Token"] = config.INTERNAL_API_TOKEN
    return headers


def _request(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{config.JAVA_API_URL}{path}"
    headers = {**_headers(), **kwargs.pop("headers", {})}
    try:
        response = httpx.request(
            method,
            url,
            headers=headers,
            timeout=config.JAVA_API_TIMEOUT,
            **kwargs,
        )
        response.raise_for_status()
        if not response.content:
            return None
        return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:500]
        raise JavaApiError(
            f"Backend Java respondeu HTTP {exc.response.status_code}: {detail}"
        ) from exc
    except httpx.RequestError as exc:
        raise JavaApiError(
            f"Não foi possível conectar ao backend Java em {config.JAVA_API_URL}."
        ) from exc


def buscar_produtos(nome: str) -> list[dict[str, Any]]:
    if not nome.strip():
        return []
    resultado = _request("GET", "/api/products", params={"query": nome})
    return resultado if isinstance(resultado, list) else []


def buscar_produto_por_codigo(codigo: str) -> dict[str, Any] | None:
    return _request("GET", f"/api/products/barcode/{quote(codigo, safe='')}")


def consultar_estoque(produto_id: int) -> dict[str, Any]:
    return _request("GET", f"/api/products/{produto_id}/stock")


def carregar_carrinho(telefone: str) -> list[dict[str, Any]]:
    resultado = _request("GET", f"/api/carts/{quote(telefone, safe='')}")
    return resultado.get("itens", []) if isinstance(resultado, dict) else []


def salvar_carrinho(telefone: str, itens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    resultado = _request(
        "PUT",
        f"/api/carts/{quote(telefone, safe='')}",
        json={"itens": itens},
    )
    return resultado.get("itens", itens) if isinstance(resultado, dict) else itens


def limpar_carrinho(telefone: str) -> None:
    _request("DELETE", f"/api/carts/{quote(telefone, safe='')}")


def criar_pedido(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/api/orders", json=payload)


def verificar_saude() -> bool:
    try:
        resultado = _request("GET", "/api/health")
        return isinstance(resultado, dict) and resultado.get("status") == "ok"
    except JavaApiError:
        log.warning("Backend Java indisponível.")
        return False


def admin_call(method: str, path: str, token: str | None = None, *, params: dict | None = None,
               payload: dict | None = None) -> Any:
    """Proxy de operações administrativas. O navegador nunca recebe o token interno do Java."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    kwargs: dict[str, Any] = {}
    if params is not None:
        kwargs["params"] = params
    if payload is not None:
        kwargs["json"] = payload
    return _request(method, path, headers=headers, **kwargs)


def admin_login(username: str, password: str) -> dict[str, Any]:
    result = _request("POST", "/api/admin/auth/login", json={"username": username, "password": password})
    return result if isinstance(result, dict) else {}
