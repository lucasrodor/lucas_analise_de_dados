# O dataset NCR Ride Bookings contém registros de corridas urbanas realizadas em regiões da National Capital Region (NCR), que abrange Delhi, Gurgaon, Noida, Ghaziabad, Faridabad e áreas próximas.
# Utilize os arquivos : ncr_ride_bookings.csv e ncr_ride_regions.xlsx para resolver as questoes.
# Principais informaçoes no dataset:
# Date → Data da corrida
# Time → Horário da corrida
# Booking ID → Identificador da corrida
# Booking Status → Status da corrida
# Customer ID → Identificador do cliente
# Vehicle Type → Tipo de veículo
# Pickup Location → Local de embarque
# Drop Location → Local de desembarque
# Booking Value → Valor da corrida
# Ride Distance → Distância percorrida
# Driver Ratings → Avaliação do motorista
# Customer Rating → Avaliação do cliente
# Payment Method → Método de pagamento

import pandas as pd
import requests
import matplotlib.pyplot as plt

df_regioes = pd.read_excel(r'C:\Users\lucas\IBMEC\programacao_para_analise_de_dados_2025.2\data\ncr_ride_regioes.xlsx')
df_booking = pd.read_csv(r'C:\Users\lucas\IBMEC\programacao_para_analise_de_dados_2025.2\data\ncr_ride_bookings.csv')

# 1 - Quantas corridas estão com Status da Corrida como Completada ("Completed") no dataset? 
filtro = df_booking['Booking Status']=='Completed'
df_completadas = df_booking.loc[filtro]
df_completadas.shape

print(f'Existem {df_completadas.shape[0]} corridas com o status como "Complete"')

# 2 - Qual a proporção em relação ao total de corridas?
total_corridas = df_booking.shape[0]
corridas_completas = df_completadas.shape[0]

proporcao = corridas_completas/total_corridas

print(f'A proporção de corridas completas em relação ao total é de {proporcao:.2f}, ou seja, {proporcao*100:.0f}%')

# 3 - Calcule a média e mediana da Distância percorrida por cada Tipo de veículo.
tipo_veiculo = df_booking['Vehicle Type'].unique()

distancia_media = df_booking.groupby('Vehicle Type')['Ride Distance'].mean()
distancia_mediana = df_booking.groupby('Vehicle Type')['Ride Distance'].median()

# 4 - Qual o Metodo de Pagamento mais utilizado pelas bicicletas ("Bike") ?

df_bike = df_booking[df_booking['Vehicle Type'] == 'Bike']
metodo_pagamento = df_bike.groupby('Payment Method')['Vehicle Type'].count()
qtd_upi = metodo_pagamento[3]

print(f'O método de pagamento mais utilizado pela Bike foi o UPI, sendo utlizado {qtd_upi} vezes')


# 5 - Faca um merge com ncr_ride_regions.xlsx pela coluna ("Pickup Location") para pegar as regioes das corrifas.
# e verifique qual a Regiao com o maior Valor da corrida?

df_novo = pd.merge(df_regioes, df_booking , on = 'Pickup Location', how = 'left')

maior_valor = df_novo.sort_values(by='Booking Value', ascending= False).head(1)
print(f'''A região que teve a corrida com maior valor foi a região {maior_valor['Regiao'].iloc[0]}
Uma corrida no valor de ${maior_valor['Booking Value'].iloc[0]:.2f}''')

# 6 - O IPEA disponibiliza uma API pública com diversas séries econômicas. 
# Para encontrar a série de interesse, é necessário primeiro acessar o endpoint de metadados.
# Acesse o endpoint de metadados: "http://www.ipeadata.gov.br/api/odata4/Metadados"
# e filtre para encontrar as séries da Fipe relacionadas a venda de imoveis (“venda”).
# Dica Técnica, filtre atraves das coluna FNTSIGLA: df["FNTSIGLA"].str.contains() 
# e depois SERNOME: df["SERNOME"].str.contains() 

url_ipea = f'http://www.ipeadata.gov.br/api/odata4/Metadados'
r4 = requests.get(url_ipea)
metadados = r4.json()
metadados = metadados['value']
df = pd.DataFrame(metadados)
df_fipe = df[df["FNTSIGLA"].str.contains('Fipe.*',regex=True, case=False)]
df_fipe[df_fipe["SERNOME"].str.contains("venda", regex=True, case=False)]

# Descubra qual é o código da série correspondente.
# Usando o código encontrado, acesse a API de valores: f"http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{CODIGO_ENCONTRADO}')"
# e construa um DataFrame pandas com as datas (DATA) e os valores (VALVALOR).

SERCODIGO = "FIPE12_VENBR12"
url_ipea2 = f"http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{SERCODIGO}')"
response = requests.get(url_ipea2)
data = response.json()['value']

# Converta a coluna de datas para o formato adequado (pd.to_datetime())
df_data = pd.DataFrame(data)
df_data = df_data[['VALDATA', 'VALVALOR']]
df_data["VALDATA"] = pd.to_datetime(
    df_data["VALDATA"], utc=True, errors="coerce")
df_data["VALDATA"] = df_data["VALDATA"].dt.tz_convert("America/Sao_Paulo")
df_data["DATA"] = df_data["VALDATA"].dt.date
df_data = df_data[['DATA', 'VALVALOR']]
df_data

