"""Modelo de execução de agendamento."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from ..base import ModelBase


class Execucao(ModelBase):
    """Execução de agendamento."""
    __tablename__ = 'Execucao'

    agendamento_uuid = Column(
        String(36),
        ForeignKey("Agendamento.uuid"),
        nullable=False
    )
    agendamento = declared_attr(
        lambda cls: relationship(
            'Agendamento', backref='Execucao',
        ))
