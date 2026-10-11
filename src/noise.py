"""Shared Phase-1 noise model.

The problem-statement framework assigns both processors the same calibration:
about 0.1% single-qubit error and 0.5% two-qubit error. Rz is a virtual Z on
this gate set and is left noiseless. Readout error is not part of the frozen
common benchmark.
"""

from __future__ import annotations

from qiskit_aer.noise import NoiseModel, depolarizing_error

SINGLE_QUBIT_P = 0.001
TWO_QUBIT_P = 0.005
SINGLE_QUBIT_GATES = ("x", "sx")
TWO_QUBIT_GATES = ("cx",)


def phase1_noise_model() -> NoiseModel:
    model = NoiseModel()
    model.add_all_qubit_quantum_error(
        depolarizing_error(SINGLE_QUBIT_P, 1), list(SINGLE_QUBIT_GATES)
    )
    model.add_all_qubit_quantum_error(
        depolarizing_error(TWO_QUBIT_P, 2), list(TWO_QUBIT_GATES)
    )
    return model
