"""Architecture metrics and noise-aware observable extraction."""

from __future__ import annotations

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import DensityMatrix, SparsePauliOp, Statevector, partial_trace, state_fidelity
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator

from .noise import phase1_noise_model


def gate_metrics(circuit: QuantumCircuit) -> dict:
    ops = {name: int(count) for name, count in circuit.count_ops().items()}
    return {
        "depth": int(circuit.depth()),
        "num_qubits": int(circuit.num_qubits),
        "cx": int(ops.get("cx", 0)),
        "swap": int(ops.get("swap", 0)),
        "sx": int(ops.get("sx", 0)),
        "x": int(ops.get("x", 0)),
        "rz": int(ops.get("rz", 0)),
        "operations": ops,
    }


def compile_for_processor(
    circuit: QuantumCircuit,
    coupling: CouplingMap,
    basis: list[str],
    seed: int,
    optimization_level: int = 1,
) -> tuple[QuantumCircuit, QuantumCircuit, dict]:
    """Return (routing circuit, execution circuit, metrics).

    SWAPs are kept visible in the routing circuit and then decomposed locally
    into CX for the circuit that is actually simulated. Both share one layout.
    """
    routed = transpile(
        circuit,
        coupling_map=coupling,
        basis_gates=[*basis, "swap"],
        optimization_level=optimization_level,
        seed_transpiler=seed,
    )
    # Local SWAP -> CX decomposition. A second transpile() call can drop or
    # reinterpret the layout, so it must not be used here.
    executed = routed.decompose(gates_to_decompose="swap")
    if routed.layout is None:
        raise RuntimeError("transpiler did not record a layout")
    layout = [int(q) for q in routed.layout.final_index_layout(filter_ancillas=True)]
    routed_m = gate_metrics(routed)
    executed_m = gate_metrics(executed)
    metrics = {
        "depth": executed_m["depth"],
        "cx": executed_m["cx"],
        "swap_count": routed_m["swap"],
        "physical_qubits": executed_m["num_qubits"],
        "sx": executed_m["sx"],
        "x": executed_m["x"],
        "rz": executed_m["rz"],
        "logical_to_physical": layout,
    }
    return routed, executed, metrics


def logical_z0(circuit: QuantumCircuit) -> float:
    state = Statevector.from_instruction(circuit)
    op = SparsePauliOp.from_sparse_list([("Z", [0], 1.0)], num_qubits=circuit.num_qubits)
    return float(state.expectation_value(op).real)


def _simulator(noisy: bool) -> AerSimulator:
    if noisy:
        return AerSimulator(method="density_matrix", noise_model=phase1_noise_model())
    return AerSimulator(method="density_matrix")


def physical_z(circuit: QuantumCircuit, physical_qubit: int, noisy: bool) -> float:
    # Do not use Aer save_expectation_value: on this Qiskit/Aer pair its qubit
    # index does not match QuantumCircuit qubit order. The density matrix does.
    probed = circuit.copy()
    probed.save_density_matrix(label="rho")
    rho = DensityMatrix(_simulator(noisy).run(probed).result().data(0)["rho"])
    op = SparsePauliOp.from_sparse_list([("Z", [physical_qubit], 1.0)], num_qubits=circuit.num_qubits)
    return float(rho.expectation_value(op).real)


def restoration_circuit(num_qubits: int, logical_to_physical: list[int]) -> QuantumCircuit:
    """Unitary that moves each logical qubit back to wire 0..n-1. Not executed as noise."""
    circuit = QuantumCircuit(num_qubits)
    position = dict(enumerate(logical_to_physical))
    occupant = {phys: logical for logical, phys in position.items()}
    for target in range(len(logical_to_physical)):
        source = position[target]
        if source == target:
            continue
        circuit.swap(source, target)
        displaced = occupant.get(target)
        occupant[source] = displaced
        occupant[target] = target
        position[target] = target
        if displaced is not None:
            position[displaced] = source
    return circuit


def logical_fidelity(
    circuit: QuantumCircuit,
    logical_to_physical: list[int],
    reference: Statevector,
    noisy: bool,
) -> float:
    probed = circuit.copy()
    probed.save_density_matrix(label="rho")
    rho = DensityMatrix(_simulator(noisy).run(probed).result().data(0)["rho"])
    restored = rho.evolve(restoration_circuit(circuit.num_qubits, logical_to_physical))
    ancillas = list(range(len(logical_to_physical), circuit.num_qubits))
    reduced = partial_trace(restored, ancillas) if ancillas else restored
    return float(state_fidelity(reduced, reference))
