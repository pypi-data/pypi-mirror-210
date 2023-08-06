from pandas import concat, DataFrame
from logging import basicConfig, INFO, DEBUG
from .Extrator import form_df_tracking, form_df_extras
from .Treatment_tracking import (fill_na_tracking, dtype_tracking, remove_test,
                                 remove_unecessary_trackings, flag_duplicated_tracks, 
                                 create_dates, clean_action)
from .Treatment_extras import (patternizing_columns, ensure_nan_extras, dtype_extras,
                                 fill_na_extras)
from .Unique_treatments import steps_residential, errors, steps_pme
from .Helper import timing, json_deserializer
from .Loader import load_cloud

class Runner:
    #batatatatata
    """
        Runner é a classe que executa todo o conjunto de funcoes de tratamento.
        Ele tambem inicializa o processo de logs
        ARGS:
            query = String que representa um SQL query valido  
    """
    def __init__(self,query:str,bot:str) -> None:
        if bot:
            self.bot = bot
            self.query = query
            basicConfig(filename='etl.log',filemode='w',level= DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')
        else:
            raise Exception("Para poder rodar essa classe repasse um bot, corparate/residential")

    def etl_df(self):
        """
            Funcao que roda ETL do dataframe tracking,
            nao arquiva em memoria o dataframe extras_df
        """ 
        df = form_df_tracking(self.query) #1
        df = fill_na_tracking(df) #2
        df = remove_test(df) #3 Não se pode remover testes no ambiente de teste porque senao você remove todo mundo
        flag_duplicated_tracks(df) #4
        df = dtype_tracking(df) #5
        df = create_dates(df) #6
        df = remove_unecessary_trackings(df) #7
        df = clean_action(df) #8
        df['steps'] = steps_residential(df['category']) #9
        df['errors'] = errors(df['category']) #10
        return df

    def etl_extras_df(self,df:DataFrame) -> DataFrame:
        """
            Funcao que forma o dataframe de extras
            e os trata
        """
        extras_df = form_df_extras(df) #1
        extras_df = patternizing_columns(extras_df) #2
        extras_df = ensure_nan_extras(extras_df) #3
        extras_df = fill_na_extras(extras_df) #4 
        extras_df = dtype_extras(extras_df) #5
        return extras_df

    def etl_df_pme(self):
        df = form_df_tracking(self.query) #1
        df = fill_na_tracking(df) #2
        df = remove_test(df) #3 Não se pode remover testes no ambiente de teste porque senao você remove todo mundo
        flag_duplicated_tracks(df) #4
        df = dtype_tracking(df) #5
        df = remove_unecessary_trackings(df) #6
        df['steps'] = steps_pme(df['category']) #7
        df['errors'] = errors(df['category']) #8
        return df

    def etl_extras_df_pme(self,df:DataFrame) -> DataFrame:
        extras_df = form_df_extras(df) #1
        extras_df = patternizing_columns(extras_df) #2
        extras_df = ensure_nan_extras(extras_df) #3 
        extras_df = fill_na_extras(extras_df) #4 
        extras_df = dtype_extras(extras_df) #5 
        return extras_df
    
    def run(self) -> None:
        if self.bot == 'residential':
            df = self.etl_df()
            extras_df = self.etl_extras_df(df)
            df = concat([df,extras_df],axis = 1)
            df = json_deserializer(df)
            load_cloud(df,self.bot)
        if self.bot == 'corporate':
            df = self.etl_df_pme()
            extras_df = self.etl_extras_df_pme(df)
            df = concat([df,extras_df],axis = 1)
            df = json_deserializer(df)
            load_cloud(df,self.bot)

