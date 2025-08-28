import pandas as pd
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU4OTczNjU1LCJpYXQiOjE3NTYzODE2NTUsImp0aSI6IjBkYzQzNGM4ZDYwOTRiMWE4Yzk1NTMzOTU2ZDYxNWEyIiwidXNlcl9pZCI6IjQwIn0.g3hHkVgmxEfNSu7_9E0YpARb9F3tYTSm15x31wUkfJM"
headers = {'Authorization': f'JWT {token}'}

# pega todos os tickers
r_ticker = requests.get('https://laboratoriodefinancas.com/api/v1/ticker', headers=headers).json()
tickers = [t['ticker'] for t in r_ticker['dados']]

roes = {}

for ticker in tickers:
    params = {'ticker': ticker, 'ano_tri': '20252T'}
    r = requests.get('https://laboratoriodefinancas.com/api/v1/balanco',
                     params=params, headers=headers).json()

    # se não vier a chave esperada, pula
    if 'dados' not in r or not r['dados']:
        continue

    df = pd.DataFrame(r['dados'][0]['balanco'])

    # Lucro Líquido (use "valor" em vez de ['valor'])
    filtro_ll = (
        (df["conta"] == "3.11") &
        (df["descricao"].str.contains("^lucro", case=False, na=False)) &
        (df["data_ini"] == "2025-01-01")
    )
    ll = df.loc[filtro_ll, "valor"]
    if ll.empty:
        continue
    lucro_liquido = ll.iloc[0]

    # Patrimônio Líquido
    filtro_pl = (
        (df["conta"].str.contains("2.0", case=False, na=False)) &
        (df["descricao"].str.contains("^patrim", case=False, na=False))
    )
    pl_s = df.loc[filtro_pl, "valor"]
    if pl_s.empty:
        continue
    pl = pl_s.iloc[0]
    if pl == 0:
        continue

    # ROE
    roes[ticker] = lucro_liquido / pl

# imprime todos
for t, v in roes.items():
    print(f"{t}: ROE = {v*100:.2f}%")

# maior ROE
if roes:
    maior_ticker = max(roes, key=roes.get)
    print(f"\nO maior ROE foi {roes[maior_ticker]*100:.2f}% na ação {maior_ticker}")
else:
    print("Nenhum ROE calculado com os filtros atuais.")
