import requests
import pandas as pd

BASE = "https://www.ipea.gov.br/atlasviolencia/api/v1"
SERIE_ID = 328  # Homicídios
ANO = 2025

# ------------------ UF (todos os estados em 2024) ------------------

url_uf = f"{BASE}/valores-series/{SERIE_ID}/3"  # abrangência=3 (UF)

r_uf = requests.get(url_uf, timeout=60)
dados_uf = r_uf.json()
df_uf = pd.DataFrame(dados_uf)

#Dados de homicídios no Goiás ao longo dos anos ( 1989 - 2023)
df_go = df_uf[df_uf['sigla']=="GO"]

# ------------------ Código de municípios do Goiás ----------------------

url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/GO/municipios"
r_cod = requests.get(url)
dados = r_cod.json()
df = pd.DataFrame(dados)

#Código IBGE de municípios do Goiás
codigos = [str(c) for c in df["id"].tolist()]
len(codigos)

# ------------------ Municípios de Goiás (apenas 2023) ------------------

url_mun = f"{BASE}/valores-series/{SERIE_ID}/4"  # abrangência=4 (Município)
r_mun = requests.get(url_mun, timeout=60)
dados_mun = r_mun.json()
df_mun = pd.DataFrame(dados_mun)
df_mun_go = df_mun[df_mun["cod"].isin(codigos)]

#Filtrando para 2023
df_mun_go["periodo"] = pd.to_datetime(df_mun_go["periodo"], errors="coerce")
df_mun_go["ano"] = df_mun_go["periodo"].dt.year

#Dados de homicídios nos municípios de Goiás no ano de 2023
df_mun_go_2023 = df_mun_go[df_mun_go["ano"] == 2023]
df_mun_go_2023.rename(columns={'valor':'qtd_homicidio'},inplace=True)


df_mun_go_2023_go = df_mun_go_2023[df_mun_go_2023["cod"] == '5208707']
df_mun_go_2023["qtd_homicidio"] = pd.to_numeric(df_mun_go_2023["qtd_homicidio"], errors="coerce")
df_mun_go_2023.sort_values('qtd_homicidio', ascending=False).head(10)

#------------------- Salvando em CSV ---------------------------

df_uf.to_csv("homicidios_uf.csv", index=False, encoding="utf-8")
df_go.to_csv("homicidios_go_aolongodosanos.csv", index=False, encoding="utf-8")
df_mun_go.to_csv("homicidios_mun_go_aolongodosanos.csv", index=False, encoding="utf-8")
df_mun_go_2023.to_csv("homicidios_mun_go_2023.csv", index=False, encoding="utf-8")

# ------------------ População dos municípios ------------------

# Tabela 9514 = Censo 2022 - População residente por município
url = "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93?localidades=N6[all]"

# Faz a requisição
response = requests.get(url)
data = response.json()

# Extrai os dados da resposta
municipios = []
for item in data[0]['resultados'][0]['series']:
    municipio_id = item['localidade']['id']
    municipio_nome = item['localidade']['nome']
    populacao = int(item['serie']['2022'])
    municipios.append({
        'codigo_municipio': municipio_id,
        'municipio': municipio_nome,
        'populacao_censo_2022': populacao
    })

# Converte para DataFrame
df = pd.DataFrame(municipios)

# Filtra apenas os municípios de Goiás (códigos iniciam com '52')
df_pop_go_2022 = df[df['codigo_municipio'].str.startswith('52')].reset_index(drop=True)

print(df_pop_go_2022.head())
print(f"\nTotal de municípios em GO: {len(df_go)}")

# (Opcional) Salvar em CSV
# df_pop_go_2022.to_csv("populacao_goias_censo_2022.csv", index=False, encoding="utf-8")

# ------------------ Outra população ---------------------------

# Última estimativa disponível para TODOS os municípios (Brasil)
url = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/2025"
data = requests.get(url, timeout=120).json()
df = pd.DataFrame(data)

# 1) tira a primeira linha (rótulos que o SIDRA devolve)
df_clean = df.iloc[1:].copy()

