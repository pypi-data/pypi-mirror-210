from pandas import Series
from numpy import nan
from logging import info,warning
from .Helper import map_substring, timing

# Tratamnetos da residencial

@timing
def steps_residential(s:Series) -> Series:
    """
    Formula coluna steps de acordo com a coluna suffix
    s =  suffix series
    """
    unstepped_trackings = []
    st = []
    for i in s:
        if 'onbo' in i:
            if 'start' in i:
                st.append('1-Onboarding + Retorno')
            elif 'segment' in i:
                st.append('1.1-Opcional-Onboarding escolha de bot')
            else:
                st.append(nan)
        elif 'product-availability' in i:
            if 'cpf-request' in i:
                st.append('3-Informa localizacao e cpf')
            elif 'cpf-validation' in i:
                st.append('3.1-CPF valido (V.2.0)')
            elif 'health-api-orders-validation' in i:
                st.append('3.2-Consulta orders (V.2.1.1)')
            elif 'api-residential-customer-contracts-open-request-validation' in i:
                st.append('3.3-Consulta customer contracts (V.2.1.2)')
            elif 'postalcode-request' in i:
                st.append('3.4-Obtencao de CEP')
            elif 'postalcode-validation' in i:
                st.append('3.5-CEP valido (V.2.2)')
            elif 'postalcode-validation-true' in i:
                st.append('3.6-Pegando complemento')
            elif 'health-api-address-validation' in i:
                st.append('3.7-Endereco sendo validado (V.2.3)')
            elif 'empty-public-space-validation' in i:
                st.append('3.8-Validacao de logradouro (V.2.4)')
            elif 'empty-neighborhood-validation' in i:
                st.append('3.9-Bairro sendo validado (V.2.3)')
            elif 'address-confirmation' in i:
                st.append('3.9.1-Endereco resumido')
            elif 'health-api-residential-customer-contracts-validation' in i:
                st.append('3.9.2-Consulta de CPF na api de base (V.2.9)')
            elif 'client-validation' in i:
                st.append('3.9.3-Localizado na api de base validacao (V.2.10)')
            elif 'product-availability-validation' in i:
                st.append('3.9.4-Produto e disponibilizado na regiao (V.2.11)')
            elif 'health-api-plan-availability-validation' in i:
                st.append('3.9.5-Consulta na api de catalogos(V.2.13)')
            elif 'plans-available-catalog-validation' in i:
                st.append('3.9.6-Plano disponivel no catalogo (V.2.14)')
            else:
                st.append(nan)
        elif 'plan-selection' in i:
            st.append('4-Escolhe plano (Todos produtos)')
        elif 'registration' in i:
            if 'full-name-request' in i:
                st.append('5-Realiza cadastro')
            elif 'name-validation' in i:
                st.append('5.1-Consulta nome valido (V.4.0)')
            elif 'email-request' in i:
                st.append('5.2-Requisicao de email')
            elif 'e-mail-validation' in i:
                st.append('5.3-Consulta email valido (V.4.1)')
            elif 'birth-date-request' in i:
                st.append('5.4-Idade do usuario')
            elif 'birth-date-validation' in i:
                st.append('5.5-Idade do usuario validacao (V.4.2)')
            elif 'birth-date-out-of-range-validation' in i:
                st.append('5.6-Idade do usuario elegibilidade (V.4.3)')
            elif 'identity-number-request' in i:
                st.append('5.7-Pedido de RG')
            elif 'identity-number-validation' in i:
                st.append('5.8-Pedido de RG (V.4.4)')
            elif 'mother-name-request' in i:
                st.append('5.9-Pedido de nome da mae')
            elif 'mother-name-validation' in i:
                st.append('5.9.1-Pedido de nome da mae validation (V.4.5)')
            elif 'additional-phone-number-confirmation' in i:
                st.append('5.9.2-Numero adicional')
            elif 'register-data-confirmation' in i:
                st.append('5.9.3-Confirmacao de data')
            elif 'address-complement-insert-confirmation' in i:
                st.append('6-Informa Complemento')
            elif 'address-complement-confirmation' in i:
                st.append('6.1-Complemento confirmado')
            else:
                st.append(nan)
        elif 'payment' in i:
            if 'invoice-sending-confirmation' in i:
                st.append('7-Metodo de pagamento')
            elif 'invoice-due-date-options' in i:
                st.append('7.1-Escolhe dia de vencimento')
            elif 'payment-method-confirmation-options' in i:
                st.append('7.2-Escolhe forma de pagamento')
            elif 'register-data-confirmation' in i:
                st.append('7.3-Confirma dados')
            else:
                st.append(nan)
        elif 'schedule start' in i:
            st.append('8-Agendamento de instalacao')
        elif 'checkout' in i:
            if 'order-details-confirmation' in i:
                st.append('9-Realiza pedido')
            elif 'order-validation' in i:
                st.append('9.1-Cascata de api (V.F.0)')
            elif 'order-placed' in i:
                st.append('9.2-Finalizado')
            else:
                st.append(nan)
        elif 'error' in i:
            st.append('Horizontal-erros-gerais')
        elif 'human-handoff' in i:
            st.append('Horizontal-Transbordo')
        elif 'decision-tree' in i:
            st.append('Horizontal-Cascatas')
        elif 'feedback' in i:
            st.append('Horizantal-Feedback')
        else:
            unstepped_trackings.append(i)
            st.append(nan)
    if any([i is not nan for i in unstepped_trackings]):
        warning('Voce tem trackings sem steps! Para ver quais são verificar lista unstepped_trackings :)')
    return Series(st).astype(str)

@timing
def errors(s:Series) -> Series:
    """
    Formula coluna de erros
    """
    e = []
    for i in s:
        if 'error' in i:
            if 'unexpected-video' in i:
                e.append('Erro video')
            elif 'unexpected-image' in i:
                e.append('Erro imagem')
            elif 'unexpected-audio' in i:
                e.append('Erro audio')
            elif 'unexpected-file' in i:
                e.append('Erro arquivo')
            elif 'unexpected-cpf' in i:
                e.append('Erro persistente CPF')
            elif 'generic' in i:
                e.append('Erro generico')
            elif 'api' in i:
                e.append('Erro generico API')
            elif 'last-state-unidentified' in i:
                e.append('Erro estado inexistente')
            elif 'bob' in i:
                e.append('Erro Bob')
            else:
                e.append(nan)
        else:
            e.append(nan)
    if any([i is not nan for i in e]):
        info('Aviso: Tivemos erros no bot :(')
    return Series(e).astype(str)

# Tratamento de pme
@timing
def steps_pme(s:Series) -> Series:
    """
    Semelhante a steps mas mais generalizada
    Aviso: Somente utilizar em bots novos
    ARGS
    s = pd.Series category do dataframe tracking
    """
    product_map = {
        'identify': '1-Identifica prospect e endereco',
        'plan-selection':'2-Escolhe plano',
        'registration':'3-Realiza cadastro',
        'payment':'4-Define metodo de pagamento',
        'schedule':'5-Agenda instalacao',
        'checkout':'6-Finaliza pedido'
    }
    
    s = s.apply(lambda x : map_substring(x, product_map)).astype('string')
    return s