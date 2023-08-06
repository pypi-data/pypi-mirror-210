"""ModeloBase de endereço."""
from sqlalchemy import Column, String


class EnderecoModelBase():
    """ModeloBase de endereço."""
    logradouro = Column(String(100), nullable=False)
    numero = Column(String(10), nullable=False)
    complemento = Column(String(100), nullable=False)
    bairro = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    cep = Column(String(8), nullable=False)
    estado = Column(String(2), nullable=False)
