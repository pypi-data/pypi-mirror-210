import sqlalchemy
from pandas import DataFrame
from typing import Type
from functools import wraps
from time import time
from logging import info,warning
from numpy import nan
from orjson import loads
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import UnicodeText


def timing(f):
    # Decorator simples para medir tempo de excecucao de funcao
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        warning(f'Funcao {f.__name__} demoro {te-ts:2.4f} segundos')
        return result
    return wrap

def helper_columns(cursor:Type) -> Type:
    # Funcao simples para extracao de nomenclatura de colunas
    # Para formar dataframe
    cols = []
    for col in cursor.description:
        cols.append(col[0])
    return cols

def map_substring(s, dict_map) -> dict:
    """
        Funcao helper mapeia as sub strings com facilidade
        ARGS
            s = pd.Series a ser interada por
        RETURNS
            dict_map = mapa se substrings
    
    """
    for key in dict_map.keys():
        if key in s: 
            return dict_map[key]
    return nan

def sqlcol(df:DataFrame) -> dict:
    """
        Funcao que mapeia os datatype das tabelas e retorna o datatype adequado do SQLalchemy
        ARGS
            df, para acessar os objetos de colunas e datatypes
    """
    info("Formulando dict_map de datatype SQLalchemy")

    valid_json_b = ['global_extras_raw','plan_value','plan_name','plan_offer']

    dtypedict = {}
    for i,j in zip(df.columns, df.dtypes):
        if i in valid_json_b:
            dtypedict.update({i: JSONB(astext_type=UnicodeText)})
            continue
            # Depois adicionar colunas a mais
        if 'object' in str(j):
            dtypedict.update({i: sqlalchemy.types.VARCHAR()})     
        if "datetime" in str(j):
            dtypedict.update({i: sqlalchemy.types.DateTime()})
        if "float" in str(j):
            dtypedict.update({i: sqlalchemy.types.Float(precision=3, asdecimal=True)})
        if "int" in str(j):
            dtypedict.update({i: sqlalchemy.types.INT()})

    warning(f"Segue dicionario de datatypes{dtypedict}")
    return dtypedict


def try_to_deserialize_json(x) -> str:
    """
        Pega celulas unicas transforma elas para string caso elas estejam em formato json caso nao
        Transforma elas, em string
        ARGS
            X = CelulaS com possibiidade json
        RETURNS
            Celula em formato str
    """
    try:
        x = str(x)
    except:
        info(f"O seguinte valor {x} veio como json, e nao foi convertido para string corretamente")
    return x

@timing
def json_deserializer(df:DataFrame) -> DataFrame:
    """
        1- Transformar elas em string
        2- Repassar elas como datatype json
        ARG
            Dataframe com jsons em formato dict
        RETURNS
            Dataframe com json em formato string
    """
    valid_json_columns = ['global_extras_raw','plan_value','plan_name','plan_offer']

    for series in valid_json_columns:
        try:
            df[series] = df[series].apply(try_to_deserialize_json)
        except KeyError as e:
            warning(f"A coluna {series} nao foi achada, nao vou transformar em string!" )
    return df

