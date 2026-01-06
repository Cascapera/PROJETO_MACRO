# Utilitário para inspecionar a saída do parser do MarketWatch
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import assets, data_sources, network  # noqa: E402


def main() -> None:
    """Coleta as variações atuais dos ativos que usam MarketWatch e grava em um documento."""
    lines = []
    for asset in assets.load_assets():
        if asset.source_key != "marketwatch":
            continue

        outcome = network.fetch_html(asset)
        parser = data_sources.get_parser(asset.source_key)
        variation = parser(outcome.html) if outcome.html else None
        reason = f" | block_reason={outcome.block_reason}" if outcome.block_reason else ""

        lines.append(
            f"Ativo: {asset.name}\n"
            f"URL: {asset.url}\n"
            f"status={outcome.status}{reason}\n"
            f"variacao_parser={variation}\n"
        )

    output_path = Path("docs/marketwatch_parser_output.txt")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Arquivo gerado em: {output_path}")


if __name__ == "__main__":
    main()

