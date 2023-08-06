from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from ..base import ModelBase


class Empresa(ModelBase):
    """Modelo de empresa."""
    __tablename__ = 'Empresa'

    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255), nullable=False)
    cpf_cnpj = Column(String(255), nullable=False)
    inscricao_municipal = Column(String(255), nullable=False)
    inscricao_estadual = Column(String(255), nullable=False)
    telefone = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)


class EmpresaEndereco(ModelBase):
    """Modelo do endereço da empresa."""
    __tablename__ = 'EmpresaEndereco'

    empresa_uuid = Column(
        String(36),
        ForeignKey('Empresa.uuid'),
        nullable=False
    )
    empresa = declared_attr(
        lambda cls: relationship(
            'Empresa', backref='EmpresaEndereco',
        ))

    endereco_uuid = Column(
        String(36),
        ForeignKey('Endereco.uuid'),
        nullable=False
    )
    endereco = declared_attr(
        lambda cls: relationship(
            'Endereco', backref='EmpresaEndereco',
        ))
