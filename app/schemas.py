from typing import List, Optional, TypedDict
from pydantic import BaseModel

# --- SCHEMAS TYPEDDICT PARA O GEMINI SDK ---
class ItemMercadoSchema(TypedDict):
    produto: str
    marca_preferida: Optional[str]
    quantidade: float
    unidade_medida: str
    categoria: Optional[str]
    aceita_substituicao: bool
    observacao: Optional[str]

class ListaSeparacaoMercadoSchema(TypedDict):
    nome_cliente: Optional[str]
    endereco_entrega: Optional[str]
    itens: List[ItemMercadoSchema]
    duvida_ou_incompleto: bool
    mensagem_resposta: str

# --- MODELOS PYDANTIC PARA VALIDAÇÃO DAS REQUISIÇÕES/RESPOSTAS ---
class ItemMercado(BaseModel):
    produto: str
    marca_preferida: Optional[str] = None
    quantidade: float
    unidade_medida: str
    categoria: Optional[str] = None
    aceita_substituicao: bool = True
    observacao: Optional[str] = ""

class ListaSeparacaoMercado(BaseModel):
    nome_cliente: Optional[str] = None
    endereco_entrega: Optional[str] = None
    itens: List[ItemMercado]
    duvida_ou_incompleto: bool
    mensagem_resposta: str

class MensagemEntrada(BaseModel):
    telefone: str
    mensagem: str