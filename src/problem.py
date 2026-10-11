"""Transverse-field Ising model used by PS-S2/PS-S3."""

from __future__ import annotations

import numpy as np
from qiskit.quantum_info import SparsePauliOp, Statevector


def pauli_label(n: int, paulis: dict[int, str]) -> str:
    """Little-endian SparsePauliOp label. Qubit 0 is the rightmost character."""
    chars = ["I"] * n
    for qubit, pauli in paulis.items():
        chars[qubit] = pauli
    return "".join(reversed(chars))


def tfim_operator(n: int, coupling: float, field: float, periodic: bool = True) -> SparsePauliOp:
    """H = -J sum Z_i Z_{i+1} - g sum X_i.

    Periodic boundary includes the closing bond Z_{n-1} Z_0. Open boundary omits it.
    """
    if n < 2:
        raise ValueError("TFIM requires at least 2 spins")
    labels: list[str] = []
    coeffs: list[float] = []
    n_bonds = n if periodic else n - 1
    for i in range(n_bonds):
        labels.append(pauli_label(n, {i: "Z", (i + 1) % n: "Z"}))
        coeffs.append(-coupling)
    for i in range(n):
        labels.append(pauli_label(n, {i: "X"}))
        coeffs.append(-field)
    return SparsePauliOp(labels, np.asarray(coeffs, dtype=float)).simplify()


def z0_operator(n: int) -> SparsePauliOp:
    return SparsePauliOp.from_sparse_list([("Z", [0], 1.0)], num_qubits=n)


def neel_state(n: int) -> Statevector:
    """Alternating |0101...⟩ with qubit 0 in |0⟩ and odd qubits flipped."""
    circuit_bits = 0
    for q in range(1, n, 2):
        circuit_bits |= 1 << q
    vector = np.zeros(2**n, dtype=complex)
    vector[circuit_bits] = 1.0
    return Statevector(vector)


def exact_evolution(operator: SparsePauliOp, initial: Statevector, time: float) -> Statevector:
    """Exact Schrödinger evolution |ψ(t)⟩ = exp(-i H t) |ψ(0)⟩."""
    hamiltonian = operator.to_matrix()
    evolution = expm_unitary(hamiltonian, time)
    return Statevector(evolution @ initial.data)


def expm_unitary(hamiltonian: np.ndarray, time: float) -> np.ndarray:
    from scipy.linalg import expm

    return expm(-1j * hamiltonian * time)


def expectation(state: Statevector, operator: SparsePauliOp) -> float:
    value = state.expectation_value(operator)
    return float(np.real(value))
