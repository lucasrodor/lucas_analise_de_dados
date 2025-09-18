import pandas as pd

arquivo = r"C:\Users\lucas\IBMEC\programacao_para_analise_de_dados_2025.2\Pandas Myntra\myntra_dataset_ByScraping.csv"

df = pd.read_csv(arquivo)
df

# 1. Crie um novo DataFrame fictício chamado df_novos_produtos com as seguintes informações e use 
# pd.concat([df, df_novos_produtos]) para juntar ao dataset original e verifique o novo tamanho do DataFrame.
# Exemplo de dicionário:
dados_novos_produtos = {
    "brand_name": ["Myntra Basics", "Denim Pro", "Urban Style"],
    "pants_description": [
        "Men Slim Fit Blue Jeans",
        "Men Regular Fit Jeans",
        "Men Tapered Fit Jeans"
    ],
    "price": [1299, 1599, 1899],
    "MRP": [1999, 2499, 2899],
    "discount_percent": [0.35, 0.40, 0.34],
    "ratings": [4.1, 3.8, 4.3],
    "number_of_ratings": [23, 12, 47]
}
df_novos_produtos = pd.DataFrame(dados_novos_produtos)
df_novos_produtos

df = pd.concat([df, df_novos_produtos], axis = 0)
df
# 2. Crie outro DataFrame df_promocoes apenas com colunas brand_name, pants_description e discount_percent 
# para 3 novos produtos fictícios. Depois, use pd.concat([...], axis=0) e pd.concat([...], axis=1) e explique 
# a diferença entre concatenação por linhas e concatenação por colunas.
# Exemplo de dicionário:
dados_promocoes = {
    "brand_name": ["Test Brand A", "Test Brand B", "Test Brand C"],
    "pants_description": [
        "Men Slim Fit Black Jeans",
        "Men Regular Fit Grey Jeans",
        "Men Loose Fit White Jeans"
    ],
    "discount_percent": [0.50, 0.60, 0.45]
}

df_promocoes = pd.DataFrame(dados_promocoes)
df_promocoes

df = pd.concat([df, df_promocoes], axis = 0)
df


# 3. Crie um DataFrame auxiliar chamado df_marcas_info com informações extras sobre algumas marcas e 
# faça um merge entre o dataset original (df) e esse DataFrame usando a coluna brand_name.
# Exemplo de dicionário:
dados_marcas_info = {
    "brand_name": ["Roadster", "WROGN", "Flying Machine", "Urban Style"],
    "country": ["India", "India", "USA", "Brazil"],
    "year_founded": [2012, 2014, 1980, 2018]
}

df_marcas_info = pd.DataFrame(dados_marcas_info)
df_marcas_info

pd.merge(df, df_marcas_info, on = 'brand_name', how = 'inner')


# 4. Crie um DataFrame df_categorias e faça um merge (inner join) entre df e df_categorias para adicionar a coluna category.
# Exemplo de dicionário:
dados_categorias = {
    "pants_description": [
        "Men Slim Fit Jeans",
        "Men Regular Fit Jeans",
        "Men Loose Fit Cotton Jeans",
        "Men Tapered Fit Jeans"
    ],
    "category": ["Slim", "Regular", "Loose", "Tapered"]
}

df_dados_categorias = pd.DataFrame(dados_categorias)
df_dados_categorias

pd.merge(df, df_dados_categorias, on = 'pants_description', how = 'inner')


# 5. Imagine que você tem um DataFrame df_ratings_extra com avaliações atualizadas. Faça um merge com o dataset original, 
# mantendo todos os registros (how='left'). Depois compare ratings (antiga) com avg_new_rating (nova).
# Exemplo de dicionário:
dados_ratings_extra = {
    "brand_name": ["Roadster", "WROGN", "Urban Style"],
    "avg_new_rating": [4.0, 4.3, 4.1]
}

df_dados_rating_extra = pd.DataFrame(dados_ratings_extra)
df_dados_rating_extra

df_novo = pd.merge(df, df_dados_rating_extra, on = 'brand_name', how = 'left')

marcas = ["Roadster", "WROGN", "Urban Style"]
df_filtrado = df_novo[df_novo['brand_name'].isin(marcas)]
df_comparacao = (
    df_filtrado.groupby('brand_name', as_index=False)
           .agg(
               media_antiga=('ratings', 'mean'),
               media_nova=('avg_new_rating', 'first')
           )
)

