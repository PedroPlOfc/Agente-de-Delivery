import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional, Dict, Any
from app.repositories.base import AbstractProductRepository

class PostgresMockRepository(AbstractProductRepository):
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://evolution:senha_postgres_cana123@localhost:5432/evolution")

    def _get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def buscar_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        query = """
            SELECT p.id, p.codigo_barras, p.nome, p.preco_venda, p.unidade_medida, c.nome as categoria, e.quantidade_disponivel
            FROM produtos p
            JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN estoque e ON p.id = e.produto_id
            WHERE p.nome ILIKE %s AND p.ativo = TRUE
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (f"%{nome}%",))
                return cursor.fetchall()

    def buscar_por_codigo_barras(self, codigo_barras: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM produtos WHERE codigo_barras = %s AND ativo = TRUE"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (codigo_barras,))
                return cursor.fetchone()

    def verificar_estoque(self, produto_id: int) -> float:
        query = "SELECT quantidade_disponivel FROM estoque WHERE produto_id = %s"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (produto_id,))
                res = cursor.fetchone()
                return float(res["quantidade_disponivel"]) if res else 0.0