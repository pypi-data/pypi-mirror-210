"""Modelo de grupo de usuário."""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import ModelBase


class GrupoUsuario(ModelBase):
    """Grupo de usuário."""
    __tablename__ = 'GrupoUsuario'

    usuario_uuid = Column(String(36), nullable=False)

    grupo_uuid = Column(String(36), ForeignKey("Grupo.uuid"), nullable=False)
    grupo = declared_attr(lambda cls: relationship(
        'Grupo', backref='GrupoUsuario',
    ))
