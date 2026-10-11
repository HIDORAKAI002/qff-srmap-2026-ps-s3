"""Figures for the Phase-1 A/B report."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from .processors import load_processor

COLORS = {"processor_A": "#8F1723", "processor_B": "#1F4E79", "exact": "#111111", "ideal": "#4C78A8"}
LABELS = {"processor_A": "Processor A", "processor_B": "Processor B"}


def _style():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.titleweight": "semibold",
        }
    )


def draw_processors(path: Path) -> None:
    _style()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))
    layouts = {
        "processor_A": {0: (0, 0), 1: (1, 0), 2: (2, 0.7), 3: (2, -0.7), 4: (3, -0.7)},
        "processor_B": {
            0: (0, 1),
            1: (1, 1),
            2: (2, 1),
            3: (3, 1.6),
            4: (4, 1),
            5: (3, 0.4),
            6: (2, 0),
            7: (2, -1),
            8: (1, 0),
        },
    }
    for ax, name in zip(axes, ("processor_A", "processor_B")):
        proc = load_processor(name)
        graph = nx.Graph()
        graph.add_nodes_from(range(proc["num_qubits"]))
        graph.add_edges_from(proc["edges"])
        nx.draw_networkx(
            graph,
            layouts[name],
            ax=ax,
            node_color=COLORS[name],
            node_size=680,
            font_color="white",
            font_size=10,
            width=2.2,
            edge_color="#333333",
        )
        ax.set_title(f"{LABELS[name]} · {proc['num_qubits']} qubits")
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_error_vs_steps(frame: pd.DataFrame, path: Path, time: float, order: int, seed: int) -> None:
    _style()
    subset = frame[
        (frame.time == time) & (frame.order == order) & (frame.seed == seed)
    ].sort_values("steps")
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ideal = subset[subset.processor == "processor_A"]
    ax.plot(ideal.steps, ideal.ideal_abs_error, color=COLORS["ideal"], marker="o", label="Ideal Trotter error")
    for name, group in subset.groupby("processor"):
        ax.plot(
            group.steps,
            group.noisy_abs_error,
            color=COLORS[name],
            marker="s",
            label=f"{LABELS[name]} noisy error",
        )
    ax.set_xlabel("Trotter steps M")
    ax.set_ylabel(r"Absolute error in $\langle Z_0\rangle$")
    ax.set_title(f"Discretization error versus noise at t = {time:g}, order {order}")
    ax.set_xticks(sorted(subset.steps.unique()))
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_resources(frame: pd.DataFrame, path: Path, time: float, order: int) -> None:
    _style()
    subset = frame[(frame.time == time) & (frame.order == order)]
    summary = subset.groupby(["processor", "steps"], as_index=False).agg(
        cx=("cx", "mean"), swap=("swap_count", "mean"), depth=("depth", "mean")
    )
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
    for name, group in summary.groupby("processor"):
        group = group.sort_values("steps")
        axes[0].plot(group.steps, group.cx, color=COLORS[name], marker="o", label=LABELS[name])
        axes[1].plot(group.steps, group.swap, color=COLORS[name], marker="o", label=LABELS[name])
    axes[0].set_title("Executed CX count")
    axes[1].set_title("Inserted SWAP count")
    for ax, ylabel in zip(axes, ("CX gates", "SWAP gates")):
        ax.set_xlabel("Trotter steps M")
        ax.set_ylabel(ylabel)
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_time_series(frame: pd.DataFrame, path: Path, steps: int, order: int, seed: int) -> None:
    _style()
    subset = frame[(frame.steps == steps) & (frame.order == order) & (frame.seed == seed)].sort_values("time")
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    exact = subset[subset.processor == "processor_A"]
    ax.plot(exact.time, exact.exact_z0, color=COLORS["exact"], marker="o", label="Exact")
    ax.plot(exact.time, exact.ideal_trotter_z0, color=COLORS["ideal"], marker="o", label="Ideal Trotter")
    for name, group in subset.groupby("processor"):
        ax.plot(group.time, group.noisy_z0, color=COLORS[name], marker="s", label=f"{LABELS[name]} noisy")
    ax.set_xlabel("Time t  (J = 1)")
    ax.set_ylabel(r"$\langle Z_0\rangle$")
    ax.set_title(f"Néel quench, M = {steps}, first-order Trotter")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_mechanism(frame: pd.DataFrame, path: Path, time: float, order: int, seed: int) -> None:
    _style()
    subset = frame[(frame.time == time) & (frame.order == order) & (frame.seed == seed)]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    offsets = {"processor_A": (8, 6), "processor_B": (8, -12)}
    for name, group in subset.groupby("processor"):
        ax.scatter(group.cx, group.noisy_abs_error, s=70, color=COLORS[name], label=LABELS[name], zorder=3)
        for _, row in group.iterrows():
            ax.annotate(
                f"M={int(row.steps)}",
                (row.cx, row.noisy_abs_error),
                textcoords="offset points",
                xytext=offsets[name],
                fontsize=8,
                color=COLORS[name],
            )
    ax.set_xlabel("Executed CX count")
    ax.set_ylabel(r"Noisy $|\langle Z_0\rangle - \langle Z_0\rangle_{\mathrm{exact}}|$")
    ax.set_title("Routing cost and observable error")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_fidelity(frame: pd.DataFrame, path: Path, time: float, order: int, seed: int) -> None:
    _style()
    subset = frame[(frame.time == time) & (frame.order == order) & (frame.seed == seed)].sort_values("steps")
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ideal = subset[subset.processor == "processor_A"]
    ax.plot(ideal.steps, ideal.ideal_logical_fidelity, color=COLORS["ideal"], marker="o", label="Ideal compiled state")
    for name, group in subset.groupby("processor"):
        ax.plot(
            group.steps,
            group.noisy_logical_fidelity,
            color=COLORS[name],
            marker="s",
            label=f"{LABELS[name]} noisy",
        )
    ax.set_xlabel("Trotter steps M")
    ax.set_ylabel("Fidelity with exact evolved state")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"State fidelity at t = {time:g}, order {order}")
    ax.set_xticks(sorted(subset.steps.unique()))
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_all(frame: pd.DataFrame, config: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    t = config["primary_time"]
    order = config["primary_order"]
    seed = config["primary_seed"]
    draw_processors(out_dir / "processors.png")
    plot_error_vs_steps(frame, out_dir / "error_vs_steps.png", t, order, seed)
    plot_resources(frame, out_dir / "resources_vs_steps.png", t, order)
    plot_time_series(frame, out_dir / "observable_vs_time.png", config["time_grid_steps"], order, seed)
    plot_mechanism(frame, out_dir / "error_vs_cx.png", t, order, seed)
    plot_fidelity(frame, out_dir / "fidelity_vs_steps.png", t, order, seed)
    if not frame[frame.order == 2].empty:
        plot_fidelity(frame, out_dir / "fidelity_order2.png", t, 2, seed)
