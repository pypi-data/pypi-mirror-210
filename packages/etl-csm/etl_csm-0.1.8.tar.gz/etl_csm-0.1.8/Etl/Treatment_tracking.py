from logging import warning,info
from numpy import nan,where
from pandas import Timedelta,Series, DataFrame
from unidecode import unidecode
from .Helper import timing

@timing
def fill_na_tracking(df:DataFrame)-> DataFrame:
    """
        Funcao feita para garantir que as colunas que são supostas, serem númericas realmente estarem em formato númerico. Tambem verifica se tem valores nulos.
        ARGS
            dataframe suja
        RETURNS
            dataframe tratada
    """
    df['user_phone'] = df.user_phone.str.replace('\D*','',regex = True).replace('',nan)
    warning("Retirando poluicao de dados na coluna user_phone de trackings e substituindo '' por nan objects")

    df['original_user_id'] = df.original_user_id.replace('',nan)
    warning("Substituindo valores '' por nan objects na coluna original_user_id")

    if df['user_phone'].isna().any():
        warning('Detectei nulos na coluna userphone! Formulando tratativa')
        evid = df.loc[df['user_phone'].isna()][['user_phone','category','queued_date_service']].head().to_dict()
        warning(f'Segue evidencias de telefone nulos: {evid}')

        start_na = df['user_phone'].isna().sum()
        df['user_phone'] = df.groupby('original_user_id',group_keys = False)['user_phone'].apply(lambda x : x.bfill().ffill())
        end_na = df['user_phone'].isna().sum()
        warning(f'O numero de nulos na coluna user_phone foi de {start_na} para {end_na}')

    if df['original_user_id'].isna().any():
        warning('Detectei nulos na colunas original_user_id! Formulando tratativa! Já que essa coluna é a base de identificacao de user isso é um erro grave')
        evid = df.loc[df['original_user_id'].isna()][['user_phone','category','queued_date_service']].head().to_dict()
        warning(f'Segue evidencias: {evid}')

    return df

@timing
def dtype_tracking(df:DataFrame) -> DataFrame:
    """
        Tratando os dtypes para que eles estejam bonitinhos,em relacao a memoria, utilizada evitando custos! Em layer.
        ARGS
            dataframe suja
        RETURNS
            dataframe tratada
    """
    dtypes= {
        'chatbot_id':str,
        'user_phone':str,
        'category':str,
        'action':str,
        'suffix':str,
        'original_user_id':str,
        'queued_date_service':'datetime64[ns]',
        'id':str,# Alterar no futuro
    }
    new_df = df.astype(dtype = dtypes)
    return new_df

@timing
def remove_test(df:DataFrame) -> DataFrame:
    """
        Funcao que remove users teste (testes joga fora)
        ARGS
            Dataframe com testes
        RETURNS
            Dataframe sem testes
    """
    testers = { 
                'Adriano': '11989999375',
                'Bruno': '13981074058', 
                'Maicon Veiga': '11969309352',
                'Jessica Varçal': '11970325152',
                'Ana Flávia Dumo': '11997842525', 
                'Sabrina Augusta': '11971565507', 
                'Salvo Menezes': '11980602111',
                'Sueli Maria': '11999171150', 
                'Leticia Dominique': '11984435186', 
                'Sueli Ferreira': '11941606552', 
                'Joana Sargo': '351910191617', 
                'Ingrid Lemos': '11987361937', 
                'Harrison Pompilha': '11982454209', 
                'Jefferson Andrade': '11986226831', 
                'Renan': '11943615412',
                'Ana Portillo': '11995879008',
                'Rafael Rodrigues': '11986705117', 
                'Andréia Lorenzoni': '11949855198',
                'Lucas Paixão': '11956075838',
                'Alexandre Pavaneli': '17997472596',
                'Murillo Nozue': '11994117676', 
                'Thiago Rasquino': '11981333149', 
                'Luis Henrique': '11986309778', 
                'Guilherme Garcia': '11984738427', 
                'Gabriel Brandao': '11940667922', 
                'Diego Coutino': '21981025516', 
                'Cintia Oliveira': '11997061023', 
                'Anderson Martins': '11974029844',
                'Alline': '11983842161', 
                'Vinicius Tirello': '34996473073', 
                'Bruna Minnicelli': '11991680459',
                'Guilherme Rapicham':'43999264449'
            }
    filt = df['user_phone'].isin(testers.values())
    if df.loc[filt].empty:
        warning('Nenhum teste foi encontrado!')
        return df
    df = df.loc[~filt].reset_index(drop = True)
    if df.empty:
        raise Exception('Acho que o seu dataframe so tinha user teste ae acabou ficando vazio!')
    return df

@timing
def flag_duplicated_tracks(df:DataFrame) -> DataFrame:
    """
        Cria coluna timediff e verifica se houve trackings repetidos num periodo de menos que um segundo
        Somente valído para view origin trackings
        ARGS
            Dataframe
        RETURNS
            None
    """
    df = df.sort_values(by ='queued_date_service').reset_index(drop = True)
    df['timediff'] = (df['queued_date_service'] - df['queued_date_service'].shift())
    df['tracking'] = df['category'] + ' ' + df['suffix']

    filt = (df['timediff'] < Timedelta(seconds = 1)) & (df['suffix'].isin(['origin','view']))
    temp_df = df[['user_phone','timediff','tracking','suffix']].loc[filt]
    flagger = ((temp_df
            .groupby('user_phone')['tracking']
            .transform(lambda x: where(x.eq(x.shift())| x.eq(x.shift(-1)), True, False))))

    if flagger.fillna(False).any():
        warning('Temos trackings duplicado passar amostra para dev!')
        warning(f'Segue evidencias:{temp_df.loc[flagger.fillna(False)].head().to_dict()}')

@timing
def create_dates(df:DataFrame) -> DataFrame:
    """
        Cria coluna de data e deixa no datatype ideal
        ARGS
            Dataframe sem data
        RETURN 
            Dataframe com data
    """
    df['date'] = df['queued_date_service'].dt.date.astype('datetime64[ns]')

    return df

@timing
def remove_unecessary_trackings(df:DataFrame) -> DataFrame:
    """
        Remove trackings de decision tree desnecessarios
        ARGS
            Dataframe com decision-tree trackings
        RETURN
            Dataframe sem decision-tree trackings
        AVISO:
            Pode incrementar de acordo com o bot
    """

    df = df.loc[~df['category'].str.startswith('decision')].reset_index(drop = True)

    return df

@timing
def clean_action(df:DataFrame) -> DataFrame:
    """
        Ira fazer a remocao de acentos e \t charaters da coluna new action
        tambem ira deixar todo mundo em lower
        ARGS
            Dataframe com action sujo
        RETURN
            Dataframe com action limpa
    """
    df['action'] = df['action'].apply(lambda x : unidecode(x)).str.replace(r'\t|\r|\n','',regex = True)
    return df