# Painel ao vivo para exibir gauge e tendência em tempo real
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import config  # noqa: E402
from core.visuals import load_latest_score, render_market_sentiment_gauge, render_sentiment_trend  # noqa: E402

REFRESH_INTERVAL_SECONDS = 60


def _update_axes(_, ax_gauge, ax_trend):
    """Atualiza ambas as visualizações a partir dos dados mais recentes."""
    scores_path = config.SCORES_PATH
    if not scores_path.exists():
        for ax in (ax_gauge, ax_trend):
            ax.clear()
            ax.text(
                0.5,
                0.5,
                "Aguardando dados...",
                ha="center",
                va="center",
                color="#dddddd",
                fontsize=14,
            )
            ax.axis("off")
        return

    try:
        score, _ = load_latest_score(scores_path)
        render_market_sentiment_gauge(score, ax=ax_gauge)
    except Exception as exc:  # pylint: disable=broad-except
        ax_gauge.clear()
        ax_gauge.set_facecolor("#161616")
        ax_gauge.text(
            0.5,
            0.5,
            f"Erro gauge:\n{exc}",
            ha="center",
            va="center",
            color="#ffb347",
            fontsize=12,
        )
        ax_gauge.axis("off")

    try:
        render_sentiment_trend(scores_path, ax=ax_trend, max_points=40)
    except Exception as exc:  # pylint: disable=broad-except
        ax_trend.clear()
        ax_trend.set_facecolor("#161616")
        ax_trend.text(
            0.5,
            0.5,
            f"Erro tendência:\n{exc}",
            ha="center",
            va="center",
            color="#ffb347",
            fontsize=12,
        )
        ax_trend.axis("off")


def launch_dashboard() -> None:
    plt.rcParams["toolbar"] = "None"
    fig = plt.figure(figsize=(12, 5))
    fig.canvas.manager.set_window_title("Painel Macro")
    fig.patch.set_facecolor("#111111")

    ax_gauge = fig.add_subplot(1, 2, 1)
    ax_trend = fig.add_subplot(1, 2, 2)

    _update_axes(0, ax_gauge, ax_trend)
    anim = FuncAnimation(
        fig,
        _update_axes,
        fargs=(ax_gauge, ax_trend),
        interval=REFRESH_INTERVAL_SECONDS * 1000,
    )

    # Mantém referência à animação para evitar coleta de lixo prematura.
    fig._sentiment_anim = anim  # type: ignore[attr-defined]

    fig.suptitle("Painel Macro", color="#f5f5f5", fontsize=16)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    launch_dashboard()

