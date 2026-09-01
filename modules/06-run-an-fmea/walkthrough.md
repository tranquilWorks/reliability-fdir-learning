# P06 walkthrough: Run an FMEA

1. Read the guiding question: What inputs, observable effects, and failure modes matter when you run an FMEA?
2. Recall P05's top-down `S OR (A AND B)` tree. State why P06 instead follows each of those three
   modes bottom-up and why a single pump failure degrades redundancy without losing cooling.
3. Define the fixed 1000-hour no-repair mission and the row-under-analysis premise: only the named
   mode is present and companion items are available. Distinguish item function, failure mode,
   example cause, local effect, next-higher effect, end effect, observable effect, and current control.
4. Predict whether an unannunciated Pump-A failure has disappeared from the physical system.
5. Run only the baseline worksheet section of `experiment.m`. Read one complete row from function
   through end effect before comparing rows.
6. Advance once to the occurrence partition. Verify row by row that detected plus latent equals
   physical occurrence and that Pump A gives `0.0700 + 0.0300 = 0.1000` per mission.
7. Interpret the baseline sums as expected listed mode-occurrence counts: `0.2050 = 0.1649 +
   0.0401` per mission. Do not call this a union probability or priority score.
8. Run sweep 1. Increase only Pump-A occurrence `qA`; explain why detected and latent Pump-A paths
   both scale while coverage, the other rows, and the effect chain remain fixed.
9. Reset, then run sweep 2. Increase only Pump-A coverage `cA`; explain why detected occurrence
   rises, latent occurrence falls, and physical occurrence remains `0.10`.
10. Open `interactive.m`. Select one FMEA row, use one view at a time, and reset before comparing an
    occurrence change with a coverage change.
11. Run the deliberately broken section. Grant the logs perfect specificity, unique attribution,
    and one true-positive record per detection. At `qA=0.10, cA=0`, diagnose why even this favorable
    log-only worksheet reports zero although the entire `0.10` occurrence path is latent; explain why
    raw logs can additionally overcount or misattribute modes.
12. Run `run_checks.m` in MATLAB when a MATLAB runtime is available, answer the prompts in
    `checks.md` one at a time, and teach back the row structure, both lever mechanisms, and the
    broken assumption in two sentences.

Static repository checks do not substitute for executing the worksheet, figures, controls, or
numerical assertions in MATLAB.
