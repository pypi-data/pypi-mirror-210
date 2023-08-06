import psycopg2
from os import environ
from sys import exit
from typing import Type
from logging import warning
from pandas import DataFrame
from .Helper import timing,helper_columns

        
@timing
def form_df_tracking(query:str) -> type(DataFrame):
    # teste
    """
        Extrai os dados do RDS, e transforma em pandas object
        ARGS
            query = Query a ser feita
    """
    try:
        engine = psycopg2.connect(
            database = 'postgres',
            user = 'tracking',
            password = environ['SQL_PRD_PASSWORD'],
            host = 'prd-avi-chatbot-tracking-db.clarobrasil.mobi',
            port = '5432',
        )
    except (Exception,psycopg2.Error) as error:
        print(f'''
            Erro na conexão
            {error}
            ''',)
        exit(1)

    cursor = engine.cursor()
    cursor.execute(query) # Executando query, para obtencao de dados
    data = cursor.fetchall() # Pegando esse dados
    cols = helper_columns(cursor = cursor)
    df = DataFrame(data = data, columns = cols)
    if df.empty:
        warning("O seu dataframe esta vazio! Algo está de errado com o seu query")
        exit(0)
    return df
    
@timing
def form_df_extras(df:DataFrame):
    """  
        Explode os extras globais dentro da coluna,
        global_extras_raw
        ARGS
            df = Dataframe base
    """
    new_df = DataFrame(list(df['global_extras_raw']))
    if new_df.empty:
        warning("O seu dataframe esta vazio! Algo está de errado com o seu query")
        exit(0)
    return new_df

