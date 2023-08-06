import os
from setuptools import setup


def listar_subpastas(diretorio):
    subpastas = [diretorio]
    for nome in os.listdir(diretorio):
        caminho = os.path.join(diretorio, nome)
        if os.path.isdir(caminho):
            subpastas.append(caminho)
            subpastas.extend(listar_subpastas(caminho))
    return subpastas


with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name='flask-dba',
    version='1.0.0',
    url='https://github.com/feiticeiro-tec/flask_dba',
    license='BSD3',
    author='Silvio Henrique Cruz Da Silva',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='silviohenriquecruzdasilva@gmail.com',
    keywords='Pacote',
    description=(u'Extenção flask para aumento de agilidade'
                 u' no processo de criação de projeto.'),
    packages=listar_subpastas('flask_dba'),

    install_requires=['flask', 'flask-sqlalchemy', 'loguru']
)
