# Research notes

## Official sources

These were read before implementation. Inaccessible pages are not claimed as reviewed.

- Portal learning home and hackathon workspace: https://www.qffsrmap2026.com/learning/hackathon
  The workspace requires a whitelisted Google account. The problem-statement objects are present in the public page bundle. The full participant dossier is the Drive folder linked from that page.
- Unstop listing, Hackathon - Project Q: https://unstop.com/hackathons/hackathon-phase-1-qiskit-fall-fest-2026-srm-university-ap-1758795
  Submission is not on Unstop. The team lead submits a repository URL on the official portal. Deadline printed there: 12 October 2026, 11:59 PM IST.
- Portal FAQ: team size 2–6; Phase 1 deadline 12 October 2026, 11:59 PM IST; Processor C is offline; Processor A/B study is the online task.
- Terms: https://www.qffsrmap2026.com/terms
  Participants retain IP. Plagiarism and misrepresented authorship are disqualifying.
- Drive folder `QFF_HACKATHON_PHASE1_PARTICIPATANTS_INSTRUCTIONSUNSTOP_DRIVE`:
  https://drive.google.com/drive/folders/1caxlXXeqjOkLmXGlimy_Etw0uPHSwyga
  Files used: `Problem_Statment_Details.pdf`, `Processor_AB_Benchmark_Configuration_FINAL.pdf`, `Update_QFF_2026_Hackathon_Phase1_Participant_Instructions (1).pdf.pdf`, `Updated_Challenge_Guide_Phase_1.pdf`, `QFF_IBM_Hackathon_Guideline.pdf`.

Conflicts and the resolution used:

| Topic | Conflict | Resolution |
|---|---|---|
| Processor B size | Slide says 7 qubits; simulation note and problem framework say 9, with an explicit edge list | Use the explicit 9-qubit edge list |
| Processor A shape | Some text says "linear chain"; the simulation edges are a branch | Use the edges `(0,1), (1,2), (1,3), (3,4)` |
| Noise numbers | Illustrative snippets use `p=0.01` and `p=0.005` | Use the framework's shared calibration: ~0.1% one-qubit, ~0.5% two-qubit |
| Processor D | Portal cards ask for `processor_D.json`; participant instructions say Phase 1 stops at A and B | Do not submit a fabricated Processor D as part of Phase 1 |
| Deadline | Proposal text says 13 October midnight; Unstop and FAQ say 12 October 11:59 PM IST | Use 12 October 11:59 PM IST |

## Technical choices

- Product formulas: first-order Lie–Trotter as the required baseline; second-order Suzuki as a labeled supporting study. The second-order state fidelity increases with \(M\), while a single Pauli expectation does not. That is reported rather than smoothed.
- Compiler: Qiskit 2.5 preset pass manager, optimization level 1, so routing remains visible. Level 3 would hide part of the comparison inside peephole cancellation.
- Observable tracking: Aer `save_expectation_value` did not use circuit qubit order on this version. Expectations are computed from the saved density matrix. A unit test locks this down.
- Classical baseline: exact Schrödinger evolution. For \(N=4\) this is the correct baseline. A variational method would add optimizer noise without answering the architecture question.

## References

- H. F. Trotter, "On the product of semi-groups of operators," Proc. Amer. Math. Soc. 10, 545 (1959).
- M. Suzuki, "General theory of fractal path integrals with applications to many-body theories and statistical physics," J. Math. Phys. 32, 400 (1991).
- S. Lloyd, "Universal quantum simulators," Science 273, 1073 (1996).
- Qiskit transpiler and Aer noise-model documentation, versions pinned in `requirements.txt`.
- IBM heavy-hex coupling discussion, used only as background. Processor B in this submission is the organizer edge list, not a claim that the list is a published heavy-hex device.

No other team's repository was copied. The coupling maps are organizer specifications, not original inventions.
