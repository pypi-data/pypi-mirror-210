from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from ..base import ModelBase
from ..base.endereco import EnderecoModelBase


class Endereco(EnderecoModelBase, ModelBase):
    """Modelo de endereço."""
    __tablename__ = 'Endereco'
    estado_uuid = Column(
        String(36),
        ForeignKey('Estado.uuid'),
        nullable=False
    )
    estado = declared_attr(
        lambda cls: relationship(
            'Estado', backref='Endereco',
        ))


class UsuarioEndereco(ModelBase):
    """Modelo de endereço de usuário."""
    __tablename__ = 'UsuarioEndereco'

    endereco_uuid = Column(
        String(36),
        ForeignKey('Endereco.uuid'),
        nullable=False
    )
    endereco = declared_attr(
        lambda cls: relationship(
            'Endereco', backref='UsuarioEndereco',
        ))


class Estado(ModelBase):
    """Modelo de estado."""
    __tablename__ = 'Estado'
    nome = Column(String(100), nullable=False)
    sigla = Column(String(2), nullable=False)