# 2) renomeia colunas principais
# D1 = Município, D2 = Variável, D3 = Ano | V = Valor
rename_map = {
    "D1C": "cod_municipio",
    "D1N": "municipio",
    "V":   "populacao",
    "D3C": "ano"      # geralmente o ano vem aqui; se não, usamos fallback abaixo
}
df_clean = df_clean.rename(columns=rename_map)

# 3) fallbacks de ano (caso o SIDRA traga em outra coluna)
if "ano" not in df_clean.columns:
    if "D3N" in df_clean.columns:  # às vezes o ano vem em D3N
        df_clean["ano"] = df_clean["D3N"]
    elif "ANO" in df_clean.columns:  # ou em ANO
        df_clean["ano"] = df_clean["ANO"]

# 4) tipos
df_clean["cod_municipio"] = df_clean["cod_municipio"].astype(str)
df_clean["populacao"] = pd.to_numeric(df_clean["populacao"], errors="coerce")
df_clean["ano"] = pd.to_numeric(df_clean["ano"], errors="coerce")


# 5) garante que sua lista codigos é string
codigos = [str(c) for c in codigos]

# 6) filtra só municípios de Goiás pela lista de códigos IBGE
df_pop_go = df_clean[df_clean["cod_municipio"].isin(codigos)].copy()

# 7) mantém só as colunas pedidas e ordena bonitinho
df_pop_go = df_pop_go[["cod_municipio", "municipio", "populacao", "ano"]]
df_pop_go_2025 = df_pop_go.sort_values(["populacao"], ascending=False).reset_index(drop=True)

# opcional: salvar
# df_pop_go.to_csv("populacao_municipios_GO_ultimo.csv", index=False, encoding="utf-8")

print(df_pop_go.head())

# ------------------ Dados interessantes -----------------------

#Filtrando para 2023
df_uf["periodo"] = pd.to_datetime(df_uf["periodo"], errors="coerce")
df_uf["ano"] = df_uf["periodo"].dt.year

#Dados de homicídios nos estados no ano de 2023
df_uf_2023 = df_uf[df_uf["ano"] == 2023]
df_uf_2023["valor"] = pd.to_numeric(df_uf_2023["valor"], errors="coerce")

#medidas

df_uf["valor"] = pd.to_numeric(df_uf["valor"], errors="coerce")
total_homicidios_estado = df_uf.groupby('sigla', as_index=False)['valor'].sum()
media_homicidios_estado = df_uf.groupby('sigla', as_index=False)['valor'].mean().round(2)

#em 2023
total_homicidios_2023 = df_uf_2023['valor'].sum()
media_homicidios_2023 = df_uf_2023['valor'].mean().round(2)

#taxa_variacao - Variação percentual ano a ano
df_go["valor"] = pd.to_numeric(df_go["valor"], errors="coerce")
df_go['taxa_var'] = df_go['valor'].pct_change() * 100

#media movel dos ultimos 3 anos
df_go['media_movel_3a'] = df_go['valor'].rolling(3).mean()

#top 10 municípios com mais homicídios
df_mun_go_2023["qtd_homicidio"] = pd.to_numeric(df_mun_go_2023["qtd_homicidio"], errors="coerce")
top10 = df_mun_go_2023.sort_values('qtd_homicidio', ascending=False).head(10)

#Dados População

caminho = 'C:\\Users\\lucas\\IBMEC\\programacao_para_analise_de_dados_2025.2\\ap2\\data\\despesas_seguranca.xlsx'
df_finbra = pd.read_excel(caminho)
df_mun_go_2023

# padroniza os tipos de código antes do merge
df_mun_go_2023["cod"] = df_mun_go_2023["cod"].astype(str).str.zfill(7)
df_finbra["Cod.IBGE"] = df_finbra["Cod.IBGE"].astype(str).str.zfill(7)

# faz o merge pegando só os códigos que existem nos dois (INNER JOIN)
df_final = pd.merge(
    df_mun_go_2023,
    df_finbra,
    left_on="cod",
    right_on="Cod.IBGE",
    how="inner"
)

# mantém apenas as colunas desejadas e na ordem especificada
df_final = df_final[["cod", "População", "Valor", "UF", "sigla", "qtd_homicidio", "ano"]]
df_final.rename(columns = {'cod':'Codigo IBGE', 'sigla':'Municipio', 'qtd_homicidio':'Qtd_Homicidios','ano':'Ano'}, inplace=True)
df_final