# 7 -  Monte um gráfico de linha mostrando a evolução das vendas ao longo do tempo.
# Dica: você pode usar a biblioteca matplotlib para gerar o gráfico.
plt.figure(figsize=(12, 6))
plt.plot(df_data["DATA"], df_data["VALVALOR"])
plt.title("Valor da venda de imóveis tabela FIPE")
plt.xlabel("Ano")
plt.ylabel("Valor (R$)")
plt.grid(True)
plt.show()



# 8 - Crie o grafico do bitcoin (ticker: "btc") atraves da api preco-diversos
# Pegue o periodo compreendido entre 2001 a 2025

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMjIwMjAzLCJpYXQiOjE3NTg2MjgyMDMsImp0aSI6IjRjMGI2NGFiNDI0MjRmNWViZjc3NzQ4NWI4ODA0MWZiIiwidXNlcl9pZCI6IjQwIn0.1_Hc0r6nEwrGwrp-3Lsqjx5sv-Y3-AnyqwKlSS9VAUU"
headers = {'Authorization': 'Bearer {}'.format(token)}
params = {
'ticker': 'btc',
'data_ini': '2001-01-01',
'data_fim': '2025-09-24'
}
response = requests.get('https://laboratoriodefinancas.com/api/v1/preco-diversos', params=params, headers=headers)
df_precos = pd.DataFrame(response.json()['dados'])
df_precos
df_precos.columns

# Monte um gráfico de linha mostrando a evolução do preco de fechamento
plt.figure(figsize=(12, 6))
plt.plot(df_precos["data"], df_precos["fechamento"])
plt.title("Evolução do preço do Bitcoin ao longo dos anos")
plt.xlabel("Ano")
plt.ylabel("Preço (R$)")
plt.grid(True)
plt.show()


# 9 - Você tem acesso à API do Laboratório de Finanças, que fornece dados do Planilhão em formato JSON. 
# A autenticação é feita via JWT Token no cabeçalho da requisição.
# Acesse a API no endpoint: https://laboratoriodefinancas.com/api/v1/planilhao
# passando como parâmetro a data (por exemplo, "2025-09-23").
import requests
token = ""
headers = {'Authorization': 'JWT {}'.format(token)}
params1 = {
'data_base': '2025-09-23'
}

# Construa um DataFrame pandas a partir dos dados recebidos.
response1 = requests.get('https://laboratoriodefinancas.com/api/v1/planilhao',params=params1, headers=headers)
df_planilhao = pd.DataFrame(response1.json()['dados'])
df_planilhao

# Selecione a empresa do setor de "tecnologia" que apresenta o maior ROC (Return on Capital) nessa data.
# Exiba o ticker da empresa, setor e o valor do ROC correspondente.
filtro = (df_planilhao['setor'] == 'tecnologia') 
df_tec = df_planilhao.loc[filtro]
df_tec_roc = df_tec.sort_values(by='roc', ascending=False).head(1)
df_tec_roc = df_tec_roc[['ticker','setor','roc']]
ticker = df_tec_roc['ticker'].iloc[0]
setor = df_tec_roc['setor'].iloc[0]
roc = df_tec_roc['roc'].iloc[0]
print(f'O maior valor do ROC encontrado foi {roc}, no ticker: {ticker} do setor de {setor}')


# 10 - A API do Laboratório de Finanças fornece informações de balanços patrimoniais de empresas listadas na B3.
# Acesse o endpoint: https://laboratoriodefinancas.com/api/v1/balanco
# usando a empresa Gerdau ("GGBR4") e o período 2025/2º trimestre (ano_tri = "20252T").
# O retorno da API contém uma chave "balanco", que é uma lista com diversas contas do balanço.

headers = {'Authorization': 'JWT {}'.format(token)}
params2 = {'ticker': 'GGBR4', 
          'ano_tri': '20252T'
          }
response2 = requests.get('https://laboratoriodefinancas.com/api/v1/balanco',params=params2, headers=headers)

dados = response2.json()['dados'][0]
dados = dados['balanco']

df_balanco = pd.DataFrame(dados)
df_balanco

# Localize dentro dessa lista a conta cuja descrição é “Ativo Total” e "Lucro Liquido".

# Conta "Ativo Total" = 1
filtro = (df_balanco['descricao']=='Ativo Total')
df_ativos = df_balanco.loc[filtro]
ativos_totais = df_ativos.loc[filtro, "valor"].iloc[0]

# Conta "Lucro líquido do período" = 6.01.01.01
filtro2= (df_balanco["descricao"].str.contains("^lucro", case=False, na=False))
df_lucro_temp = df_balanco.loc[filtro2]
filtro3 = (df_lucro_temp["conta"] =='6.01.01.01')
df_lucro = df_lucro_temp.loc[filtro3]
lucro_liquido = df_lucro['valor'].iloc[0]

# Calcule o Return on Assets que é dados pela formula: ROA = Lucro Liquido / Ativo Totais
roa = lucro_liquido/ativos_totais

print(f'O valor dos ativos totais foi de {ativos_totais:.2f}')
print(f'O valor do lucro liquido foi de {lucro_liquido:.2f}')
print(f'O ROA foi de {roa}, ou aproximadamente {roa*100:.2f}%')