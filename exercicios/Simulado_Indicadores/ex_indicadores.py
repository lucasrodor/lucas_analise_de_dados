
# 1 - Você tem acesso … API do Laboratório de Finanças, que fornece dados do Planilhão em formato JSON. 
# A autenticação ‚ feita via JWT Token no cabeçalho da requisição.
# Acesse a API no endpoint: https://laboratoriodefinancas.com/api/v1/planilhao
# passando como parƒmetro a data do dia de hoje (por exemplo, "2025-09-17").
# Construa um DataFrame pandas a partir dos dados recebidos.
# Selecione a empresa que apresenta o maior ROE (Return on Equity) nessa data.
# Exiba o nome da empresa e o valor do ROE correspondente.

import requests
import pandas as pd

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMjIwMjAzLCJpYXQiOjE3NTg2MjgyMDMsImp0aSI6IjRjMGI2NGFiNDI0MjRmNWViZjc3NzQ4NWI4ODA0MWZiIiwidXNlcl9pZCI6IjQwIn0.1_Hc0r6nEwrGwrp-3Lsqjx5sv-Y3-AnyqwKlSS9VAUU"
headers = {'Authorization': 'JWT {}'.format(token)}

params = {
'data_base': '2025-09-17'
}

response = requests.get('https://laboratoriodefinancas.com/api/v1/planilhao',params=params, headers=headers)
df = pd.DataFrame(response.json()['dados'])
df

roe_maior = df.sort_values(by='roe',ascending=False).head(1)

print(f'A empresa com maior ROE foi a {roe_maior["ticker"].iloc[0]}, com um ROE de {roe_maior["roe"].iloc[0]:.2f}')

# 2 - Acesse a API do Planilh?o e traga os dados de uma data de sua escolha.
# Construa um DataFrame pandas com os dados recebidos.
# Filtre as empresas que pertencem ao setor ?petr¢leo?.
# Elimine todos os registros cujo indicador P/VP (p_vp) seja negativo.
# Selecione a empresa com o maior P/VP dentro do setor de petr¢leo e exiba seu ticker, setor e valor de P/VP.

response2 = requests.get('https://laboratoriodefinancas.com/api/v1/planilhao',params=params, headers=headers)
df2 = pd.DataFrame(response2.json()['dados'])
df2

filtro = (df2['setor'] == 'petróleo') & (df2['p_vp']>0)
df_petroleo = df2.loc[filtro]
df_petroleo_pvp = df_petroleo.sort_values(by='p_vp', ascending=False).head(1)
df_petroleo_pvp = df_petroleo_pvp[['ticker','setor','p_vp']]


# 3 - A API do Laborat¢rio de Finan‡as fornece informa‡?es de balan‡os patrimoniais de empresas listadas na B3.
# Acesse o endpoint: https://laboratoriodefinancas.com/api/v1/balanco
# usando o ticker PETR4 e o per¡odo 2025/2§ trimestre (ano_tri = "20252T").
# O retorno da API cont‚m uma chave "balanco", que ‚ uma lista com diversas contas do balan‡o.
# Localize dentro dessa lista a conta cuja descri‡?o ‚ ?1 - Ativo Total?.
# Exiba o valor correspondente a essa conta.

import requests
token = ""
headers = {'Authorization': 'JWT {}'.format(token)}
params = {'ticker': 'PETR4', 
'ano_tri': '20231T'
}
response3 = requests.get('https://laboratoriodefinancas.com/api/v1/balanco',params=params, headers=headers)
dados = response3.json()['dados'][0]
dados = dados['balanco']

df3 = pd.DataFrame(dados)
df3
filtro = (df3['descricao']=='Ativo Total') & (df3['conta']=='1')
df_final = df3.loc[filtro]["valor"].iloc[0]
print(f'O valor final foi {df_final:.2f}')