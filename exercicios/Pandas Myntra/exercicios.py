import pandas as pd 

arquivo = r"C:\Users\lucas\IBMEC\programacao_para_analise_de_dados_2025.2\Pandas Myntra\myntra_dataset_ByScraping.csv"

df = pd.read_csv(arquivo)
df

# 1. Mostrar as 5 primeiras e as 5 últimas linhas do DataFrame. 
df.head(5)
df.tail(5)

# 2. Exibir o número de linhas e colunas.
df.shape
print(f'Número de linhas: {df.shape[0]}')
print(f'Número de colunas: {df.shape[1]}')

# 3. Listar os nomes das colunas.
nome_colunas = df.columns
for i in range (df.shape[1]):
    print (df.columns[i])
# 4. Mostrar os tipos de dados de cada coluna.
df.dtypes
# 5. Usar info() para ver informações gerais.
df.info
# 6. Verifique quais são as marcas (brand_name) que temos na amostra.
marcas = df['brand_name'].unique()
print(f'{marcas.shape[0]} marcas')

# 7. Filtrar produtos com price acima de 1.000,00 e abaixo de 3.000,00
df.columns
filtro = (df['price'] >1000) & (df['price'] < 3000)
df_preco = df.loc[filtro]
df_preco

# 8. Selecionar as colunas brand_name, pants_description e price em um novo DataFrame chamado df2.
df2 = df[['brand_name', 'pants_description', 'price']]
df2

# 9. Filtrar os produtos da marca Roadster e gravar em um novo df_roadster.
filtro = (df['brand_name'] == 'Roadster')
df_roadster = df.loc[filtro]
df_roadster

# 10. Verificar valores nulos em cada coluna.
df.isnull()

# 11. Ordenar os 10 produtos mais caros (price em ordem decrescente).
top10 = df.sort_values(by='price', ascending= False).head(10) 
top10
# 12. Qual é o preço médio (mean) dos produtos no dataset?
df['price'].mean()

# 13. Qual é o preço mediano (median)?
df['price'].median()

# 14. Qual é o desvio padrão do preço (std)?
df['price'].std()

# 15. Mostre o valor mínimo e o valor máximo do desconto (discount_percent).
df['discount_percent'].min()
df['discount_percent'].max()
# 16. Quantos produtos estão abaixo do preço médio e quantos estão acima?
(df['price'] < df['price'].mean()).sum()
(df['price'] > df['price'].mean()).sum()


# 17. Adicionar uma nova coluna chamada preco_desconto que multiplica MRP por (1 - discount_percent).
df.columns
df['preco_desconto'] = df['MRP'] * (1 - df['discount_percent'])
df

# 18. Remover todos os produtos com ratings menores que 2.0.
df_novo = df[df['ratings']>2]

# 19. Excluir a coluna pants_description.
df3 = df.drop(columns=['pants_description'])
df3.columns

# 20. Agrupar por brand_name e calcular o preço médio (price).
preco_medio = df.groupby('brand_name')['price'].mean()