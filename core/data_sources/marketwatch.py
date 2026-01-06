# Parser específico para páginas do MarketWatch
import json
from typing import Optional

from bs4 import BeautifulSoup


def _clean_text(raw: str) -> str:
    """Normaliza o texto percentual para manter o formato esperado."""
    text = raw.replace("\u00a0", "").replace("(", "").replace(")", "").replace(" ", "")
    text = text.replace(",", ".")
    if not text.endswith("%"):
        text = f"{text}%"
    return text


def _extract_from_intraday_block(soup: BeautifulSoup) -> Optional[str]:
    """Busca a variação dentro do bloco principal de intraday indicado pelo MarketWatch."""
    main = soup.find("div", id="maincontent")
    if not main:
        return None

    intraday_region = main.select_one("div.region--intraday")
    if intraday_region is None:
        return None

    # Preferimos o bg-quote específico que contém o percentual
    quote = intraday_region.find("bg-quote", attrs={"field": "percentchange"})
    if quote is not None:
        text = quote.get_text(separator="", strip=True)
        if text:
            return _clean_text(text)

    # Caso o bg-quote não esteja disponível, tentamos localizar o span indicado
    selector_candidates = [
        "div.element--intraday div.intraday__data span.change--percent--q",
        "div.intraday__data span.change--percent--q",
    ]
    for selector in selector_candidates:
        span = intraday_region.select_one(selector)
        if span is None:
            continue
        text = span.get_text(separator="", strip=True)
        if text:
            return _clean_text(text)

    return None


def _extract_from_json_ld(soup: BeautifulSoup) -> Optional[str]:
    """Procura a variação dentro das estruturas JSON-LD da página."""
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for script in scripts:
        raw = script.string
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("@type") in {"Intangible/FinancialQuote", "FinancialProduct"}:
                percent = item.get("priceChangePercent")
                if percent:
                    return _clean_text(str(percent))
            if item.get("@type") == "BreadcrumbList":
                continue
            if "@graph" in item and isinstance(item["@graph"], list):
                for graph_item in item["@graph"]:
                    if not isinstance(graph_item, dict):
                        continue
                    percent = graph_item.get("priceChangePercent")
                    if percent:
                        return _clean_text(str(percent))
    return None


def parse_variation(html: str) -> Optional[str]:
    """Extrai a variação percentual exibida na página do MarketWatch."""
    soup = BeautifulSoup(html, "html.parser")

    text = _extract_from_json_ld(soup)
    if text:
        return text

    text = _extract_from_intraday_block(soup)
    if text:
        return text

    # Fallback: mantém o comportamento anterior caso o layout mude
    span = soup.find("span", class_="change--percent--q")
    if span:
        raw = span.get_text(separator="", strip=True)
        if raw:
            return _clean_text(raw)
    return None

