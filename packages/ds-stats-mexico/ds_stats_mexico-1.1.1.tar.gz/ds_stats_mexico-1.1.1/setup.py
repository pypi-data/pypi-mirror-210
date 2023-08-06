import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '1.1.1'
PACKAGE_NAME = 'ds_stats_mexico'
AUTHOR = 'DavichoStar'
AUTHOR_EMAIL = 'davichostar@protonmail.com'
URL = 'https://github.com/DavichoStar'

LICENSE = 'MIT'
DESCRIPTION = 'Librería de estadística (Gráficas) de México (Paises ricos, envejecimiento, mortalidad infantil)'
LONG_DESCRIPTION = (HERE / "ds_stats_mexico" / "README.md").read_text()

# Paquetes necesarios para que funcione la libreía. Se instalarán a la vez si no lo tuvieras ya instalado
INSTALL_REQUIRES = [
    'matplotlib'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',  # Este es importante para que se muestre bien el README.md
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)