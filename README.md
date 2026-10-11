# PS-S3 — Trotter error versus processor noise

**Qiskit Fall Fest SRMAP 2026 · Project Q · Phase 1**
**Track:** Quantum Simulation
**Problem:** S3, Noise in Trotter Simulation
**Deadline targeted:** 12 October 2026, 11:59 PM IST

A 4-spin periodic Ising quench has one interaction that Processor A cannot host. Processor A is a 5-qubit tree. Processor B's 9-qubit graph contains a 4-cycle, so the same first-order Trotter circuit compiles with **zero SWAPs**. Under one shared noise model, that routing tax — not a different calibration — is what lowers fidelity.

No quantum advantage is claimed. The reference evolution is an exact 16-dimensional classical diagonalization.

## 30-second result

At \(t = 1\) (\(J = g = 1\)), five transpiler seeds:

| M | A CX | A SWAP | B CX | B SWAP | A noisy fidelity | B noisy fidelity | A \(\lvert\Delta\langle Z_0\rangle\rvert\) | B \(\lvert\Delta\langle Z_0\rangle\rvert\) |
|---|-----:|-------:|-----:|-------:|-----------------:|-----------------:|------------------------------------------:|------------------------------------------:|
| 1 | 11 | 1 | 8 | 0 | 0.171 | 0.172 | 0.754 | 0.755 |
| 2 | 25 | 3 | 16 | 0 | 0.595 | 0.614 | 0.139 | 0.132 |
| 4 | 53 | 7 | 32 | 0 | 0.734 | 0.796 | 0.084 | 0.066 |
| 8 | 109 | 15 | 64 | 0 | 0.618 | 0.733 | 0.114 | 0.081 |

The useful depth peaks at **M\* = 4** on both processors. Eight Trotter steps is a better formula and a worse device. Processor B can afford that extra depth; Processor A cannot. Every extra SWAP on A becomes exactly three CX gates.

![Fidelity versus Trotter steps](results/figures/fidelity_vs_steps.png)

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest tests.test_core -v
python main.py
```

`python main.py` rewrites `results/tables/` and `results/figures/`. The checked-in results were produced with Qiskit 2.5.2 and Qiskit Aer 0.17.2. Seeds, the noise model, and the instance are frozen in `configs/benchmark.json`.

## What Phase 1 asked for

Phase 1 is an architecture comparison of **Processor A and Processor B only**. Processor C and a custom Processor D are the offline round. This repository therefore does not invent a Processor D.

Authoritative coupling maps, taken from the organizer simulation configuration:

- Processor A, 5 qubits: `(0,1), (1,2), (1,3), (3,4)`
- Processor B, 9 qubits: `(0,1), (1,2), (1,6), (2,3), (2,5), (2,6), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)`

An earlier slide described Processor B as 7 qubits. The problem-statement framework and the processor-configuration note both give the 9-qubit edge list above. That list is what this benchmark uses.

## Repository map

| Path | Role |
|---|---|
| `main.py` | End-to-end reproducible runner |
| `main.ipynb` | Narrative notebook over the same code and saved results |
| `src/` | Hamiltonian, product formula, compilation, noise, metrics |
| `processors/` | Official A/B JSON definitions |
| `configs/benchmark.json` | Frozen instance, seeds, and noise policy |
| `tests/test_core.py` | Map checks, Trotter convergence, layout tracking |
| `results/` | Tables and figures from the recorded run |
| `report.md` | Methods, numbers, interpretation, limitations |
| `AI_DISCLOSURE.md` | Required disclosure of AI assistance |

## AI assistance

This implementation was produced with AI assistance and then executed and checked in this environment. See `AI_DISCLOSURE.md`. The numerical results are computed, not typed in by hand.
