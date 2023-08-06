"""Módulo de permissão de grupo."""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import ModelBase


class PermissaoGrupo(ModelBase):
    """Permissão de grupo."""
    __tablename__ = 'PermissaoGrupo'
    grupo_uuid = Column(String(36), ForeignKey("Grupo.uuid"), nullable=False)
    grupo = declared_attr(lambda cls: relationship(
        'Grupo', backref='PermissaoGrupo',
    ))

    permissao_uuid = Column(
        String(36), ForeignKey("Permissao.uuid"), nullable=False)
    permissao = declared_attr(lambda cls: relationship(
        'Permissao', backref='PermissaoGrupo',
    ))

    @staticmethod
    def permissoes_com_grupo_sem_match(db):
        """Retorna as permissões (P.uuid, G.uuid) que não possuem
        relacao com grupo correspondente.
        """
        query = db.text("""
            SELECT P.uuid, G.uuid
            FROM Permissao P
            JOIN Grupo G ON
                P.endpoint == G.nome
                AND G.custom == 0
            LEFT JOIN PermissaoGrupo PG ON
                P.uuid == PG.permissao_uuid
                AND G.uuid == PG.grupo_uuid
            WHERE
                P.custom == 0
                AND P.excludo == 0
                AND PG.uuid IS NULL
            """)
        return db.session.execute(query).fetchall()

    @staticmethod
    def gerar_relacoes(cls, db):
        """Gera as relações entre permissão e grupo."""
        for match in cls.permissoes_com_grupo_sem_match(db):
            permissao_grupo = cls(
                permissao_uuid=match[0],
                grupo_uuid=match[1],
            )
            permissao_grupo.add(db)
        db.session.commit()
