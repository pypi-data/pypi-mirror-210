from pandas import DataFrame
from numpy import nan
from logging import warning, info
from orjson import loads, JSONDecodeError
from .Helper import timing

@timing
def patternizing_columns(extras_df:DataFrame) -> DataFrame:
    """
        Padroniza nome de colunas para lower com underscore
        ARGS
            extras_df com colunas sem nomenclatura correta
        RETURNS
            extras_df com nomenclatura correta
    """
    extras_df.columns = extras_df.columns.str.replace('-','_').str.lower()
    return extras_df

@timing
def ensure_nan_extras(extras_df:DataFrame) -> DataFrame:
    """
        Padronizando valores nulos, e garantindo que coisas como campaing source,hp tenham o mesmo padrao de nulos
        ARGS
            df com valores nulos fora de padrao
        RETURNS
            df com valores nulos dentro do padrao
    """
    extras_df['userphone'] = extras_df.userphone.str.replace('\D*','',regex = True).replace('',nan)
    extras_df['campaign_source'] = extras_df.campaign_source.replace('',nan)

    if 'cpf' in extras_df.columns:
        extras_df['cpf'] = extras_df.cpf.str.replace('\D*','',regex = True).replace('',nan)

    if 'hp' in extras_df.columns:
        extras_df['hp'] = extras_df.hp.str.replace('\D*','',regex = True).replace('',nan)

    if 'postalcode' in extras_df.columns:   
        extras_df['postalcode'] = extras_df.postalcode.str.replace('\D*','',regex = True).replace('',nan)

    return extras_df

@timing
def fill_na_extras(extras_df:DataFrame) -> DataFrame:
    """
        Preenche valores nulos de colunas que nao podem ter nulos
        de acordo com logica de userid.
        ARGS
            Df com valores nulos
        RETURNS
            Df sem valores nulos
    """
    if extras_df['userphone'].isna().any():
        warning('Detectei nulos na coluna userphone do dataframe extras! Formulando tratativa')
        start_na = extras_df['userphone'].isna().sum()
        extras_df['userphone'] = extras_df.groupby('userid',group_keys = False)['userphone'].apply(lambda x : x.bfill().ffill())
        end_na = extras_df['userphone'].isna().sum()
        warning(f'O numero de nulos na coluna userphone foi de {start_na} para {end_na}')

    if extras_df['campaign_source'].isna().any():
        warning('Detectei nulos na coluna campaign_source! Formulando tratativa')
        start_na = extras_df['campaign_source'].isna().sum()
        extras_df['campaign_source'] = extras_df.groupby('userphone',group_keys = False)['campaign_source'].apply(lambda x : x.bfill().ffill())
        end_na = extras_df['campaign_source'].isna().sum()
        warning(f'O numero de nulos na coluna campaign_source foi de {start_na} para {end_na}')

    if 'origin_link' in extras_df.columns:
        extras_df['origin_link'] = extras_df.groupby(['userid','campaign_source',],group_keys = False)['origin_link'].apply(lambda x : x.bfill().ffill())

    return extras_df

@timing
def dtype_extras(extras_df:DataFrame) -> DataFrame:
    """
        Funcao que deixa dtypes dos extras no datatype correto.
        Semelhante a dtype_tracking só que embasada na tabela extras criada
        Ele tem um mapa geral porque as vezes nao vamos ter todos os extras globais
        nos eventos.
    """
    general_map = {'userphone':str,
                'cpf':str,
                'city':str,
                'state':str,
                'postalcode':str,
                'laststate':str,
                'userid':str,
                'completed_address':str,
                'type_of_person':str,
                'origin_link':str,
                'api_orders_hash_id':str,
                'campaign_source':str,
                'type_of_product':str,
                'data_change':str,
                'redemption_passage':'bool',
                'hp': str,
                'provider_message':str,
                'payment':str,
                'email':str,
                'due_date':str,
                'full_name':str,
                'address_complement_path':str,
                'complement_non_identified':str,
                'chosen_product':str,
                'bank':str,
                'bot_origin':str,
                'onboarding_simplified':'bool',
                'bot_id':str,
                'main_installation_date':str,
                'alternative_installation_date':str,
                'main_installation_period_day':str,
                'alternative_installation_period_day':str,
                'type_of_instalation':str,
                'redemption_laststate':str,
                'ticket_id':str,
                'userphone_plus':str,
                'incentive_redirection':str,
                'api_customercontracts_error':str,
                'api_homepassed_error':str,
                'plan_offer':str,
                'plan_name':str,
                'plan_value':str,
                'api_assine_error':str,
                'incentive_redirection':str,
                'plan_value':str,
                'plan_offer':str,
                'plan_name':str,
                'plan_discount_value':str,
                'additional_point':str,
                'type_of_documentation':str,
                'plan_discount_name':str,
                'plan_discount_name':str,
                'plan_discount_value':str,
                'additional_lines':str,
                'affiliatedid':str,
                'given_number':str,
                'age':str,
                'type_of_discount':str
                }
    dtypes = {}
    # Mapa dos dtypes do dataframe atual
    for k in list(extras_df.columns):
        try:
            dtypes[k] = general_map[k]
        except KeyError as error:
            warning(f'O general map de datatypes precisa ser atualizado com a seguinte extra {k}')
            warning("Nesse handler irei converter a coluna sem datatype para str")
            extras_df[k] = extras_df[k].astype('string')
    extras_df = extras_df.astype(dtype = dtypes)
    return extras_df


