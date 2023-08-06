from sqlalchemy import Column, String, Boolean

from ..base import ModelBase


class Usuario(ModelBase):
    """Usuário do sistema."""
    __tablename__ = 'Usuario'

    email = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

    admin = Column(Boolean, default=False, nullable=False)
