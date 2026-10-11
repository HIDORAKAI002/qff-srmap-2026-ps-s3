"""Load and validate the official Processor A/B definitions."""

from __future__ import annotations

import json
from pathlib import Path

from qiskit.transpiler import CouplingMap

ROOT = Path(__file__).resolve().parents[1]
PROCESSOR_DIR = ROOT / "processors"

OFFICIAL_EDGES = {
    "processor_A": [(0, 1), (1, 2), (1, 3), (3, 4)],
    "processor_B": [
        (0, 1),
        (1, 2),
        (1, 6),
        (2, 3),
        (2, 5),
        (2, 6),
        (3, 4),
        (4, 5),
        (5, 6),
        (6, 7),
        (6, 8),
        (8, 0),
    ],
}


def load_processor(name: str) -> dict:
    path = PROCESSOR_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    edges = [tuple(edge) for edge in data["coupling_map"]]
    expected = OFFICIAL_EDGES[name]
    if edges != expected:
        raise ValueError(f"{name} coupling map does not match the official edge list")
    if data["num_qubits"] != (5 if name == "processor_A" else 9):
        raise ValueError(f"{name} qubit count does not match the official benchmark")
    data["edges"] = edges
    data["path"] = str(path)
    return data


def coupling_map(processor: dict) -> CouplingMap:
    return CouplingMap(processor["edges"])


def load_benchmark_config() -> dict:
    with (ROOT / "configs" / "benchmark.json").open(encoding="utf-8") as handle:
        return json.load(handle)
