"""Módulo de grupo de permissão."""
from sqlalchemy import Column, String, Boolean
from ..base import ModelBase


class Grupo(ModelBase):
    """Grupo de permissão."""
    __tablename__ = 'Grupo'
    nome = Column(String(255), nullable=False)
    descricao = Column(String(255))
    custom = Column(Boolean, default=False, nullable=False)

    @staticmethod
    def get_or_create(cls, nome, db):
        """Retorna o grupo ou cria um novo."""
        grupo = cls.query.filter(
            cls.custom == 0,
            cls.excludo == 0,
            cls.nome == nome,
        ).first()
        if not grupo:
            grupo = cls(nome=nome, custom=False)
            grupo.add(db)
        return grupo

    @staticmethod
    def gerar_grupos(cls, permissao, db):
        raws = permissao.permissoes_sem_grupo_correspondente(
            db
        )
        for raw in raws:
            grupo = cls(nome=raw[0], custom=False)
            grupo.add(db)
        db.session.commit()
