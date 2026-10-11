# Decision

Phase 1 of Project Q asks for exactly one problem statement, implemented and compared on Processor A and Processor B. Processor C and Processor D are out of scope until shortlisting. The portal cards still mention those later processors; the participant instructions override them.

Deadline used: 12 October 2026, 11:59 PM IST, as stated on Unstop and in the portal FAQ. The proposal PDF's "13 October midnight" was not used as the operating deadline.

## Scoring

Scores are 1–5 against the Phase-1 rubric: correctness, A/B architecture evidence, and insight a later round could use. Feasibility is the remaining-time constraint, not a judging category.

| PS | Rubric fit | Depth | Quantum-specific | Feasible now | Measurable | Distinctive | Risk | Choice |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C1 H₂ VQE | 3 | 3 | 3 | 4 | 4 | 2 | 3 | no |
| O1 Max-Cut | 4 | 3 | 3 | 4 | 4 | 2 | 2 | no |
| S1 Ising ground state | 4 | 4 | 4 | 5 | 5 | 3 | 2 | close |
| S2 Real-time dynamics | 4 | 4 | 4 | 4 | 5 | 3 | 2 | close |
| **S3 Trotter vs noise** | **5** | **5** | **5** | **4** | **5** | **5** | **2** | **yes** |
| Q1 Biomedical VQC | 3 | 3 | 2 | 3 | 3 | 3 | 3 | no |
| P3 PQC benchmark | 3 | 3 | 2 | 3 | 3 | 3 | 3 | no |

S3 is the problem whose question is the hackathon's question: how does architecture change the same quantum solution once noise is present? C1 and O1 are solvable, but they are the default submissions and their architecture story is weaker on these two particular graphs. QML would have to beat a classical baseline honestly, which this instance size does not support. P3 is mostly a classical migration benchmark.

## Why this instance

A 4-spin periodic chain is small enough to validate against exact diagonalization and large enough that the closing bond does not embed in Processor A's tree. Processor B contains a 4-cycle. That is a graph fact, not a fitted narrative. An open chain would have compiled cleanly on both and produced a weak comparison.

## Assumptions

- Official edges are the 5-qubit and 9-qubit lists in the problem-statement framework, not the earlier 7-qubit slide.
- Shared noise is 0.1% on physical single-qubit gates and 0.5% on CX. Virtual `rz` is noiseless. Readout is not in the common benchmark.
- Optimization level 1, Sabre, and the listed seeds are the controlled compiler setting.
- The repository is public so judges can clone it without a private invitation list.
