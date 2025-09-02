import pandas as pd
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU4OTczNjU1LCJpYXQiOjE3NTYzODE2NTUsImp0aSI6IjBkYzQzNGM4ZDYwOTRiMWE4Yzk1NTMzOTU2ZDYxNWEyIiwidXNlcl9pZCI6IjQwIn0.g3hHkVgmxEfNSu7_9E0YpARb9F3tYTSm15x31wUkfJM"
headers = {'Authorization': f'JWT {token}'}
# --- pega todos os tickers e tenta mapear nome/empresa ---
resp_tk = requests.get('https://laboratoriodefinancas.com/api/v1/ticker', headers=headers).json()
lista = resp_tk['dados'] if isinstance(resp_tk, dict) and 'dados' in resp_tk else resp_tk
tickers = [t['ticker'] for t in lista]
nome_por_ticker = {t['ticker']: (t.get('empresa') or t.get('nome') or "") for t in lista}

periodo = '20252T'
resultados = {}     # {ticker: roe} só para consulta rápida
linhas_df = []      # para montar o DataFrame no final

print('='*50)
print(f'Análise do ROE de ações no período {periodo}')
print('='*50)

for ticker in tickers:
    params = {'ticker': ticker, 'ano_tri': periodo}
    r = requests.get('https://laboratoriodefinancas.com/api/v1/balanco',
                     params=params, headers=headers)

    if r.status_code != 200:
        continue

    data = r.json()
    if 'dados' not in data or not data['dados'] or 'balanco' not in data['dados'][0]:
        continue

    df = pd.DataFrame(data['dados'][0]['balanco'])

    # ---- Lucro Líquido (linha conta 3.11, descrição começa com "lucro", data-alvo) ----
    filtro_ll = (
        (df["conta"] == "3.11") &
        (df["descricao"].str.contains("^lucro", case=False, na=False)) &
        (df["data_ini"] == "2025-01-01")
    )
    ll_series = df.loc[filtro_ll, "valor"]
    if ll_series.empty:
        continue
    lucro_liquido = float(ll_series.iloc[0])

    # ---- Patrimônio Líquido (grupo 2.0..., descrição começa com "patrim") ----
    filtro_pl = (
        (df["conta"].astype(str).str.contains("^2\\.0", regex=True, na=False)) &
        (df["descricao"].str.contains("^patrim", case=False, na=False))
    )
    pl_series = df.loc[filtro_pl, "valor"]
    if pl_series.empty:
        continue
    pl = float(pl_series.iloc[0])
    if pl == 0:
        continue

    # ---- (Opcional) Receita Líquida, se existir (muitas vezes é 3.01 ou descrição com "receita líquida") ----
    # Mantém simples: se não achar, fica None e segue o jogo.
    filtro_receita = (
        (df["descricao"].str.contains("receita", case=False, na=False)) &
        (df["descricao"].str.contains("l[ií]quida", case=False, regex=True, na=False))
    )
    receita_series = df.loc[filtro_receita, "valor"]
    receita_liquida = float(receita_series.iloc[0]) if not receita_series.empty else None

    # ---- ROE ----
    roe = lucro_liquido / pl
    resultados[ticker] = roe

    # imprime imediatamente
    print(f"{ticker}: ROE = {roe*100:.2f}% | LL = R${lucro_liquido:,.2f} | PL = R${pl:,.2f}")

    # guarda linha para o DataFrame final
    linhas_df.append({
        "ticker": ticker,
        "nome": nome_por_ticker.get(ticker, ""),
        "periodo": periodo,
        "lucro_liquido": lucro_liquido,
        "pl": pl,
        "roe": roe,
        "receita_liquida": receita_liquida
    })

# --- DataFrame final, ordenado por ROE desc ---
df_result = pd.DataFrame(linhas_df)
if not df_result.empty:
    df_result = df_result.sort_values("roe", ascending=False).reset_index(drop=True)

    print('\n' + '='*50)
    print("Top 10 por ROE")
    print('='*50)
    print(df_result.loc[:, ["ticker","nome","roe","lucro_liquido","pl","receita_liquida"]].head(10))

    # Maior ROE
    maior_ticker = df_result.iloc[0]["ticker"]
    print(f"\nO maior ROE foi {df_result.iloc[0]['roe']*100:.2f}% na ação {maior_ticker}")
else:
    print("\nNenhum ROE calculado com os filtros atuais.")