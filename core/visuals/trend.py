# Plota a tendência temporal do sentimento com base na soma acumulada
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def load_trend_series(scores_path: Path) -> pd.Series:
    """Retorna a série crua da linha 'Soma Acumulada'."""
    return _load_cumulative_series(scores_path)


def _load_cumulative_series(scores_path: Path) -> pd.Series:
    """Extrai os valores da linha 'Soma Acumulada' como série temporal float."""
    df = pd.read_csv(scores_path)
    if "Ativo" not in df.columns:
        raise ValueError("Coluna 'Ativo' ausente em historico_scores.csv")

    df = df.set_index("Ativo")
    if "Soma Acumulada" not in df.index:
        raise ValueError("Linha 'Soma Acumulada' não encontrada em historico_scores.csv")

    series = df.loc["Soma Acumulada"]
    return series.apply(lambda value: float(str(value).replace("+", "")))


def render_sentiment_trend(
    scores_path: Path,
    output_path: Optional[Path] = None,
    *,
    ax: Optional[plt.Axes] = None,
    max_points: int = 20,
) -> plt.Figure:
    """Gera gráfico de linha mostrando a evolução da soma acumulada das variações."""
    cumulative = _load_cumulative_series(scores_path)
    if len(cumulative) > max_points:
        cumulative = cumulative.iloc[-max_points:]

    timestamps = pd.to_datetime(cumulative.index.tolist(), errors="coerce")
    time_labels = [
        moment.strftime("%H:%M") if pd.notna(moment) else str(raw) for moment, raw in zip(timestamps, cumulative.index)
    ]
    values = cumulative.values.astype(float)

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        created_fig = True
    else:
        fig = ax.figure
        ax.clear()

    fig.patch.set_facecolor("#161616")
    ax.set_facecolor("#161616")

    x = range(len(time_labels))
    ax.plot(x, values, color="#f0c330", linewidth=2.5)

    ax.set_xticks(list(x))
    ax.set_xticklabels(time_labels, rotation=35, ha="right", fontsize=9, color="#e0e0e0")

    ax.set_title("")
    ax.tick_params(axis="y", left=False, labelleft=False)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.grid(False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#444444")

    if created_fig:
        fig.tight_layout()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, facecolor=fig.get_facecolor())

    if created_fig:
        plt.close(fig)

    return fig

