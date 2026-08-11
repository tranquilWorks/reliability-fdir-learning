# Curriculum readiness audit

**Track:** Reliability, Diagnostics, and Fault-Tolerant Systems

## Baseline conclusion

The repository has 24 uniquely identified modules in a six-phase, prerequisite-ordered sequence. P01 is the complete reference slice; P02-P24 are explicit non-runnable batch scaffolds. The learner flow is read → visualize → move one lever → visualize the delta → read/explain, followed by a broken case, checks, and teach-back.

Static structure and CLI behavior are verified in CI. MATLAB was not available during the 2026-08-11 baseline audit, so numerical execution, UI behavior, and instructional efficacy remain named validation gaps rather than implied evidence.

## Coverage and compounding order

### Phase 1: Reliability fundamentals

- **P01 — Compare Series and Redundant Reliability:** How do required functions, redundancy, and common causes determine mission reliability?
- **P02 — Relate Hazard Rate to Survival:** What inputs, observable effects, and failure modes matter when you relate Hazard Rate to Survival?
- **P03 — Compute Availability from Failure and Repair:** What inputs, observable effects, and failure modes matter when you compute Availability from Failure and Repair?
- **P04 — Expose Common-Cause Failure:** What inputs, observable effects, and failure modes matter when you expose Common-Cause Failure?

### Phase 2: Failure analysis

- **P05 — Build a Fault Tree:** What inputs, observable effects, and failure modes matter when you build a Fault Tree?
- **P06 — Run an FMEA:** What inputs, observable effects, and failure modes matter when you run an FMEA?
- **P07 — Construct a Reliability Block Diagram:** What inputs, observable effects, and failure modes matter when you construct a Reliability Block Diagram?
- **P08 — Prioritize Risk Quantitatively:** What inputs, observable effects, and failure modes matter when you prioritize Risk Quantitatively?

### Phase 3: Detection and isolation

- **P09 — Generate a Diagnostic Residual:** What inputs, observable effects, and failure modes matter when you generate a Diagnostic Residual?
- **P10 — Move a Fault Threshold:** What inputs, observable effects, and failure modes matter when you move a Fault Threshold?
- **P11 — Isolate Competing Faults:** What inputs, observable effects, and failure modes matter when you isolate Competing Faults?
- **P12 — Reason with Bayesian Diagnosis:** What inputs, observable effects, and failure modes matter when you reason with Bayesian Diagnosis?

### Phase 4: Recovery and degradation

- **P13 — Recover with a Watchdog:** What inputs, observable effects, and failure modes matter when you recover with a Watchdog?
- **P14 — Retry Without Creating a Failure Loop:** What inputs, observable effects, and failure modes matter when you retry Without Creating a Failure Loop?
- **P15 — Vote Across Redundant Channels:** What inputs, observable effects, and failure modes matter when you vote Across Redundant Channels?
- **P16 — Enter Graceful Degradation and Safe State:** What inputs, observable effects, and failure modes matter when you enter Graceful Degradation and Safe State?

### Phase 5: Verification of dependability

- **P17 — Inject Faults Systematically:** What inputs, observable effects, and failure modes matter when you inject Faults Systematically?
- **P18 — Design an Accelerated-Life Test:** What inputs, observable effects, and failure modes matter when you design an Accelerated-Life Test?
- **P19 — Measure Maintainability:** What inputs, observable effects, and failure modes matter when you measure Maintainability?
- **P20 — Collect FDIR Evidence:** What inputs, observable effects, and failure modes matter when you collect FDIR Evidence?

### Phase 6: Fault-tolerant architecture

- **P21 — Allocate Redundancy:** What inputs, observable effects, and failure modes matter when you allocate Redundancy?
- **P22 — Trade Coverage Against Complexity:** What inputs, observable effects, and failure modes matter when you trade Coverage Against Complexity?
- **P23 — Contain Fault Propagation:** What inputs, observable effects, and failure modes matter when you contain Fault Propagation?
- **P24 — Build an End-to-End FDIR Architecture:** What inputs, observable effects, and failure modes matter when you build an End-to-End FDIR Architecture?

## Batch readiness gates

A scaffold may become `implemented` only when it has a deterministic model, a sectioned experiment, two independent parameter sweeps, one deliberately broken case, interactive controls, interpretation-focused tutor text, numerical checks, focused static tests, and evidence that says exactly what did and did not run.
