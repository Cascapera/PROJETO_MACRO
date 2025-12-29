# Parser específico para páginas do MarketWatch
from typing import Optional

from bs4 import BeautifulSoup


def parse_variation(html: str) -> Optional[str]:
    """Extrai a variação percentual exibida na página do MarketWatch."""
    soup = BeautifulSoup(html, "html.parser")
    span = soup.find("span", class_="change--percent--q")
    if not span:
        return None
    text = span.get_text(separator="", strip=True)
    text = text.replace("\u00a0", "").replace("(", "").replace(")", "").replace(",", ".")
    if not text.endswith("%"):
        text = f"{text}%"
    return text

