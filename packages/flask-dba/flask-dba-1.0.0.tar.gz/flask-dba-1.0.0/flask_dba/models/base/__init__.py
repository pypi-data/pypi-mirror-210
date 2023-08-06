"""Model base para todos os modelos."""
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
from ..utils import uuid_default


class ModelMetodosBase():
    """Model base para todos os modelos."""

    def add(self, db):
        """Adiciona o obj ao banco de dados."""
        db.session.add(self)
        self.flush(db)

    def save(self, db):
        """Faz Commit no banco de dados."""
        db.session.commit()

    def flush(self, db):
        """Atualiza as informações do banco de dados."""
        db.session.flush()


class ModelBase(ModelMetodosBase):
    """Model base para todos os modelos."""
    uuid = Column(
        String(36),
        primary_key=True,
        default=uuid_default,
        unique=True,
        nullable=False
    )
    data_criado = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    data_atualizado = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    excludo = Column(
        Boolean,
        default=False,
        nullable=False
    )
    ativo = Column(
        Boolean,
        default=True,
        nullable=False
    )
