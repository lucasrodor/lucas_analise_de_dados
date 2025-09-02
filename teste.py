import json
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIError(RuntimeError):
    """Erro genérico da API."""


def _build_session(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: Tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Session:
    """Cria uma sessão Requests com política de retry."""
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _extract_records(payload: Union[List[Any], Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrai a lista de registros do JSON retornado pela API, mesmo que venha
    embrulhado em chaves como 'data', 'items', 'results', etc.
    """
    if isinstance(payload, list):
        # já é uma lista de registros
        return payload  # type: ignore[return-value]

    if not isinstance(payload, dict):
        raise APIError("Formato de resposta inesperado: não é lista nem dict.")

    # Heurísticas comuns para chaves de coleção
    candidate_keys = ["data", "dados", "items", "results", "registros", "content"]
    for key in candidate_keys:
        if key in payload and isinstance(payload[key], list):
            return payload[key]  # type: ignore[return-value]

    # Se não achou, tente detectar a primeira lista dentro do dict
    for v in payload.values():
        if isinstance(v, list) and (not v or isinstance(v[0], (dict, str, int, float, bool))):
            return v  # type: ignore[return-value]

    # Como fallback, se for um dict simples, retornamos uma lista com um único item
    if payload:
        return [payload]  # type: ignore[return-value]

    # Último recurso: lista vazia
    return []


def consumir_api_vendas(
    url: str = "http://189.115.241.122:8097/federal/vendas",
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 15,
    retries: int = 3,
    backoff_factor: float = 0.5,
) -> pd.DataFrame:
    """
    Consome a API de vendas e retorna um pandas.DataFrame com tratamento de erros.

    Parâmetros:
        url: endpoint completo da API.
        params: dicionário de query params (opcional).
        timeout: timeout por requisição em segundos.
        retries: número de tentativas automáticas em falhas transitórias.
        backoff_factor: fator de espera exponencial entre retries.

    Retorna:
        DataFrame com os registros normalizados.
    """
    session = _build_session(retries=retries, backoff_factor=backoff_factor)

    try:
        resp = session.get(url, params=params, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Falha de rede ao acessar a API: {exc}") from exc

    # Erros HTTP explícitos
    if not (200 <= resp.status_code < 300):
        # Tentar extrair mensagem da API
        msg = None
        try:
            j = resp.json()
            msg = j.get("message") or j.get("error") or j.get("detail")
        except Exception:
            pass
        raise APIError(
            f"HTTP {resp.status_code} ao acessar a API."
            + (f" Detalhe: {msg}" if msg else "")
        )

    # Tentar parsear JSON
    try:
        payload = resp.json()
    except json.JSONDecodeError as exc:
        # Às vezes a API retorna texto; capturar para diagnóstico
        text_preview = (resp.text or "")[:300]
        raise APIError(
            "Resposta não é um JSON válido. Prévia do conteúdo: "
            + repr(text_preview)
        ) from exc

    # Extrair registros e normalizar em DataFrame
    try:
        records = _extract_records(payload)
        # Se os registros forem escalares (ex.: lista de strings), transformar em dicts
        if records and not isinstance(records[0], dict):
            records = [{"valor": r} for r in records]  # type: ignore[list-item]

        df = pd.json_normalize(records)
    except Exception as exc:
        raise APIError(f"Falha ao converter o JSON em DataFrame: {exc}") from exc

    # Limpeza leve: remover colunas completamente vazias e ordenar colunas
    if not df.empty:
        df = df.dropna(axis=1, how="all")
        df = df.reindex(sorted(df.columns), axis=1)

    return df


if __name__ == "__main__":
    try:
        df = consumir_api_vendas()
        print(f"Linhas: {len(df)}, Colunas: {len(df.columns)}")
        # Exemplo: salvar em CSV
        df.to_csv("vendas.csv", index=False, encoding="utf-8")
        print("Arquivo salvo: vendas.csv")
        # Exibir primeiras linhas
        print(df.head(10).to_string(index=False))
    except APIError as e:
        # Erro controlado da API
        print(f"[ERRO] {e}")
    except Exception as e:
        # Erro inesperado
        print(f"[ERRO INESPERADO] {e}")


df['NOMVND'].unique()