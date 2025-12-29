# Parser específico para páginas do Investing.com
from typing import Optional

from bs4 import BeautifulSoup


def parse_variation(html: str) -> Optional[str]:
    """Localiza o span com a variação percentual atual."""
    soup = BeautifulSoup(html, "html.parser")
    span = soup.find("span", {"data-test": "instrument-price-change-percent"})
    if not span:
        return None
    text = span.get_text(separator="", strip=True)
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1]
    text = text.replace("\u00a0", "").replace(" ", "").replace(",", ".")
    if not text.endswith("%"):
        text = f"{text}%"
    return text

