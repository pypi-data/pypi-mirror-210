# Pacote para ter acesso a funcoes de tratamento e extracao de dados RDS
* Aqui se localiza a biblioteca etl
* Joguei ele para um pacote para facilidade de importação e aproveitamento de classes de limpeza
* Aviso nao instale etl-csm aqui
# Como instalar a biblioteca?
* pip install etl-csm
* Pronto
# Configuração de ambiente?
* As demandas do ambiente local localizam-se na environment.yml
* As demandos do ambiente cloud localizam-se no serverless.yml.
# Links importantes
## Verificação de testes realizados na lambda apos subir a pipeline
* https://us-east-1.console.aws.amazon.com/lambda/home?region=us-east-1#/functions/etl-pet-csm?tab=code
## Pipeline
* https://jenkins.clarobrasil.mobi/view/ChatBot/job/csm-etl/job/pet/
## Logs de testes
* https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fetl-pet-csm
batatatatata