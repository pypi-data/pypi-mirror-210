from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from ..base import ModelBase


class Colaborador(ModelBase):
    """Modelo de colaborador."""
    __tablename__ = 'Colaborador'

    empresa_uuid = Column(
        String(36),
        ForeignKey('Empresa.uuid'),
        nullable=False
    )
    empresa = declared_attr(
        lambda cls: relationship(
            'Empresa', backref='Colaborador',
        ))

    usuario_uuid = Column(
        String(36),
        ForeignKey('Usuario.uuid'),
        nullable=False
    )
    usuario = declared_attr(
        lambda cls: relationship(
            'Usuario', backref='Colaborador',
        ))


class PermissaoColaborador(ModelBase):
    """Modelo de permissão de colaborador."""
    __tablename__ = 'PermissaoColaborador'

    colaborador_uuid = Column(
        String(36),
        ForeignKey('Colaborador.uuid'),
        nullable=False
    )
    colaborador = declared_attr(
        lambda cls: relationship(
            'Colaborador', backref='PermissaoColaborador',
        ))

    permissao_uuid = Column(
        String(36),
        ForeignKey('Permissao.uuid'),
        nullable=False
    )
    permissao = declared_attr(
        lambda cls: relationship(
            'Permissao', backref='PermissaoColaborador',
        ))


class GrupoColaborador(ModelBase):
    """Modelo de grupo de colaborador."""
    __tablename__ = 'GrupoColaborador'

    colaborador_uuid = Column(
        String(36),
        ForeignKey('Colaborador.uuid'),
        nullable=False
    )
    colaborador = declared_attr(
        lambda cls: relationship(
            'Colaborador', backref='GrupoColaborador',
        ))

    grupo_uuid = Column(
        String(36),
        ForeignKey('Grupo.uuid'),
        nullable=False
    )
    grupo = declared_attr(
        lambda cls: relationship(
            'Grupo', backref='GrupoColaborador',
        ))
