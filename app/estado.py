"""Armazena o carrinho por telefone (Redis se REDIS_URL existir, senão memória)."""
import json
import logging
from typing import Dict, List

from app.config import REDIS_URL

log = logging.getLogger("hermes.estado")
TTL_SEGUNDOS = 60 * 60 * 24  # carrinho expira em 24h

_memoria: Dict[str, List[dict]] = {}
_redis = None

if REDIS_URL:
    try:
        import redis

        _redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        _redis.ping()
    except Exception as e:  # noqa: BLE001
        log.warning("Redis indisponível (%s). Usando memória local.", e)
        _redis = None


def _chave(telefone: str) -> str:
    return "hermes:carrinho:" + "".join(c for c in telefone if c.isdigit())


def carregar_carrinho(telefone: str) -> List[dict]:
    if _redis:
        try:
            bruto = _redis.get(_chave(telefone))
            return json.loads(bruto) if bruto else []
        except Exception as e:  # noqa: BLE001
            log.warning("Falha ao ler Redis: %s", e)
    return list(_memoria.get(_chave(telefone), []))


def salvar_carrinho(telefone: str, itens: List[dict]) -> None:
    if _redis:
        try:
            _redis.set(_chave(telefone), json.dumps(itens, ensure_ascii=False), ex=TTL_SEGUNDOS)
            return
        except Exception as e:  # noqa: BLE001
            log.warning("Falha ao gravar Redis: %s", e)
    _memoria[_chave(telefone)] = list(itens)
