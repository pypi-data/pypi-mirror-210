from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.1.8'
DESCRIPTION = 'Pacote de ETL'

# Setting up
setup(
    name = "etl_csm",
    version = VERSION,
    author = "ingloriamori",
    author_email = "francisco.froes@globalhitss.com.br",
    description = DESCRIPTION,
    long_description = 'Biblioteca para aproveitar classes de tratamento CSM, direcionada para pet',
    packages = find_packages(),
    url = 'https://gitdev.clarobrasil.mobi/vendas-claro/csm/etl',
    keywords = ['python', 'etl'],
    license = 'MIT',
    install_requires = ['numpy', 'pandas', 'orjson','SQLAlchemy','psycopg2-binary','undefined'],
    extras_require = {
        'dev':['twine>=4.0.2'],
    },
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
    ],
    python_requires = '>=3.9'
)