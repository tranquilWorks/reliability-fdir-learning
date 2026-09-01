# P09 walkthrough: Generate a Diagnostic Residual

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you generate a Diagnostic Residual?
2. Recall P08's `A only` degraded-success scenario. Explain why its priority motivates Pump-A
   monitoring without turning every Pump-A loss into mission failure.
3. Separate P08 occurrence probability `q_A` from P09 conditional effectiveness-loss magnitude `L`.
   State the residual convention `r=y-y_hat(u)` and its `L/min` unit.
4. Make one prediction: should the residual jump when the known normalized speed command changes
   normally from `0.5` to `0.8` at 10 seconds?
5. Run only baseline view 1 in `experiment.m`. Follow the measured and predicted flow from `5` to
   `8 L/min`; then observe measured flow fall to a `6.4 L/min` mean after the 20% loss at 20 seconds.
6. Advance once to baseline residual view 2. Verify command-step mean change `0 L/min`, post-fault
   mean `-1.6 L/min`, and the sign interpretation “measured below expected.”
7. Advance once to the decomposition. Add model mismatch, effectiveness-loss, and deterministic
   ripple components and confirm their maximum closure error is near machine precision.
8. Run sweep 1. Change only `L=[0,0.05,0.10,0.20,0.30]`; reproduce post-fault means
   `[0,-0.4,-0.8,-1.6,-2.4] L/min` and verify every pre-fault signal stays fixed.
9. Reset. Run sweep 2 and change only `K_hat=[8,9,10,11,12] L/min per normalized command`. Confirm
   physical measured flow stays fixed, healthy high-command means become
   `[1.6,0.8,0,-0.8,-1.6] L/min`, and the fault-induced shift remains `-1.6 L/min`.
10. At `K_hat=8`, identify cancellation: the post-fault mean is zero even though the 20% physical
    loss remains. Explain why zero residual at one operating point is not proof of health.
11. Open `interactive.m`. Reproduce one loss change and one predictor-gain change, using Reset
    baseline between them and selecting one visible view at a time.
12. Run the deliberately broken healthy case. The frozen predictor omits the known command and
    produces a `+3 L/min` mean step at 10 seconds while the correct residual changes by zero.
13. Name the violated assumption: the nominal predictor must condition on every known input that
    materially drives the measurement. Do not repair it with a threshold.
14. Explain why the residual is a discrepancy rather than a P10 alarm, a P11 unique diagnosis, a
    P12 posterior, or a recovery command. Distinguish deterministic ripple from field noise evidence.
15. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, answer `checks.md` one question
    at a time, and give the two-sentence teach-back.

Static and independent-reference checks do not substitute for executing the model, figures,
controls, callbacks, or numerical assertions in MATLAB.
