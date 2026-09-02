# P11 walkthrough: Isolate Competing Faults

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you isolate Competing Faults?
2. Recall P10's command-conditioned sign and unit: Pump-A loss makes
   `r_Q=y_Q-y_Q_hat(u)` negative in `L/min`, and the retained flow test is `r_Q<=-0.50 L/min`.
3. Make one prediction: if pump loss and sensor bias generate identical flow traces, can moving the
   same flow threshold make them distinguishable?
4. Run only baseline view 1 in `experiment.m`. Observe the 20% pump-loss and `1.6 L/min` sensor-bias
   flow traces overlap exactly, with mean `-1.6 L/min`; both cross the P10 boundary.
5. State what is known: a negative discrepancy was detected. State what remains unknown: which
   competing cause generated it.
6. Advance once to baseline view 2. Observe mean pressure `-8 kPa` for pump loss and `0 kPa` for
   flow-sensor bias. Tie this difference to the declared physical-versus-measurement fault model.
7. Advance once to the signature view. Read Pump-A loss as `11`, flow-sensor bias as `10`, and
   healthy as `00`. Explain Hamming distance as a bit mismatch count, not probability.
8. Run sweep 1 while holding bias at zero. Move only Pump-A loss
   `[0,4,8,12,20]%`. Confirm mean flow `[0,-0.32,-0.64,-0.96,-1.6] L/min`, mean pressure
   `[0,-1.6,-3.2,-4.8,-8] kPa`, and codes `00,00,10,11,11`.
9. At 8% loss, identify the coverage gap: flow crossed while pressure did not, so a real pump-loss
   teaching injection matched the sensor signature. A unique match is not automatically correct.
10. Reset pump loss to zero. Run sweep 2 with negative sensor-bias magnitude
    `[0,0.30,0.60,1.00,1.60] L/min`. Confirm codes `00,00,10,10,10` and pressure mean stays zero.
11. Verify sweep isolation: pump-loss changes leave every sensor-bias component zero; sensor-bias
    changes leave the pressure trace and every pump-loss component fixed.
12. Open `interactive.m`. Reproduce one pump-loss change and one sensor-bias change, using Reset
    Pump-A baseline between them and selecting one view at a time.
13. Set both controls nonzero. Read the raw signature and the separate applicability warning: the
    candidate library assumes at most one modeled fault.
14. Run the deliberately broken flow-only case. Confirm Pump-A loss and flow-sensor bias both have
    distance zero and the exact-match count is two.
15. Name the violated assumption: candidate faults must retain distinct signatures over the
    channels actually used. Explain why flow-threshold tuning cannot replace discarded pressure.
16. Explain why deterministic signature isolation is neither P12 posterior reasoning, a field
    isolation rate, nor a recovery or safety decision.
17. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, answer `checks.md` one question
    at a time, and give the two-sentence teach-back.

Static and independent-reference checks do not substitute for executing the model, figures,
controls, callbacks, or numerical assertions in MATLAB.
