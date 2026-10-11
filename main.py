"""Reproducible Phase-1 runner for PS-S3.

Usage:
    python main.py
"""

from __future__ import annotations

import json
from pathlib import Path

from src.experiment import run_experiment, save_results
from src.processors import load_benchmark_config
from src.visualization import write_all

ROOT = Path(__file__).resolve().parent


def main() -> None:
    config = load_benchmark_config()
    frame = run_experiment(config)
    tables = save_results(frame, config)
    write_all(frame, config, ROOT / "results" / "figures")
    primary = frame[
        (frame.order == config["primary_order"])
        & (frame.time == config["primary_time"])
        & (frame.seed == config["primary_seed"])
    ].sort_values(["processor", "steps"])
    columns = [
        "processor",
        "steps",
        "exact_z0",
        "ideal_trotter_z0",
        "noisy_z0",
        "ideal_abs_error",
        "noisy_abs_error",
        "cx",
        "swap_count",
        "depth",
        "noisy_logical_fidelity",
    ]
    print(primary[columns].to_string(index=False))
    summary_path = tables / "primary_preview.json"
    summary_path.write_text(primary[columns].to_json(orient="records", indent=2), encoding="utf-8")
    print(f"\nWrote tables to {tables}")
    print(f"Wrote figures to {ROOT / 'results' / 'figures'}")


if __name__ == "__main__":
    main()
