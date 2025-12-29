# Carrega e normaliza os ativos a partir da planilha de referência
from typing import List
from urllib.parse import urlparse

import pandas as pd

from core import config
from core.models import Asset


def _ensure_reference_file() -> None:
    """Garante que a planilha esteja na pasta de dados (migra se necessário)."""
    config.DATA_SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    legacy_path = config.BASE_DIR / config.DATA_SOURCE_PATH.name
    if config.DATA_SOURCE_PATH.exists():
        return
    if legacy_path.exists():
        legacy_path.replace(config.DATA_SOURCE_PATH)


def _resolve_source_key(url: str) -> str:
    """Determina a chave do parser/data-source a partir do domínio da URL."""
    netloc = urlparse(url).netloc.lower()
    if "marketwatch.com" in netloc:
        return "marketwatch"
    return "investing"


def load_assets() -> List[Asset]:
    """Lê a planilha, valida colunas e devolve lista de objetos Asset."""
    _ensure_reference_file()
    df = pd.read_excel(config.DATA_SOURCE_PATH)
    required_columns = {"Ativo", "ValorBase", "URL"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes na planilha: {missing}")

    assets: List[Asset] = []
    for _, row in df.iterrows():
        name = str(row["Ativo"]).strip()
        value_base = float(row["ValorBase"])
        url = str(row["URL"]).strip()
        source_key = _resolve_source_key(url)
        assets.append(Asset(name=name, value_base=value_base, url=url, source_key=source_key))
    return assets

