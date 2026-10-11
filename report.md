# Report — PS-S3, Trotter error versus noise

## Problem

Simulate a sudden quench of a 4-spin transverse-field Ising chain and measure how processor connectivity changes the accuracy of a digital simulation once gate noise is included.

The instance, fixed before looking at the A/B outcome:

- \(N = 4\) spins, periodic boundary
- \(H = -J\sum_{i} Z_i Z_{i+1} - g\sum_i X_i\), with \(J = g = 1\)
- initial Néel state \(|0101\rangle\) (qubit 0 in \(|0\rangle\))
- primary observable \(\langle Z_0\rangle\)
- primary time \(t = 1\), inside the suggested window \(t \le 2\)
- first-order product formula at \(M \in \{1, 2, 4, 8\}\)
- exact reference from `scipy.linalg.expm` on the \(16\times 16\) Hamiltonian

Periodic boundary is allowed by the companion statement PS-S1 and is the right probe here. An open chain of four spins embeds in both graphs, so it would hide the architectural difference. The closing bond \(Z_3 Z_0\) does not.

## Method

Each Trotter slice is

\[
e^{-iH\Delta t} \approx e^{-i H_{ZZ}\Delta t}\, e^{-i H_X\Delta t},
\]

implemented as `RZZ(-2JΔt)` and `RX(-2gΔt)`. Those angles follow from `RZZ(θ) = exp(-i θ ZZ / 2)` and `RX(θ) = exp(-i θ X / 2)`. A unit test checks that the formula converges to the exact observable as \(M\) increases.

The logical circuit is transpiled with Qiskit preset level 1 onto each coupling map, with `swap` left in the basis so inserted SWAPs can be counted. SWAPs are then decomposed locally into CX. A second `transpile()` call is not used for that step: on Qiskit 2.5 it can drop the layout and point the observable at the wrong qubit. A regression test checks that the ideal compiled \(\langle Z_0\rangle\) matches the logical circuit on both processors.

Noise is the shared Phase-1 calibration stated in the problem-statement framework, not a device calibration:

- depolarizing probability \(0.001\) on `x` and `sx`
- depolarizing probability \(0.005\) on `cx`
- `rz` treated as a virtual Z and left noiseless
- no readout error in the common benchmark

The same channel is attached to A and B. Connectivity is the controlled variable. Expectations and fidelities are taken from the Aer density matrix, so the comparison is not confounded by shot noise. Five transpiler seeds, `{0, 1, 7, 21, 42}`, test layout luck. CX and SWAP counts did not change across those seeds.

## Processors

Processor A is a tree: four edges, five qubits, no cycle. A 4-cycle cannot be a subgraph. Sabre therefore inserts SWAPs for the periodic bond.

Processor B contains the 4-cycle `1—2—5—6—1`. The compiler embeds the ring there and inserts **zero SWAPs** at every \(M\) tested.

Routing tax on A is exact: extra CX \(= 3 \times\) SWAP count. At \(M = 8\) that is 45 extra CX gates on top of 64 algorithmic CX gates, a 70% two-qubit overhead. Processor B's overhead is zero.

## Results

Primary comparison, \(t = 1\), first order. Fidelity is the seed-42 density-matrix fidelity with the exact evolved state. Resource and \(\langle Z_0\rangle\) errors are means over five seeds; their standard deviations are below \(0.003\) for the observable error and zero for CX and SWAP counts.

| M | Ideal fidelity | A noisy fidelity | B noisy fidelity | A \(\lvert\Delta Z_0\rvert\) | B \(\lvert\Delta Z_0\rvert\) | A CX / SWAP | B CX / SWAP |
|---|---------------:|-----------------:|-----------------:|-----------------------------:|-----------------------------:|------------:|------------:|
| 1 | 0.178 | 0.171 | 0.172 | 0.754 | 0.755 | 11 / 1 | 8 / 0 |
| 2 | 0.662 | 0.595 | 0.614 | 0.139 | 0.132 | 25 / 3 | 16 / 0 |
| 4 | 0.921 | 0.734 | 0.796 | 0.084 | 0.066 | 53 / 7 | 32 / 0 |
| 8 | 0.981 | 0.618 | 0.733 | 0.114 | 0.081 | 109 / 15 | 64 / 0 |

Exact \(\langle Z_0\rangle(t=1) = 0.348\). The ideal first-order circuit moves from \(-0.416\) at \(M=1\) to \(0.341\) at \(M=8\).

The time series at fixed \(M=4\) shows the same ordering at every sampled time from \(0.25\) to \(2.0\): exact, then ideal Trotter, then noisy B, then noisy A. Noise pulls \(\langle Z_0\rangle\) toward zero. It does not invent a different oscillation.

## Interpretation

1. **At \(M=1\), architecture does not matter.** Both fidelities are about \(0.17\). The product formula is the error. Adding connectivity cannot repair a bad formula.
2. **From \(M=2\) onward, the tree pays a routing tax and the cycle does not.** The tax is deterministic across seeds: 1, 3, 7, then 15 SWAPs.
3. **The useful depth is \(M^\*=4\), not the largest \(M\).** Ideal fidelity is still rising at \(M=8\) (0.981), but noisy fidelity has already peaked at \(M=4\) and fallen. This is the tradeoff the problem asks for: \(\varepsilon_{\mathrm{total}} \approx \varepsilon_{\mathrm{Trotter}}(M) + \varepsilon_{\mathrm{hardware}}(D(M))\).
4. **Processor B shifts that tradeoff, it does not remove it.** B is better at \(M=4\) and still better at \(M=8\), but B also gets worse from \(M=4\) to \(M=8\). A 4-cycle is not a noise-free processor. It only avoids SWAP noise.
5. **One observable can lie.** Second-order Trotter at \(M=1\) has ideal fidelity only \(0.348\) but \(\lvert\Delta\langle Z_0\rangle\rvert = 0.008\). The observable happened to land near the exact value. Fidelity is the honest state-quality metric; \(\langle Z_0\rangle\) is the requested problem metric. Both are reported.

## What this says for Phase 2

Phase 1 stops at A and B. The architecture lesson to carry forward is specific: the coupling graph should contain the interaction graph of the Hamiltonian as a subgraph. For this periodic chain, that subgraph is a 4-cycle, which B has and A does not. A later Processor D that only adds degree, without hosting the actual bonds, would not be justified by these measurements.

## Limitations

- Four spins are classically trivial. This is a controlled architecture experiment, not evidence of quantum advantage.
- The noise model is the organizer's approximate shared calibration, not a measured IBM backend. `rz` is assumed virtual. Readout error is omitted because the frozen common benchmark does not specify it.
- Optimization level 1 and Sabre are one compiler point, not every possible routing strategy. The zero-SWAP embedding on B is a property of the graph, so a better compiler cannot remove A's need to route a cycle onto a tree.
- Density-matrix noise is the average channel. It is not a single-shot device trajectory.
- Processor B is the official 9-qubit edge list. It is not the 7-qubit heavy-hex cartoon in an earlier slide.
- Second-order results are a supporting study. The common benchmark is first order, as specified.

## Reproducibility

```bash
pip install -r requirements.txt
python -m unittest tests.test_core -v
python main.py
```

Recorded environment: Python 3.13, Qiskit 2.5.2, Qiskit Aer 0.17.2. Primary seed 42. Tables are in `results/tables/all_runs.csv`.
