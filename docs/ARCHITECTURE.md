# Architecture

This reference implementation makes each mechanism in *Tiered Autonomy: A
Human-Machine Cybernetic Architecture for LLM-Based Incident Response*
(IEEE SMC 2026) executable and testable. Every module maps to a specific part
of the paper and to the reviewer comments it answers.

## Module map

| Module | Paper section | Reviewer comment answered |
|---|---|---|
| `policy/reversibility_taxonomy.yaml` | Table I (reversibility-typed action taxonomy) | R1.3, R3.4 — operationalize the blast-radius envelope |
| `tiered_autonomy/taxonomy.py` | §III-A (operationalizing the envelope) | R1.3, R3.4 |
| `tiered_autonomy/controller.py` | §III (the five-tier ladder + three tier properties) | R1.6 — runnable prototype |
| `tiered_autonomy/escalation.py` | §III (escalation triggers) | R1.6 |
| `tiered_autonomy/incident.py` | §III-D (bidirectional transitions across one incident) | R1.6 |
| `tiered_autonomy/audit.py` | §III / T3 "execute-then-review" post-hoc audit log | R1.6 |
| `tiered_autonomy/calibration.py` | §III-B (temperature/isotonic scaling + ensemble disagreement) | R1.4, R3.3 |
| `tiered_autonomy/simulator.py` | §IV-B (control-allocation vs capability) | R1.1, R3.1, R1.6 |
| `tiered_autonomy/security.py` | §IV (blast radius as a containment primitive) | adversarial-robustness argument |

## The decision loop

`TierController.decide(action, confidence)` implements the cybernetic loop:

1. **Classify** the action into a reversibility class (`taxonomy.classify`).
2. Optionally **recalibrate** the raw confidence (`calibration`), because the
   paper insists raw token-level log-probabilities are miscalibrated.
3. Apply the **blast-radius bound**: each class has a tier ceiling. R1 is
   always autonomous (T5); **R5 is never autonomous (T1) regardless of
   confidence** — the containment invariant.
4. Apply the **calibration threshold**: for gated classes (R2-R4), the agent
   acts autonomously only if calibrated confidence ≥ τ for that class;
   otherwise it demotes to T2 (advisory) and escalates.
5. Apply **escalation triggers**: confidence below threshold, precondition
   mismatch (mental-model mismatch), operator override, or an unclassifiable
   action all transfer authority toward the human.

Authority is re-evaluated per action, so it moves up and down within a single
incident (`Incident.step`), which is the cybernetic feedback behaviour the
paper argues for.

## Key invariant (tested)

**R5 (unbounded / non-recoverable) is never executed autonomously**, for any
confidence in [0, 1] and even under adversarial confidence inflation. This is
the property that makes the handoff a containment primitive (see
`security.py` / `tests/test_security.py`).