df_final['taxa/1000hab'] = df_final['Qtd_Homicidios']/df_final['População']*1000
df_final

#-------------------- Pib per capita municípios -------------------
URL = (
    "https://apisidra.ibge.gov.br/values/"
    "t/5938/n6/all/n3/52/v/37/p/last?formato=json"
)

resp = requests.get(URL, timeout=60)
resp.raise_for_status()
data = resp.json()


# A primeira linha do retorno é metadado; dados começam no índice 1
df_raw = pd.DataFrame(data[1:])

# Extrai e renomeia colunas úteis
df = df_raw.rename(columns={
    "D1C": "codigo_municipio",   # código do município
    "D1N": "municipio",          # nome do município
    "D3N": "ano",                # ano
    "V": "valor_pib"             # valor do PIB
})

# Converte tipos
df["codigo_municipio"] = df["codigo_municipio"].astype(str)
df["ano"] = df["ano"].astype(int)
df["valor_pib"] = pd.to_numeric(df["valor_pib"], errors="coerce")

# Filtra pelos códigos desejados
df_filtrado = df[df["codigo_municipio"].isin(codigos)]

# Ordena (opcional)
df_filtrado = df_filtrado.sort_values(["ano", "municipio"]).reset_index(drop=True)

df_pib = df_filtrado[['codigo_municipio','municipio','valor_pib','ano']]

df_pib['valor_pib'] = df_pib['valor_pib'] * 1000

# 1) padroniza chaves
df_final["Codigo IBGE"] = df_final["Codigo IBGE"].astype(str).str.zfill(7)
df_pib["codigo_municipio"] = df_pib["codigo_municipio"].astype(str).str.zfill(7)

# 2) pega o PIB do ano mais recente por município
df_pib_latest = (
    df_pib.sort_values(["codigo_municipio", "ano"])
          .drop_duplicates(subset="codigo_municipio", keep="last")
          .loc[:, ["codigo_municipio", "valor_pib", "ano"]]
          .rename(columns={"ano": "Ano_PIB"})
)

# 3) merge (LEFT mantém todos os municípios do df_final)
df_final = (
    df_final.merge(
        df_pib_latest,
        left_on="Codigo IBGE",
        right_on="codigo_municipio",
        how="left"
    )
    .drop(columns=["codigo_municipio"])  # coluna auxiliar
)

# 4) PIB per capita
# valor_pib está em MIL R$ -> converto para R$ multiplicando por 1000
df_final["PIB_per_capita"] = (df_final["valor_pib"]) / df_final["População"]

# (opcional) arredonda e organiza
df_final["PIB_per_capita"] = df_final["PIB_per_capita"].round(2)
df_final = df_final[['Codigo IBGE','Municipio', 'População','Valor','Qtd_Homicidios','valor_pib','PIB_per_capita','taxa/1000hab','Ano','Ano_PIB']]
df_final.rename(columns={'valor_pib':'PIB'},inplace=True)
df_final.rename(columns={'Valor':'Gasto_Seguranca'},inplace=True)
df_final


#--------------------------- Dados Finais ------------------------- 
#Dados de homicídios no Goiás ao longo dos anos ( 1989 - 2023)
df_go

#Código IBGE de municípios do Goiás
codigos

#Dados de homicídios nos municípios de Goiás no ano de 2023
df_mun_go_2023

# População dos municípios do Goiás no ano de 2022 )
df_pop_go_2022

# População dos municípios do Goiás no ano de 2022 )
df_pop_go_2025

#Dados de homicídios nos estados no ano de 2023
df_uf_2023

#dados PIB 2021 
df_pib

#dados PIB municipios goias
df_filtrado

#medidas
total_homicidios_estado
media_homicidios_estado
total_homicidios_2023
media_homicidios_2023
df_go['taxa_var']
df_go['media_movel_3a']
top10

#dados finais
df_final

#salvar em arquivo
# df_final.to_excel("dados_completos.csv", index=False, encoding="utf-8")
# df_final.to_excel("dados_completos.xlsx", index=False)