"""Modelo de agendamento para o scheduler."""
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from ..base import ModelBase


class Agendamento(ModelBase):
    """Agendamento para o scheduler."""
    __tablename__ = 'Agendamento'

    dia = Column(Integer, nullable=False)
    hora = Column(Integer, nullable=False)
    minuto = Column(Integer, nullable=False)

    credencial_uuid = Column(
        String(36),
        ForeignKey("Credencial.uuid"),
        nullable=False
    )
    credencial = declared_attr(
        lambda cls: relationship(
            'Credencial', backref='Agendamento',
        ))
