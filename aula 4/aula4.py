import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ===============================================

file = "C:\\Users\\lucas\\IBMEC\\programacao_para_analise_de_dados_2025.2\\data\\cadastro_alunos.xlsx"
df1 = pd.read_excel(file)
filtro = df1['nome_aluno'].str.contains("^a", case = False)
df1.loc[filtro]

# ===============================================

url2 = "http://www.ipeadata.gov.br/api/odata4/Metadados"
response = requests.get(url2)
metadados = response.json()
metadados = metadados["value"]
df = pd.DataFrame(metadados)
filtro = df['SERNOME'].str.contains('IPCA - educação, leitura e papelaria - taxa de variação', case = False)
df.loc[filtro, ['SERNOME']].values
df.loc[filtro]

SERCODIGO = "PRECOS12_IPCAED12"
url1 = f"http://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO = '{SERCODIGO}')"
response = requests.get(url1)
dados = response.json()
dados = dados['value']
df_dados = pd.DataFrame(dados)
df_dados['VALDATA'] = pd.to_datetime(df_dados['VALDATA'], errors = 'coerce')
df_dados[['VALDATA','VALVALOR']].plot()

# ===============================================

import requests

uri = 'https://api.football-data.org/v4/matches'
headers = { 'X-Auth-Token': '28461ba496ad4610aa93688b3a28621c' }

response = requests.get(uri, headers=headers)
dados1 = response.json()
dados1 = dados1['matches']
df_fut = pd.DataFrame(dados1)
df_fut


