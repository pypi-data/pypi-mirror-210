"""Modelo de dados para coleta de dados."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from ..base import ModelBase


class Coleta(ModelBase):
    """Coleta de dados."""
    __tablename__ = 'Coleta'

    execucao_item_uuid = Column(
        String(36),
        ForeignKey('ExecucaoItem.uuid'),
        nullable=False
    )
    execucao_item = declared_attr(
        lambda cls: relationship(
            'ExecucaoItem', backref='Coleta',
        ))
