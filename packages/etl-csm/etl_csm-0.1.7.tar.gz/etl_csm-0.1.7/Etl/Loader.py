import psycopg2
import sqlalchemy.exc
from os import environ
from re import findall
from logging import info, warning
from sqlalchemy import create_engine
from pandas import DataFrame
from .Helper import timing,sqlcol

@timing
def load_cloud(df:DataFrame,bot:str) -> None:
    """
    1- Ira fazer o processo de carregamento para o RDS.
    2- Ira inserir com os datatypes corretos
    3- Em seu exception irá acrescentar a coluna com o datatype varchar faltante para nao quebra toda vez que um extra global e lancado
    ARGS
        df = pd.DataFrame
        bot = Bot que irá ser carregado
    """
    engine_alchemy = create_engine(f"postgresql://tracking:{environ['SQL_PRD_PASSWORD']}@prd-avi-chatbot-tracking-db.clarobrasil.mobi:5432/clean_data")
    tries = 15
    sql_dict = sqlcol(df)
    for _ in range(tries):
        try:
            df.to_sql(f'{bot}_tracking_treated',engine_alchemy,if_exists = 'append',dtype = sql_dict,index = False,chunksize = 10000)
            break
        except sqlalchemy.exc.ProgrammingError as error:
                warning(f"Tivemos um erro {error}")
                if isinstance(error.orig, psycopg2.errors.UndefinedColumn):
                    warning("Vou executar um handler para ver se consigo resolver!")         
                    engine = psycopg2.connect(
                        database = 'clean_data',
                        user = 'tracking',
                        password = environ['SQL_PRD_PASSWORD'],
                        host = 'prd-avi-chatbot-tracking-db.clarobrasil.mobi',
                        port = '5432',
                    )
                    cursor = engine.cursor()
                    column = findall('"(.*?)"',str(error))[0]
                    warning(f"Tive que acrescentar mais uma coluna ao seu dataframe ja existente a coluna foi {column}")
                    query = f"""
                    ALTER TABLE {bot}_tracking_treated
                    ADD COLUMN {column} VARCHAR NULL;
                    """
                    info(query)
                    cursor.execute(query)
                    engine.commit()
                    tries -= 1
                else:
                    warning("Erro severo sem exception handling no load_cloud!")
        # Sempre fazer esse commit pelo amor
