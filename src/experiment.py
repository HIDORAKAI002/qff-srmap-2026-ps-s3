"""Phase-1 A/B experiment for PS-S3."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .circuits import trotter_circuit
from .metrics import compile_for_processor, logical_fidelity, logical_z0, physical_z
from .problem import exact_evolution, expectation, neel_state, tfim_operator, z0_operator
from .processors import coupling_map, load_benchmark_config, load_processor

ROOT = Path(__file__).resolve().parents[1]


def reference_observable(config: dict, time: float) -> float:
    n = config["n_spins"]
    operator = tfim_operator(n, config["J"], config["g"], config["periodic"])
    state = exact_evolution(operator, neel_state(n), time)
    return expectation(state, z0_operator(n))


def reference_state(config: dict, time: float):
    n = config["n_spins"]
    operator = tfim_operator(n, config["J"], config["g"], config["periodic"])
    return exact_evolution(operator, neel_state(n), time)


def run_point(config: dict, processor: dict, time: float, steps: int, order: int, seed: int) -> dict:
    logical = trotter_circuit(
        config["n_spins"],
        config["J"],
        config["g"],
        time,
        steps,
        order=order,
        periodic=config["periodic"],
        initial=config["initial_state"],
    )
    _routed, executed, metrics = compile_for_processor(
        logical,
        coupling_map(processor),
        config["basis_gates"],
        seed=seed,
        optimization_level=config["optimization_level"],
    )
    logical_ideal = logical_z0(logical)
    physical = metrics["logical_to_physical"][0]
    noisy = physical_z(executed, physical, noisy=True)
    exact = reference_observable(config, time)
    row = {
        "ps": config["ps_code"],
        "processor": processor["name"],
        "time": time,
        "steps": steps,
        "order": order,
        "seed": seed,
        "exact_z0": exact,
        "ideal_trotter_z0": logical_ideal,
        "noisy_z0": noisy,
        "ideal_abs_error": abs(logical_ideal - exact),
        "noisy_abs_error": abs(noisy - exact),
        "noise_induced_error": abs(noisy - logical_ideal),
        **{k: v for k, v in metrics.items() if k != "logical_to_physical"},
        "logical_qubit0_physical": metrics["logical_to_physical"][0],
    }
    # Fidelity is the expensive extra check. Compute it for the primary seed only.
    if seed == config["primary_seed"]:
        ref = reference_state(config, time)
        row["noisy_logical_fidelity"] = logical_fidelity(
            executed, metrics["logical_to_physical"], ref, noisy=True
        )
        row["ideal_logical_fidelity"] = logical_fidelity(
            executed, metrics["logical_to_physical"], ref, noisy=False
        )
    return row


def run_experiment(config: dict | None = None) -> pd.DataFrame:
    config = config or load_benchmark_config()
    processors = [load_processor("processor_A"), load_processor("processor_B")]
    rows: list[dict] = []
    for processor in processors:
        for steps in config["steps"]:
            for seed in config["transpiler_seeds"]:
                rows.append(
                    run_point(
                        config,
                        processor,
                        config["primary_time"],
                        steps,
                        config["primary_order"],
                        seed,
                    )
                )
        # Second-order study on the primary seed only.
        for steps in config["steps"]:
            if 2 in config["trotter_orders"]:
                rows.append(
                    run_point(
                        config,
                        processor,
                        config["primary_time"],
                        steps,
                        2,
                        config["primary_seed"],
                    )
                )
        # Time grid at fixed step count, primary seed, first order.
        for time in config["time_grid"]:
            rows.append(
                run_point(
                    config,
                    processor,
                    time,
                    config["time_grid_steps"],
                    config["primary_order"],
                    config["primary_seed"],
                )
            )
    frame = pd.DataFrame(rows)
    # Logical CX reference: same for both processors, attached for routing-tax plots.
    logical = trotter_circuit(
        config["n_spins"],
        config["J"],
        config["g"],
        config["primary_time"],
        config["steps"][0],
        order=config["primary_order"],
        periodic=config["periodic"],
        initial=config["initial_state"],
    )
    from qiskit import transpile

    logical_cx = {}
    for steps in config["steps"]:
        for order in (1, 2):
            circ = trotter_circuit(
                config["n_spins"],
                config["J"],
                config["g"],
                config["primary_time"],
                steps,
                order=order,
                periodic=config["periodic"],
                initial=config["initial_state"],
            )
            decomposed = transpile(circ, basis_gates=config["basis_gates"], optimization_level=1)
            logical_cx[(order, steps)] = int(decomposed.count_ops().get("cx", 0))
    frame["logical_cx"] = [
        logical_cx.get((int(r.order), int(r.steps)), np.nan) for r in frame.itertuples()
    ]
    frame["routing_cx"] = frame["cx"] - frame["logical_cx"]
    del logical
    return frame


def save_results(frame: pd.DataFrame, config: dict | None = None) -> Path:
    config = config or load_benchmark_config()
    tables = ROOT / "results" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    frame.to_csv(tables / "all_runs.csv", index=False)
    primary = frame[
        (frame["order"] == config["primary_order"])
        & (frame["time"] == config["primary_time"])
        & (frame["seed"] == config["primary_seed"])
    ].copy()
    primary.to_csv(tables / "primary_AB.csv", index=False)
    summary = (
        frame[
            (frame["order"] == config["primary_order"])
            & (frame["time"] == config["primary_time"])
        ]
        .groupby(["processor", "steps"], as_index=False)
        .agg(
            cx_mean=("cx", "mean"),
            cx_std=("cx", "std"),
            depth_mean=("depth", "mean"),
            swap_mean=("swap_count", "mean"),
            swap_std=("swap_count", "std"),
            noisy_abs_error_mean=("noisy_abs_error", "mean"),
            noisy_z0_mean=("noisy_z0", "mean"),
            ideal_abs_error=("ideal_abs_error", "mean"),
            exact_z0=("exact_z0", "first"),
        )
    )
    summary.to_csv(tables / "seed_summary.csv", index=False)
    (tables / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    return tables
