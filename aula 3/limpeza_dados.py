import pandas as pd

arquivo = "C:\\Users\\lucas\\IBMEC\\programacao_para_analise_de_dados_2025.2\\data\\titanic.csv"
df = pd.read_csv(arquivo)

#Verifica a quantidade de linhas e colunas
df.shape

#Lista os nomes das colunas
df.columns

#Mostra os tipos de dados de cada coluna
df.info()

# Verifica valores nulos em cada coluna
df.isna().sum()  

#linhas com valores nulos de Fare NA
filtro = df["Fare"].isna()
df.loc[filtro]

#Linhas com valores nulos de Age NA
filtro = df["Age"].isna()
df.loc[filtro]

media_idade = df["Age"].mean()
media_idade
df['Age'] = df["Age"].fillna(0).round(2)
df.isna().sum()  # Verifica novamente se há valores nulos

#Valor medio da idade separado por sexo
media_sexo = df.groupby('Sex',as_index=False)['Age'].mean().round(2)
media_sexo

filtro = (df['Sex'] == 'female') & (df['Survived'] == 1)
df_mulher_sobrevivente = df.loc[filtro]
df_mulher_sobrevivente.shape[0]

#Criar uma coluna nova chamada family members
df['Family_members'] = df['SibSp'] + df['Parch']
df

