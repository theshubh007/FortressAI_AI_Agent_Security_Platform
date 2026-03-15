# Tiered Autonomy — Reference Implementation

A runnable reference implementation and evaluation harness for the five-tier
autonomy architecture described in:

> **Tiered Autonomy: A Human–Machine Cybernetic Architecture for LLM-Based
> Incident Response.** Satish Kathiriya, Shubham J. Kothiya, Sweta Gupta,
> Maulik Jyani. *IEEE International Conference on Systems, Man, and Cybernetics
> (SMC), 2026.*

The paper argues that the performance ceiling of LLM-based incident response is
as much a *control-allocation* problem as a model-capability one, and proposes a
five-tier ladder in which **calibrated confidence** and **action reversibility**
jointly decide whether an agent acts or defers to a human. This repository makes
every load-bearing mechanism in that argument executable, tested, and
reproducible.

> **Provenance.** The architecture was developed during the SMC 2026 submission
> cycle (early 2026); this reference implementation was open-sourced in July 2026
> alongside the camera-ready. Commit history reflects the actual authorship dates.

## What's here

| Component | File | Paper |
|---|---|---|
| Reversibility taxonomy (Table I) as editable policy | `policy/reversibility_taxonomy.yaml`, `tiered_autonomy/taxonomy.py` | §III-A, Table I |
| Five-tier decision controller (the cybernetic loop) | `tiered_autonomy/controller.py`, `escalation.py` | §III |
| Incident timeline + post-hoc audit log (T3) | `tiered_autonomy/incident.py`, `audit.py` | §III, §III-D |
| Calibration (temperature/isotonic + ensemble disagreement, ECE) | `tiered_autonomy/calibration.py` | §III-B |
| Control-allocation simulation harness | `tiered_autonomy/simulator.py` | §IV-B, Table III |
| Blast-radius containment under confidence poisoning | `tiered_autonomy/security.py` | §IV |

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# §III-D worked incident -> real execution trace
python -m examples.worked_incident

# §III-B calibration -> measured ECE + reliability diagrams in figures/
python -m examples.calibration_demo

# §IV blast-radius containment under adversarial confidence poisoning
python -m examples.containment_demo

# §IV-B Table III + robustness sweeps
python -m experiments.reproduce_table3
python -m experiments.miscalibration_sweep
python -m experiments.sensitivity_sweep

pytest -q          # full test suite
```

## Key results (reproducible)

**§III-D worked incident.** A canary rollback (class R2, confidence 0.91 ≥ τ=0.80)
executes autonomously at **T4**; minutes later a credential rotation (class R4,
confidence 0.62 < τ=0.95) **demotes to T2** and escalates to the operator —
authority moving within a single incident.

**§IV-B control allocation** (capability held fixed across policies; 40 seeds):

| Policy | Resolved % | Harm / 100 | Escalated % |
|---|---|---|---|
| Full autonomy | 70.0 | 264.3 | 0.0 |
| Advisory only | 29.7 | 0.0 | 100.0 |
| Global gate (τ=0.76) | 66.2 | 57.2 | 57.1 |
| **Tiered (ours)** | **66.2** | **6.5** | **52.3** |

At matched resolution, reversibility-typed gating cuts harm **8.8×** more than a
single global threshold, and **~41×** less than full autonomy — with identical
agent capability. The benefit degrades gracefully but persists under
overconfidence (40.8× → 15.8× → 8.1× at bias 0.0/0.1/0.2) and across action-mix,
harm-weight, and operator-bandwidth sweeps (12.8×–122×).

**§III-B calibration.** On a synthetic overconfident agent, temperature scaling
reduces Expected Calibration Error from **0.100 → 0.081**; isotonic regression,
which corrects non-uniform miscalibration, reduces it to **0.027** (73%).

**§IV containment.** Under maximal telemetry-manipulation confidence poisoning,
full autonomy incurs 148.9 catastrophic (R5) harm per 100; the tiered policy
holds catastrophic harm at **exactly 0.0**, because unbounded/non-recoverable
(R5) actions are never autonomous regardless of confidence.

## Design invariant (tested)

**R5 (unbounded, non-recoverable) is never executed autonomously** — for any
confidence in [0, 1] and even under adversarial confidence inflation. The
simulator's `tiered` policy is proven equivalent to `TierController.decide` by a
fidelity test over thousands of sampled and boundary cases, so the fast harness
and the shipped controller cannot drift apart.

## Reproducibility

All examples/experiments use fixed seeds (calibration demo `20260714`,
simulation seeds `0..39`). See `docs/ARCHITECTURE.md` for the module-to-paper
mapping.

## Citation

See `CITATION.cff`. Licensed under MIT (`LICENSE`).
