import matplotlib.pyplot as plt
import pandas as pd
import requests

# 1 - A BrasilAPI possui um endpoint que retorna os feriados nacionais de um ano específico.
# Acesse o endpoint:https://brasilapi.com.br/api/feriados/v1/{ano}
# Responda: quantos feriados nacionais existem no ano atual?
ano = 2025
url = f'https://brasilapi.com.br/api/feriados/v1/{ano}'
r = requests.get(url)
dados = r.json()
df = pd.DataFrame(dados)
feriados = df.shape[0]
print(f'No ano {ano} existem {feriados} feriados')

# 2 - A BrasilAPI disponibiliza informações da tabela FIPE, incluindo marcas, modelos e preços de veículos.
# Acesse o endpoint de marcas da FIPE para o tipo de veículo carros.
# Transforme em DataFrame e acha o codigo BYD através da coluna "nome"
# Use esse código para acessar o endpoint de modelos da marca BYD.
# api = f"https://brasilapi.com.br/api/fipe/veiculos/v1/{tipoVeiculo}/{codigoMarca}"
# Construa um DataFrame com os modelos disponíveis.
# Responda: quantos modelos de veículos BYD estão cadastrados na FIPE?

tipoVeiculo = "carros"
api = f"https://brasilapi.com.br/api/fipe/marcas/v1/{tipoVeiculo}"
r1 = requests.get(api)
carros = r1.json()

df_carros = pd.DataFrame(carros)

filtro = df_carros['nome'] == 'BYD'
byd = df_carros.loc[filtro]

codigoMarca = '238'
api1 = f"https://brasilapi.com.br/api/fipe/veiculos/v1/{tipoVeiculo}/{codigoMarca}"
r2 = requests.get(api1)
modelos = r2.json()

df_byd = pd.DataFrame(modelos)


# 3 - O Banco Mundial disponibiliza uma API pública com diversos indicadores econômicos.
# O código do indicador NY.GDP.PCAP.CD corresponde ao PIB per capita (em dólares correntes).
# Usando Python e a biblioteca requests para acessar a API e pandas para manipulação dos dados:
# Acesse o indicador NY.GDP.PCAP.CD para o Brasil (BRA).
# Construa um DataFrame contendo os anos (date) e os valores de PIB per capita (value).
# Identifique em qual ano o Brasil apresentou o menor PIB per capita e mostre o respectivo valor.


pais = "BRA"
indicador = "NY.GDP.PCAP.CD"
url = f"https://api.worldbank.org/v2/country/{pais}/indicator/{indicador}?format=json"
r3 = requests.get(url)
indicadores = r3.json()
indicadores = indicadores[1]
df = pd.json_normalize(indicadores)
df = df[['date', 'value']]
df_min = df.sort_values(by='value', ascending=True)
top1 = df_min.head(1)

print(
    f'No ano de {top1.values[0][0]} foi o menor PIB PER CAPITA do Brasil, no valor de {top1.values[0][1]:.2f}')


# 4 - O IPEA disponibiliza uma API pública com diversas séries econômicas.
# Para encontrar a série de interesse, é necessário primeiro acessar o endpoint de metadados.
# Acesse o endpoint de metadados: http://www.ipeadata.gov.br/api/odata4/Metadados
# e filtre para encontrar as séries da ANFAVEA relacionadas a “licenciamento”.
# Dica Técnica, filtre atraves das colunas FNTSIGLA e depois SERNOME:

url_ipea = f'http://www.ipeadata.gov.br/api/odata4/Metadados'
r4 = requests.get(url_ipea)
metadados = r4.json()
metadados = metadados['value']
df = pd.DataFrame(metadados)

df_anfavea = df[df["FNTSIGLA"].str.contains(
    "anfavea.*", regex=True, case=False)]
df_anfavea[df_anfavea["SERNOME"].str.contains(
    "licenciamento", regex=True, case=False)]

# Descubra qual é o código da série correspondente ao total de Licenciamentos de Autoveículos.
# Observe a descrição da série (SERCOMENTARIO) para confirmar que se trata de automóveis, veículos comerciais leves e pesados.
# Usando o código encontrado, acesse a API de valores: http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='CODIGO_ENCONTRADO')

SERCODIGO = "ANFAVE12_LICVETOT12"
url_ipea2 = f"http://ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='{SERCODIGO}')"
r5 = requests.get(url_ipea2)
data = r5.json()['value']

# e construa um DataFrame pandas com as datas (DATA) e os valores (VALVALOR).
df_data = pd.DataFrame(data)
df_data = df_data[['VALDATA', 'VALVALOR']]

# Converta a coluna de datas para o formato adequado.
# Dicas técnicas: Para tratar corretamente as datas da série:

df_data["VALDATA"] = pd.to_datetime(
    df_data["VALDATA"], utc=True, errors="coerce")
df_data["VALDATA"] = df_data["VALDATA"].dt.tz_convert("America/Sao_Paulo")
df_data["DATA"] = df_data["VALDATA"].dt.date
df_data = df_data[['DATA', 'VALVALOR']]
df_data
# Monte um gráfico de linha mostrando a evolução dos licenciamentos de autoveículos ao longo do tempo.
# Dica: você pode usar a biblioteca matplotlib ou pandas.plot para gerar o gráfico.

plt.figure(figsize=(12, 6))
plt.plot(df_data["DATA"], df_data["VALVALOR"])
plt.title("Licenciamento de Autoveículos no Brasil")
plt.xlabel("Ano")
plt.ylabel("Quantidade")
plt.grid(True)
plt.show()


# 5 - Utilize a API PTAX do Banco Central (endpoint CotacaoDolarPeriodo) para obter as cotações do dólar (compra e venda) em um período definido por você (ex.: de 01/01/2023 a 31/12/2023).
# Baixe os dados e monte um DataFrame com as datas e as cotações.
# Converta a coluna de datas para o formato adequado.
# Construa um gráfico de linha mostrando a evolução do dólar (venda) ao longo do período.
url_bc = (
    f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?"
    "@dataInicial='01-01-2023'&@dataFinalCotacao='12-31-2023'&$format=json"
)
r6 = requests.get(url_bc).json()['value']
dados = pd.DataFrame(r6)
dados

dados["dataHoraCotacao"] = pd.to_datetime(
    dados["dataHoraCotacao"], utc=True, errors="coerce")
dados["dataHoraCotacao"] = dados["dataHoraCotacao"].dt.tz_convert(
    "America/Sao_Paulo")
dados["data"] = dados["dataHoraCotacao"].dt.date
dados = dados[['data', 'cotacaoVenda', 'cotacaoCompra']]
dados

plt.figure(figsize=(12, 6))
plt.plot(dados['data'], dados['cotacaoVenda'])
plt.title("Valor de venda do dólar ao longo de 2023")
plt.xlabel("Ano")
plt.ylabel("Valor Venda")
plt.grid(True)
plt.show()
