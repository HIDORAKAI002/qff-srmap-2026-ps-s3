"""First- and second-order product formulas for the TFIM."""

from __future__ import annotations

from qiskit import QuantumCircuit


def _apply_zz(circuit: QuantumCircuit, n: int, coupling: float, dt: float, periodic: bool) -> None:
    """exp(-i (-J sum ZZ) dt) = product of RZZ(-2 J dt)."""
    n_bonds = n if periodic else n - 1
    angle = -2.0 * coupling * dt
    for i in range(n_bonds):
        circuit.rzz(angle, i, (i + 1) % n)


def _apply_x(circuit: QuantumCircuit, n: int, field: float, dt: float) -> None:
    """exp(-i (-g sum X) dt) = product of RX(-2 g dt)."""
    angle = -2.0 * field * dt
    for i in range(n):
        circuit.rx(angle, i)


def prepare_initial(circuit: QuantumCircuit, kind: str) -> None:
    n = circuit.num_qubits
    if kind == "neel":
        for qubit in range(1, n, 2):
            circuit.x(qubit)
    elif kind == "plus":
        for qubit in range(n):
            circuit.h(qubit)
    elif kind != "zero":
        raise ValueError(f"unknown initial state: {kind}")


def trotter_circuit(
    n: int,
    coupling: float,
    field: float,
    time: float,
    steps: int,
    order: int = 1,
    periodic: bool = True,
    initial: str = "neel",
) -> QuantumCircuit:
    """Product-formula circuit for evolution to `time` in `steps` slices."""
    if steps < 1:
        raise ValueError("steps must be positive")
    if order not in (1, 2):
        raise ValueError("only Trotter orders 1 and 2 are implemented")
    if time < 0:
        raise ValueError("time must be non-negative")
    circuit = QuantumCircuit(n, name=f"tfim_trotter_p{order}_m{steps}")
    prepare_initial(circuit, initial)
    dt = time / steps
    for _ in range(steps):
        if order == 1:
            _apply_zz(circuit, n, coupling, dt, periodic)
            _apply_x(circuit, n, field, dt)
        else:
            _apply_x(circuit, n, field, dt / 2.0, )
            _apply_zz(circuit, n, coupling, dt, periodic)
            _apply_x(circuit, n, field, dt / 2.0)
    return circuit
