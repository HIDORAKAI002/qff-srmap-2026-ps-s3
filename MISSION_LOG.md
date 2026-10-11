# Mission log

Times are IST (UTC+5:30). Deadline: 12 October 2026, 23:59 IST.

## 2026-10-11 21:07

- Mission started. Remaining time about 27 hours. Operating cap requested: 12 hours.
- Opened https://www.qffsrmap2026.com/learning. Public pages load. Hackathon workspace shows "Continue with Google" and requires a whitelisted Gmail. Authentication was not bypassed.

## 2026-10-11 21:15

- Unstop Project Q page: Phase 1 is an online sprint, submission on the official portal, not on Unstop. Deadline 12 October 2026, 11:59 PM IST. Team size on the portal FAQ is 2–6.
- FAQ: study Processor A (described there as 5-qubit linear) and Processor B (described there as 7-qubit heavy-hex), then design Processor D. Later documents contradict the qubit counts and move Processor D to Phase 2.

## 2026-10-11 21:25

- Extracted 20 problem statements from the public hackathon page bundle.
- Downloaded the public Drive dossier. Authoritative maps:
  - A: 5 qubits, edges (0,1), (1,2), (1,3), (3,4)
  - B: 9 qubits, 12 edges listed in `processors/processor_B.json`
- Phase 1 scope confirmed: one PS, benchmark on A and B, structured public repository. C and D are offline.

## 2026-10-11 21:35

- Selected PS-S3. Recorded the comparison in `DECISION.md`.
- Installed Qiskit 2.5.2 and Aer 0.17.2 on Python 3.13.

## 2026-10-11 21:45

- Implemented the product formula, official maps, shared noise model, and layout-safe observable.
- Fixed two measurement bugs before trusting numbers: a second transpile dropped the layout, and Aer `save_expectation_value` did not use circuit qubit order.
- Unit tests passed, including a routing regression on both processors.

## 2026-10-11 21:55

- Full benchmark completed. Five seeds. Processor B inserts zero SWAPs. Processor A inserts 1, 3, 7, 15 SWAPs at M = 1, 2, 4, 8. Noisy fidelity peaks at M = 4 on both devices. Results written to `results/`.
- Report and README written from those tables. No performance number was filled in before the run.

## Next

- Push the repository to GitHub as a public repo so judges can clone it.
- Portal submission is blocked until the team lead signs in with the whitelisted Gmail and a team of at least two exists. Do not invent teammates.
