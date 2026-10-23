from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class AbstractProductRepository(ABC):
    """Contrato abstrato. Garante que trocar o banco não quebre a IA."""
    
    @abstractmethod
    def buscar_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def buscar_por_codigo_barras(self, codigo_barras: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def verificar_estoque(self, produto_id: int) -> float:
        pass