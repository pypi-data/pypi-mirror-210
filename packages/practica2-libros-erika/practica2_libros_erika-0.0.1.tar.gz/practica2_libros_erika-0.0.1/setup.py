import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.1'
PACKAGE_NAME = 'practica2_libros_erika'
AUTHOR = 'García Márquez Erika Araceli'
AUTHOR_EMAIL = 'erika_gm1@tesch.edu.mx'
URL = ''

LICENSE = 'MIT'
DESCRIPTION = 'Es la Practica 2 del segundo parcial en Topicos Avanzados de programación del grupo 44-71, escuela TESCha'

#Paquetes necesarios para que funcione la libreía. Se instalarán a la vez si no lo tuvieras ya instalado
INSTALL_REQUIRES = [
        'libros'
]
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)