# Utilitários genéricos para parsing e conversões numéricas
from typing import Optional

from bs4 import BeautifulSoup


def extract_relevant_text(html: str, max_chars: int = 6000) -> str:
    """Extrai o trecho mais relevante do HTML (removendo scripts/estilos)."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
    keywords = ("%", "Pre-Market", "After Hours", "After-Hours", "Previous Close")
    filtered = [line for line in lines if any(keyword in line for keyword in keywords)]
    if not filtered:
        filtered = lines[:120]
    return "\n".join(filtered)[:max_chars]


def parse_variation_percent(value: Optional[str]) -> Optional[float]:
    """Converte string percentual para decimal (ex.: '0,36%' -> 0.0036)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("%"):
        text = text[:-1]
    text = text.replace(" ", "").replace(",", ".")
    try:
        return float(text) / 100.0
    except ValueError:
        return None

