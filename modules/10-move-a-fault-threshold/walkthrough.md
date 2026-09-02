# P10 walkthrough: Move a Fault Threshold

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you move a Fault Threshold?
2. Recall P09's convention `r=y-y_hat(u)` in `L/min` and state why a Pump-A effectiveness loss is
   negative. Do not introduce a threshold until the sign and unit are explicit.
3. Make one prediction: when `T` rises and `-T` moves farther below zero, should healthy false alarms
   or missed fault samples eventually increase?
4. Run only baseline view 1 in `experiment.m`. Observe the healthy `[-0.1,+0.1] L/min` ripple stay
   above `-0.5 L/min` and the 20% loss residual `[-1.7,-1.5] L/min` stay below it.
5. Advance once to baseline view 2. Read the 60 healthy and 60 fault reference samples: TN/FP is
   `60/0`, detected/missed is `60/0`.
6. Explain why these window fractions are deterministic counts rather than estimated field
   probabilities or event rates.
7. Run sweep 1. Move only `T=[0.06,0.12,0.50,1.49,1.56,1.72] L/min`. Confirm false-alarm fractions
   `[0.25,0,0,0,0,0]` and detection fractions `[1,1,1,1,0.65,0]`.
8. Verify that every residual sample stayed fixed while the signed boundary moved, and that each
   higher-threshold alarm set is a subset of the previous set.
9. Reset `T=0.50 L/min`. Run sweep 2 with conditional loss `[0,4,6,8,20]%`. Confirm post-fault means
   `[0,-0.32,-0.48,-0.64,-1.6] L/min` and detection fractions `[0,0,0.45,1,1]`.
10. Verify that the threshold and every pre-fault residual sample stayed fixed while the fault alarm
    set grew monotonically. Keep conditional magnitude separate from occurrence probability.
11. Open `interactive.m`. Reproduce one threshold change and one conditional-loss change, using
    Reset baseline between them and selecting one visible view at a time.
12. Run the deliberately broken case. Place the boundary at `+T` while retaining `<=`; observe the
    healthy false-alarm fraction change from `0` to `1`.
13. Name the violated assumption: signed threshold placement must preserve P09's negative
    loss-residual convention. Explain why moving `T` is not a repair for that interface defect.
14. Explain why detection is not P11 isolation, P12 posterior reasoning, a recovery command, or
    field performance evidence.
15. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, answer `checks.md` one question
    at a time, and give the two-sentence teach-back.

Static and independent-reference checks do not substitute for executing the model, figures,
controls, callbacks, or numerical assertions in MATLAB.
