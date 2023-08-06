"""Modelo de item de execução de agendamento."""""
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from ..base import ModelBase


class ExecucaoItem(ModelBase):
    """Item de execução de agendamento."""
    __tablename__ = 'ExecucaoItem'

    execucao_uuid = Column(
        String(36),
        ForeignKey('Execucao.uuid'),
        nullable=False
    )
    execucao = declared_attr(
        lambda cls: relationship(
            'Execucao', backref='ExecucaoItem',
        ))

    tempo_de_coleta = Column(Float, nullable=False)
