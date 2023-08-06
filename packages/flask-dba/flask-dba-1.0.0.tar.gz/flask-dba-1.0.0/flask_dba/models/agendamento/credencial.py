"""Modelo de credencial."""
from sqlalchemy import Column, String
from ..base import ModelBase


class Credencial(ModelBase):
    """Credencial de acesso."""
    __tablename__ = 'Credencial'

    login = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False)
