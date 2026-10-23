import os
from app.repositories.base import AbstractProductRepository
from app.repositories.postgres_mock import PostgresMockRepository
from app.repositories.syspdv_api import SysPDVApiRepository

def get_product_repository() -> AbstractProductRepository:
    data_source = os.getenv("DATA_SOURCE_PROVIDER", "POSTGRES_MOCK")

    if data_source == "SYSPDV_API":
        return SysPDVApiRepository()
    
    return PostgresMockRepository()