import unittest

from qiskit.quantum_info import Statevector

from src.circuits import trotter_circuit
from src.metrics import compile_for_processor, logical_z0, physical_z
from src.problem import exact_evolution, expectation, neel_state, tfim_operator, z0_operator
from src.processors import OFFICIAL_EDGES, coupling_map, load_processor


class ProcessorTests(unittest.TestCase):
    def test_official_maps(self):
        processor_a = load_processor("processor_A")
        processor_b = load_processor("processor_B")
        self.assertEqual(processor_a["edges"], OFFICIAL_EDGES["processor_A"])
        self.assertEqual(processor_b["edges"], OFFICIAL_EDGES["processor_B"])
        self.assertEqual(processor_a["num_qubits"], 5)
        self.assertEqual(processor_b["num_qubits"], 9)

    def test_processor_a_is_a_tree(self):
        self.assertEqual(len(OFFICIAL_EDGES["processor_A"]), 4)


class LayoutTests(unittest.TestCase):
    def test_observable_survives_routing(self):
        circuit = trotter_circuit(4, 1.0, 1.0, 0.8, steps=2, order=1)
        expected = logical_z0(circuit)
        for name in ("processor_A", "processor_B"):
            processor = load_processor(name)
            _routed, executed, metrics = compile_for_processor(
                circuit,
                coupling_map(processor),
                ["rz", "sx", "x", "cx"],
                seed=42,
            )
            measured = physical_z(executed, metrics["logical_to_physical"][0], noisy=False)
            self.assertAlmostEqual(measured, expected, places=8, msg=name)


class HamiltonianTests(unittest.TestCase):
    def test_hermitian_and_known_neel_energy(self):
        operator = tfim_operator(4, 1.0, 0.0, periodic=True)
        matrix = operator.to_matrix()
        self.assertLess(abs(matrix - matrix.conj().T).max(), 1e-12)
        # On the Néel state every periodic bond has <ZZ> = -1, so E = -J * 4 * (-1) = 4.
        energy = expectation(neel_state(4), operator)
        self.assertAlmostEqual(energy, 4.0, places=8)

    def test_trotter_converges(self):
        operator = tfim_operator(4, 1.0, 1.0, periodic=True)
        exact = exact_evolution(operator, neel_state(4), 0.6)
        exact_z = expectation(exact, z0_operator(4))
        coarse = trotter_circuit(4, 1.0, 1.0, 0.6, steps=1, order=1)
        fine = trotter_circuit(4, 1.0, 1.0, 0.6, steps=20, order=1)
        z_coarse = expectation(Statevector.from_instruction(coarse), z0_operator(4))
        z_fine = expectation(Statevector.from_instruction(fine), z0_operator(4))
        self.assertLess(abs(z_fine - exact_z), abs(z_coarse - exact_z))
        self.assertLess(abs(z_fine - exact_z), 0.02)

    def test_zero_time_is_neel(self):
        circuit = trotter_circuit(4, 1.0, 1.0, 0.0, steps=1, order=1)
        state = Statevector.from_instruction(circuit)
        self.assertAlmostEqual(abs(state.inner(neel_state(4))) ** 2, 1.0, places=8)


if __name__ == "__main__":
    unittest.main()
