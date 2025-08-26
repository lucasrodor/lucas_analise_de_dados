import pandas as pd

df = pd.read_csv("C:\\Users\\lucas\\IBMEC\\programacao_para_analise_de_dados_2025.2\\data\\imoveis_brasil.csv")

# 1.	Mostrar as 5 primeiras e as 5 ultimas linhas do DataFrame. Use também df.sample(5) e verifique qual o resultado.

df.head(5)
df.tail(5)
df.sample(5)

# 2.	Exibir o número de linhas e colunas com shape.
print(df.shape)

# 3.	Listar os nomes das colunas.
print(df.columns)
for i in range(len(df.columns)):
    print(df.columns[i])

# 4.	Mostrar os tipos de dados de cada coluna.
df.dtypes

# 5.	Usar describe() para ver estatísticas das colunas numéricas.
df.describe()

# 6.	Usar info() para ver informações gerais.
print(df.info)

# 7.	Verifique quais os tipos de imóveis que temos na amostra.
df['Tipo_Imovel'].unique()  # Mostra apenas uma vez os itens que aparecem
df['Tipo_Imovel'].nunique()  # Mostra o número de itens diferente que aparecem
df['Tipo_Imovel'].value_counts()  # Mostra a quantidade que aparece de cada um

# 8.	Filtrar imóveis com valor acima de R$ 1.000.000,00.
df.columns
df.milhao = df[df['Valor_Imovel'] > 1000000]

# 9.	Selecionar as colunas cidade, bairro, e valor em um novo DataFrame chamado df2
df.columns
df2 = df[['Cidade', 'Bairro', 'Valor_Imovel']]
df2

# 10.	Filtrar os imóveis da cidade de Curitiba e gravar em um novo df_curitiba
df_curitiba = df[df['Cidade'] == 'Curitiba']
df_curitiba

# 11.	Verificar valores nulos em cada coluna com isnull().sum().
df.isnull().sum()

# 12.	Ordenar os 10 imóveis mais caros (coluna valor decrescente).
df_caro = df.sort_values(by='Valor_Imovel', ascending=False)
df_caro.head(10)

# 13.	Qual é o valor médio (média) dos imóveis no dataset?
media = df['Valor_Imovel'].mean()
print(f'Média: R${media:.2f}')

# 14.	Qual é o valor mediano (mediana)?
mediana = df['Valor_Imovel'].median()
print(f'Mediana: R${mediana:.2f}')

# 15.	Qual é o desvio padrão do valor dos imóveis?
desvio_padro = df['Valor_Imovel'].std()
print(f'Desvio Padrão: R${desvio_padro:.2f}')

# 16.	Mostre o valor mínimo e o valor máximo de área construída (ou variável similar).
df.columns  # Area_m2
media_area = df['Area_m2'].mean()
print(f'Média: {media_area:.2f} m²')
df['Area_m2'].max()
df['Area_m2'].min()


# 17.	Quantos imóveis estão abaixo do valor médio e quantos estão acima?
media
abaixo = df[df['Valor_Imovel'] < media].shape[0]
acima = df[df['Valor_Imovel'] > media].shape[0]
abaixo
acima

# 18.	Adicionar uma nova coluna chamada valor_m2 que divide o valor pela area.
df['Valor_m2'] = (df['Valor_Imovel'] / df['Area_m2']).round(2)
df

# 19.	Inserir uma linha fictícia no final do DataFrame, com um imóvel da cidade "Teste", valor 999999 e área 100.
linha = pd.DataFrame([{
    'Cidade': 'teste',
    'Valor_Imovel': 999999,
    'Area': 100}])

df = pd.concat([df, linha], ignore_index=True)
df


# 20.	Verificar valores nulos novamente.
df.isnull().sum()

# 21.	Remover todos os imóveis com valor Numero_Quartos=5
df.filtrado = df[df['Numero_Quartos'] != 5]
# ou df = df.drop(df[df['Numero_Quartos'] == 5].index)

df.filtrado
# 22.	Excluir a coluna ID_Imovel
df = df.drop('ID_Imovel', axis=1)
df

# 23.	Remover os imóveis da cidade "Teste".
df = df.drop(df[df['Cidade'] == 'Teste'].index)

# 24.	Agrupar por cidade e calcular média de valor dos imóveis.
pd.set_option('display.float_format', '{:,.2f}'.format)
media_cidade = df.groupby('Cidade', as_index=False)[
    'Valor_Imovel'].mean().round(2)
media_cidade['Valor_Formatado'] = media_cidade['Valor_Imovel'].apply(
    lambda x: f"R$ {x:,.2f}")
media_cidade
