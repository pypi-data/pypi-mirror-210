from uuid import uuid4
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship


def uuid_default():
    return str(uuid4())


def relacao_usuario(backref):
    """Relação de usuário."""
    class Relacao():
        """Relação de usuário."""

        usuario_uuid = Column(
            String(36),
            ForeignKey("Usuario.uuid"),
            nullable=False
        )
        usuario = declared_attr(lambda cls: relationship(
            'Usuario', backref=backref,
        ))
    return Relacao
