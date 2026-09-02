from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/10-move-a-fault-threshold"
P09_FOLDER = ROOT / "modules/09-generate-a-diagnostic-residual"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you "
    "move a Fault Threshold?"
)


def reference_decision(
    threshold_lpm: float,
    loss_fraction: float,
    ripple_lpm: float = 0.10,
) -> dict[str, object]:
    times = [sample / 10 for sample in range(301)]
    command = [0.5 if time < 10 else 0.8 for time in times]
    fault_active = [time >= 20 for time in times]
    ripple = [
        ripple_lpm * math.sin(2 * math.pi * 0.5 * time) for time in times
    ]
    fault_residual = [
        -10 * loss_fraction * active * speed
        for active, speed in zip(fault_active, command)
    ]
    residual = [
        fault_value + nuisance
        for fault_value, nuisance in zip(fault_residual, ripple)
    ]
    alarm = [value <= -threshold_lpm for value in residual]
    broken_alarm = [value <= threshold_lpm for value in residual]
    healthy_window = [12 <= time < 18 for time in times]
    fault_window = [22 <= time < 28 for time in times]

    def count(values: list[bool], window: list[bool]) -> int:
        return sum(value and selected for value, selected in zip(values, window))

    def fraction(values: list[bool], window: list[bool]) -> float:
        return count(values, window) / sum(window)

    false_count = count(alarm, healthy_window)
    detection_count = count(alarm, fault_window)

    return {
        "times": times,
        "command": command,
        "fault_active": fault_active,
        "ripple": ripple,
        "fault_residual": fault_residual,
        "residual": residual,
        "alarm": alarm,
        "broken_alarm": broken_alarm,
        "healthy_window": healthy_window,
        "fault_window": fault_window,
        "false_count": false_count,
        "true_negative_count": sum(healthy_window) - false_count,
        "detection_count": detection_count,
        "missed_count": sum(fault_window) - detection_count,
        "false_fraction": fraction(alarm, healthy_window),
        "detection_fraction": fraction(alarm, fault_window),
        "broken_false_fraction": fraction(broken_alarm, healthy_window),
    }


class P10ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P10"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p10_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 10)
        self.assertEqual(self.module["title"], "Move a Fault Threshold")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 3)
        self.assertEqual(self.module["phase_title"], "Detection and isolation")
        self.assertEqual(self.module["slug"], "move-a-fault-threshold")
        self.assertEqual(
            self.module["folder"], "modules/10-move-a-fault-threshold"
        )
        self.assertEqual(self.module["prerequisites"], ["P09"])
        self.assertEqual(self.module["implementation_batch"], "P10")
        self.assertEqual(self.module["status"], "implemented")
        self.assertEqual(self.module["evidence_level"], "simulated")
        required = {
            "README.md",
            "lesson.m",
            "model.m",
            "experiment.m",
            "interactive.m",
            "lesson.md",
            "walkthrough.md",
            "checks.md",
            "run_checks.m",
        }
        self.assertTrue(required <= self.text.keys())
        for name in required:
            with self.subTest(newline=name):
                payload = (FOLDER / name).read_bytes()
                self.assertGreater(len(payload), 80)
                self.assertTrue(payload.endswith(b"\n"))
                self.assertFalse(payload.endswith(b"\n\n"))

    def test_guiding_question_prerequisite_and_phase_boundary_are_visible(self):
        for name in (
            "README.md",
            "lesson.md",
            "walkthrough.md",
            "lesson.m",
            "experiment.m",
        ):
            with self.subTest(name=name):
                normalized = " ".join(self.text[name].replace("%", " ").split())
                self.assertIn(QUESTION, normalized)
        for name in (
            "README.md",
            "lesson.md",
            "walkthrough.md",
            "checks.md",
            "lesson.m",
            "experiment.m",
        ):
            with self.subTest(name=name):
                self.assertIn("P09", self.text[name])
        combined = "\n".join(self.text.values())
        for token in (
            "r=y-y_hat",
            "negative residual",
            "L/min",
            "conditional",
            "not an occurrence probability",
            "P11",
            "P12",
            "recovery",
        ):
            self.assertIn(token.lower(), combined.lower())

    def test_model_exposes_transparent_signed_threshold_equations(self):
        model = self.text["model.m"]
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "timeSeconds=(0:samplePeriodSeconds:30).';",
            "deterministicRippleLpm=rippleAmplitudeLpm*sin(2*pi*rippleFrequencyHz*timeSeconds);",
            "faultResidualLpm=-nominalGainLpmPerCommand*effectivenessLossFraction*faultActive.*speedCommand;",
            "residualLpm=faultResidualLpm+deterministicRippleLpm;",
            "signedThresholdLpm=-thresholdMagnitudeLpm*ones(size(timeSeconds));",
            "decisionStatisticLpm=-residualLpm;",
            "alarm=residualLpm<=signedThresholdLpm;",
            "brokenSignedThresholdLpm=thresholdMagnitudeLpm*ones(size(timeSeconds));",
            "brokenWrongSignAlarm=residualLpm<=brokenSignedThresholdLpm;",
        ):
            self.assertIn(equation, compact)
        for output in (
            "trueNegativeCount",
            "falseAlarmCount",
            "detectionCount",
            "missedDetectionCount",
            "falseAlarmSampleFraction",
            "detectionSampleFraction",
            "alarmMarginLpm",
            "decisionEquation",
            "fractionMeaning",
            "scopeBoundary",
        ):
            self.assertIn(output, model)
        self.assertEqual(model.count("(1,1) double"), 3)
        self.assertIn("{'real','finite','>=',0,'<=',10}", model)
        self.assertGreaterEqual(model.count("{'real','finite','>=',0,'<=',1}"), 2)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "scatter(",
            "uifigure",
            "uiaxes",
        ):
            self.assertNotIn(presentation_call, model.lower())

    def test_baseline_signals_counts_and_limits_are_independently_known(self):
        reference = reference_decision(0.50, 0.20)
        self.assertEqual(len(reference["times"]), 301)
        self.assertEqual(sum(reference["healthy_window"]), 60)
        self.assertEqual(sum(reference["fault_window"]), 60)
        healthy_values = [
            value
            for value, selected in zip(
                reference["residual"], reference["healthy_window"]
            )
            if selected
        ]
        fault_values = [
            value
            for value, selected in zip(
                reference["residual"], reference["fault_window"]
            )
            if selected
        ]
        self.assertAlmostEqual(sum(healthy_values) / 60, 0.0, places=15)
        self.assertAlmostEqual(sum(fault_values) / 60, -1.6, places=14)
        self.assertAlmostEqual(min(healthy_values), -0.1, places=14)
        self.assertAlmostEqual(max(healthy_values), 0.1, places=14)
        self.assertAlmostEqual(min(fault_values), -1.7, places=14)
        self.assertAlmostEqual(max(fault_values), -1.5, places=14)
        self.assertEqual(reference["false_fraction"], 0)
        self.assertEqual(reference["detection_fraction"], 1)
        checks = self.text["run_checks.m"]
        for token in (
            "fixed 301-sample deterministic record",
            "exactly three ripple cycles",
            "Healthy and baseline fault means must be 0 and -1.6 L/min",
            "Reference-window ranges must be [-0.1,0.1] and [-1.7,-1.5] L/min",
            "TN/FP/detected/missed = 60/0/60/0",
            "Confusion counts and deterministic sample fractions must close exactly",
        ):
            self.assertIn(token, checks)

    def test_p09_to_p10_matched_residual_behavior_contract_is_regressed(self):
        p09_model = (P09_FOLDER / "model.m").read_text(encoding="utf-8")
        p10_model = self.text["model.m"]
        shared_names = (
            "samplePeriodSeconds",
            "commandStepTimeSeconds",
            "faultTimeSeconds",
            "lowCommand",
            "highCommand",
            "nominalGainLpmPerCommand",
            "rippleFrequencyHz",
        )

        def scalar_contract(source: str) -> dict[str, float]:
            contract = {}
            for name in shared_names:
                matches = re.findall(
                    rf"(?m)^\s*{re.escape(name)}\s*=\s*"
                    r"(-?(?:\d+(?:\.\d*)?|\.\d+))\s*;",
                    source,
                )
                self.assertEqual(
                    len(matches),
                    1,
                    f"{name} must have one transparent scalar assignment",
                )
                contract[name] = float(matches[0])
            return contract

        p09_contract = scalar_contract(p09_model)
        p10_contract = scalar_contract(p10_model)
        self.assertEqual(p10_contract, p09_contract)
        predictor_defaults = re.findall(
            r"predictorGainLpmPerCommand\s+\(1,1\)\s+double\s*=\s*"
            r"(-?(?:\d+(?:\.\d*)?|\.\d+))",
            p09_model,
        )
        self.assertEqual(len(predictor_defaults), 1)
        matched_predictor_gain = float(predictor_defaults[0])
        self.assertEqual(
            matched_predictor_gain,
            p09_contract["nominalGainLpmPerCommand"],
        )

        p09_compact = re.sub(r"\s+|\.\.\.", "", p09_model)
        p10_compact = re.sub(r"\s+|\.\.\.", "", p10_model)
        for source in (p09_compact, p10_compact):
            self.assertIn("timeSeconds=(0:samplePeriodSeconds:30).';", source)
            self.assertIn(
                "speedCommand(timeSeconds>=commandStepTimeSeconds)=highCommand;",
                source,
            )
            self.assertIn("faultActive=double(timeSeconds>=faultTimeSeconds);", source)
            self.assertIn(
                "deterministicRippleLpm=rippleAmplitudeLpm*"
                "sin(2*pi*rippleFrequencyHz*timeSeconds);",
                source,
            )
        for equation in (
            "faultFlowLossLpm=nominalGainLpmPerCommand*"
            "effectivenessLossFraction*faultActive.*speedCommand;",
            "trueFlowLpm=healthyFlowLpm-faultFlowLossLpm;",
            "measuredFlowLpm=trueFlowLpm+deterministicRippleLpm;",
            "predictedFlowLpm=predictorGainLpmPerCommand*speedCommand;",
            "residualLpm=measuredFlowLpm-predictedFlowLpm;",
        ):
            self.assertIn(equation, p09_compact)
        for equation in (
            "faultResidualLpm=-nominalGainLpmPerCommand*"
            "effectivenessLossFraction*faultActive.*speedCommand;",
            "residualLpm=faultResidualLpm+deterministicRippleLpm;",
        ):
            self.assertIn(equation, p10_compact)
        for source in (p09_model, p10_model):
            self.assertIn("r(t) = y(t) - y_hat(t | u(t))", source)
            self.assertIn("out.residualUnit = 'L/min'", source)
        self.assertIn(
            "highCommandHealthyWindow=timeSeconds>=12&timeSeconds<18;",
            p09_compact,
        )
        self.assertIn(
            "postFaultWindow=timeSeconds>=22&timeSeconds<28;",
            p09_compact,
        )
        self.assertIn(
            "healthyReferenceWindow=timeSeconds>=12&timeSeconds<18;",
            p10_compact,
        )
        self.assertIn(
            "faultReferenceWindow=timeSeconds>=22&timeSeconds<28;",
            p10_compact,
        )

        sample_period = p10_contract["samplePeriodSeconds"]
        sample_count = round(30 / sample_period) + 1
        times = [sample * sample_period for sample in range(sample_count)]
        command = [
            p10_contract["lowCommand"]
            if time < p10_contract["commandStepTimeSeconds"]
            else p10_contract["highCommand"]
            for time in times
        ]
        fault_active = [
            time >= p10_contract["faultTimeSeconds"] for time in times
        ]
        nominal_gain = p10_contract["nominalGainLpmPerCommand"]
        ripple_frequency = p10_contract["rippleFrequencyHz"]

        for loss_fraction, ripple_amplitude in (
            (0.0, 0.0),
            (0.06, 0.10),
            (0.20, 0.10),
            (1.0, 1.0),
        ):
            with self.subTest(
                loss_fraction=loss_fraction,
                ripple_amplitude=ripple_amplitude,
            ):
                ripple = [
                    ripple_amplitude
                    * math.sin(2 * math.pi * ripple_frequency * time)
                    for time in times
                ]
                p09_matched_residual = [
                    (
                        nominal_gain * speed
                        - nominal_gain * loss_fraction * active * speed
                        + nuisance
                    )
                    - matched_predictor_gain * speed
                    for speed, active, nuisance in zip(
                        command, fault_active, ripple
                    )
                ]
                p10_residual = [
                    -nominal_gain * loss_fraction * active * speed + nuisance
                    for speed, active, nuisance in zip(
                        command, fault_active, ripple
                    )
                ]
                for p09_value, p10_value in zip(
                    p09_matched_residual, p10_residual
                ):
                    self.assertAlmostEqual(p10_value, p09_value, places=14)

    def test_inclusive_zero_full_and_resource_limits_are_independently_known(self):
        inclusive = reference_decision(1.60, 0.20, 0)
        self.assertEqual(inclusive["detection_fraction"], 1)
        self.assertTrue(
            all(
                value == -1.60
                for value, selected in zip(
                    inclusive["residual"], inclusive["fault_window"]
                )
                if selected
            )
        )

        zero_loss = reference_decision(0.50, 0, 0.10)
        self.assertEqual(zero_loss["detection_fraction"], 0)
        full_loss = reference_decision(0.50, 1, 0)
        self.assertEqual(full_loss["detection_fraction"], 1)
        self.assertTrue(
            all(
                value == -8
                for value, selected in zip(
                    full_loss["residual"], full_loss["fault_window"]
                )
                if selected
            )
        )

        zero_boundary = reference_decision(0, 0, 0)
        self.assertEqual(zero_boundary["false_fraction"], 1)
        self.assertEqual(zero_boundary["detection_fraction"], 1)
        maximum_supported = reference_decision(10, 1, 1)
        self.assertEqual(maximum_supported["detection_fraction"], 0)
        self.assertTrue(all(math.isfinite(value) for value in maximum_supported["residual"]))

    def test_threshold_sweep_has_exact_isolated_monotone_reference_behavior(self):
        thresholds = [0.06, 0.12, 0.50, 1.49, 1.56, 1.72]
        references = [reference_decision(value, 0.20) for value in thresholds]
        false_fractions = [item["false_fraction"] for item in references]
        detection_fractions = [item["detection_fraction"] for item in references]
        self.assertEqual(false_fractions, [0.25, 0, 0, 0, 0, 0])
        self.assertEqual(detection_fractions, [1, 1, 1, 1, 0.65, 0])
        baseline_residual = references[0]["residual"]
        for item in references[1:]:
            self.assertEqual(item["residual"], baseline_residual)
        for previous, current in zip(references, references[1:]):
            self.assertTrue(
                all(
                    not later or earlier
                    for earlier, later in zip(previous["alarm"], current["alarm"])
                )
            )
        experiment = self.text["experiment.m"]
        self.assertIn(
            "thresholdSweepLpm = [0.06 0.12 0.50 1.49 1.56 1.72]",
            experiment,
        )
        self.assertIn("changed = model(thresholdSweepLpm(k),0.20,0.10)", experiment)
        checks = self.text["run_checks.m"]
        self.assertIn("leave every residual component fixed", checks)
        self.assertIn("make each alarm set a subset", checks)

    def test_loss_sweep_has_exact_isolated_monotone_reference_behavior(self):
        losses = [0, 0.04, 0.06, 0.08, 0.20]
        references = [reference_decision(0.50, value) for value in losses]
        detection_fractions = [item["detection_fraction"] for item in references]
        self.assertEqual(detection_fractions, [0, 0, 0.45, 1, 1])
        expected_means = [0, -0.32, -0.48, -0.64, -1.6]
        for item, expected in zip(references, expected_means):
            fault_values = [
                value
                for value, selected in zip(item["residual"], item["fault_window"])
                if selected
            ]
            self.assertAlmostEqual(sum(fault_values) / 60, expected, places=14)
            self.assertEqual(item["false_fraction"], 0)
        for item in references:
            self.assertEqual(item["residual"][:200], references[0]["residual"][:200])
        for previous, current in zip(references, references[1:]):
            previous_fault_alarm = [
                value
                for value, selected in zip(previous["alarm"], previous["fault_window"])
                if selected
            ]
            current_fault_alarm = [
                value
                for value, selected in zip(current["alarm"], current["fault_window"])
                if selected
            ]
            self.assertTrue(
                all(
                    not earlier or later
                    for earlier, later in zip(
                        previous_fault_alarm, current_fault_alarm
                    )
                )
            )
        experiment = self.text["experiment.m"]
        self.assertIn("lossSweep = [0 0.04 0.06 0.08 0.20]", experiment)
        self.assertIn("changed = model(0.50,lossSweep(k),0.10)", experiment)
        checks = self.text["run_checks.m"]
        self.assertIn("leave every pre-fault residual and alarm fixed", checks)
        self.assertIn("must not remove an existing fault-window alarm", checks)

    def test_ripple_control_has_exact_isolated_reference_behavior(self):
        ripple_values = [0, 0.40, 0.60, 0.70, 1.00]
        references = [
            reference_decision(0.55, 0.20, ripple) for ripple in ripple_values
        ]
        self.assertEqual(
            [item["false_count"] for item in references], [0, 0, 9, 15, 21]
        )
        self.assertEqual(
            [item["false_fraction"] for item in references],
            [0, 0, 0.15, 0.25, 0.35],
        )
        self.assertEqual(
            [item["detection_count"] for item in references], [60] * 5
        )
        self.assertEqual(
            [item["detection_fraction"] for item in references], [1] * 5
        )

        fixed_command = references[0]["command"]
        fixed_fault_active = references[0]["fault_active"]
        fixed_fault_residual = references[0]["fault_residual"]
        previous_healthy_alarm = [False] * 60
        for item in references:
            self.assertEqual(
                item["true_negative_count"] + item["false_count"], 60
            )
            self.assertEqual(item["detection_count"] + item["missed_count"], 60)
            self.assertEqual(item["command"], fixed_command)
            self.assertEqual(item["fault_active"], fixed_fault_active)
            self.assertEqual(item["fault_residual"], fixed_fault_residual)
            for residual, fault, nuisance in zip(
                item["residual"], item["fault_residual"], item["ripple"]
            ):
                self.assertAlmostEqual(residual, fault + nuisance, places=15)
            current_healthy_alarm = [
                value
                for value, selected in zip(
                    item["alarm"], item["healthy_window"]
                )
                if selected
            ]
            self.assertTrue(
                all(
                    not earlier or later
                    for earlier, later in zip(
                        previous_healthy_alarm, current_healthy_alarm
                    )
                )
            )
            previous_healthy_alarm = current_healthy_alarm

        interactive = re.sub(r"\s+|\.\.\.", "", self.text["interactive.m"])
        self.assertIn(
            "out=modelForThisModule(thresholdControl.Value,"
            "lossControl.Value/100,rippleControl.Value);",
            interactive,
        )
        checks = re.sub(
            r"'\s*\.\.\.\s*\n\s*'", "", self.text["run_checks.m"]
        )
        for token in (
            "rippleSweepLpm = [0 0.40 0.60 0.70 1.00]",
            "leave command, fault signature, and threshold fixed",
            "counts and fractions must close against the pointwise alarm vector",
            "must not remove an existing healthy-window alarm",
            "alarm counts must match independent references",
        ):
            self.assertIn(token, checks)

    def test_broken_wrong_sign_threshold_has_recognizable_false_alarm_symptom(self):
        reference = reference_decision(0.50, 0.20)
        self.assertEqual(reference["false_fraction"], 0)
        self.assertEqual(reference["broken_false_fraction"], 1)
        for name in ("README.md", "lesson.md", "checks.md", "experiment.m"):
            with self.subTest(name=name):
                self.assertIn("wrong-sign", self.text[name].lower())
                self.assertIn("+T", self.text[name])
        self.assertIn("brokenCase = model(0.50,0.20,0.10)", self.text["experiment.m"])
        self.assertIn("all-healthy-alarm symptom", self.text["run_checks.m"])

    def test_experiment_has_labeled_views_metrics_two_sweeps_and_broken_case(self):
        experiment = self.text["experiment.m"]
        joined = re.sub(r"'\s*\.\.\.\s*\n\s*'", "", experiment)
        self.assertIn("baseline = model(0.50,0.20,0.10)", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn("Baseline view 1", experiment)
        self.assertIn("Baseline view 2", experiment)
        self.assertIn("Deliberately broken case", experiment)
        for label in (
            "Time (s)",
            "Diagnostic residual and threshold (L/min)",
            "Alarm state (0 or 1)",
            "Threshold magnitude T (L/min)",
            "Alarmed reference-window sample fraction (0 to 1)",
            "Conditional Pump-A effectiveness loss (%)",
        ):
            self.assertIn(label, joined)
        self.assertGreaterEqual(experiment.count("figure("), 5)
        self.assertNotIn("subplot(", experiment)
        sweep_one = experiment.split("%% Sweep 1", 1)[1].split("%% Sweep 2", 1)[0]
        sweep_two = experiment.split("%% Sweep 2", 1)[1].split(
            "%% Deliberately broken case", 1
        )[0]
        for section in (sweep_one, sweep_two):
            self.assertNotIn("baseline.", section)

    def test_interactive_controls_have_units_reset_and_one_view_at_a_time(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertEqual(interactive.count("uispinner"), 3)
        self.assertIn("'Limits',[0 3]", interactive)
        self.assertIn("'Limits',[0 100]", interactive)
        self.assertIn("'Limits',[0 1]", interactive)
        self.assertIn("Threshold magnitude T (L/min)", interactive)
        self.assertIn("Conditional effectiveness loss after 20 s (%)", interactive)
        self.assertIn("Deterministic ripple amplitude (L/min)", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        for view in (
            "Residual and signed threshold",
            "Alarm decision",
            "Threshold tradeoff",
            "Fault-magnitude tradeoff",
        ):
            self.assertIn(view, interactive)
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 4)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(thresholdControl.Value", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("values = [out.residualLpm;out.signedThresholdLpm;0]", interactive)
        self.assertIn("min(values)", interactive)
        self.assertIn("max(values)", interactive)

    def test_checks_cover_malformed_recovery_isolation_applicability_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 30)
        for token in (
            "Identical inputs must produce identical outputs",
            "fixed 301x1 column",
            "decision equation, sign convention, and units",
            "pointwise comparator",
            "Threshold sweep",
            "Loss sweep",
            "Wrong-sign threshold",
            "Zero loss",
            "inclusive signed boundary",
            "Full effectiveness loss",
            "nonscalar threshold",
            "negative threshold",
            "threshold above the resource bound",
            "nonscalar effectiveness loss",
            "effectiveness loss above one",
            "nonscalar ripple amplitude",
            "ripple amplitude above the resource bound",
            "must not contaminate exact recovery",
            "P10 checks passed",
        ):
            self.assertIn(token.lower(), checks.lower())
        self.assertGreaterEqual(checks.count("assertRejects("), 18)
        applicability = self.text["checks.md"].lower()
        for token in (
            "positive",
            "negative",
            "malformed",
            "timeout",
            "cancellation",
            "not applicable",
            "rollback",
            "recovery",
            "isolation",
            "compatibility",
            "resource bound",
        ):
            self.assertIn(token, applicability)

    def test_lesson_is_concept_first_with_interpretation_and_teach_back(self):
        lesson_script = self.text["lesson.m"]
        model_position = lesson_script.index("baseline = model")
        first_plot_position = lesson_script.index("plot(", model_position)
        alarm_position = lesson_script.index("alarmFigure")
        interactive_position = lesson_script.index("interactive;")
        self.assertLess(model_position, first_plot_position)
        self.assertLess(first_plot_position, alarm_position)
        self.assertLess(alarm_position, interactive_position)
        self.assertEqual(lesson_script.count("Prediction:"), 1)

        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "known command",
            "residual",
            "l/min",
            "sign convention",
            "threshold magnitude",
            "false alarm",
            "missed",
            "conditional loss",
            "deterministic",
            "field probabilities",
            "wrong-sign",
            "fault isolation",
            "teach-back",
        ):
            self.assertIn(concept, combined)
        self.assertIn("answer one at a time", combined)
        for name, content in self.text.items():
            with self.subTest(placeholder=name):
                self.assertIsNone(re.search(r"\b(TODO|TBD)\b", content, re.IGNORECASE))
                self.assertNotIn("not implemented", content.lower())
                self.assertNotIn("scaffolded", content.lower())

    def test_base_matlab_path_is_deterministic_isolated_and_synchronously_bounded(self):
        matlab = "\n".join(
            self.text[name]
            for name in (
                "model.m",
                "experiment.m",
                "interactive.m",
                "lesson.m",
                "run_checks.m",
            )
        ).lower()
        banned_patterns = {
            "randomness": r"\b(rand|randn|rng)\s*\(",
            "opaque diagnostic toolbox": (
                r"\b(residualgenerator|faultdetector|thresholddetector|kalman|ssest|arx|iddata)\s*\("
            ),
            "dynamic evaluation": r"\b(eval|evalin|feval)\s*\(",
            "external process": r"\b(system|unix|dos)\s*\(",
            "network": r"\b(webread|webwrite|urlread)\s*\(",
            "file input": r"\b(load|readtable|readmatrix|fopen)\s*\(",
            "file output": r"\b(save|writetable|writematrix|writecell)\s*\(",
            "asynchronous work": r"\b(timer|parfeval|batch)\s*\(",
            "unbounded loop": r"(?m)^\s*while\b",
            "blocking prompt": r"\b(input|pause|uiwait)\s*\(",
            "global state": r"(?m)^\s*global\b",
            "persistent state": r"(?m)^\s*persistent\b",
            "unrelated figure closure": r"\bclose\s+all\b",
        }
        for name, pattern in banned_patterns.items():
            with self.subTest(boundary=name):
                self.assertIsNone(re.search(pattern, matlab))
        model = self.text["model.m"]
        self.assertIsNone(re.search(r"(?m)^\s*(for|while)\b", model))
        self.assertIn("'sampleCount',numel(timeSeconds)", model)
        self.assertIn("'<=',10", model)
        self.assertGreaterEqual(model.count("'<=',1"), 2)

    def test_shared_entry_points_publish_p10_without_freezing_later_frontier(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        module_index = (ROOT / "modules/README.md").read_text(encoding="utf-8")
        for token in (
            "./bin/learn start P10",
            'launch_lesson("P10")',
            'run_module_checks("P10")',
        ):
            self.assertIn(token, readme)
        self.assertIn("P10", start_here)
        p10_row = next(
            line for line in module_index.splitlines() if line.startswith("| P10 |")
        )
        self.assertTrue(p10_row.endswith("| implemented |"))

    def test_retained_evidence_maps_acceptance_results_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P10-*.md"))
        self.assertTrue(records, "P10 retained evidence is missing")
        evidence = records[-1].read_text(encoding="utf-8")
        normalized_evidence = " ".join(evidence.lower().split())
        for marker in (
            "## Acceptance map",
            "## Exact validation commands and results",
            "## Figure, control, metric, and unit inventory",
            "## Runtime inventory",
            "## Focused behavior matrix",
            "## Independent audit findings and repairs",
            "## Independent system-risk review and repair",
            "## Final independent system-risk review and repair",
            "## Changed and preserved invariants",
            "## Rollback",
            "## Residual risks",
            "## Unperformed validation",
            "MATLAB execution",
            "UI behavior",
            "numerical fidelity",
            "static",
            "simulated",
            "protocol",
            "bench",
            "HIL",
            "RT1/RT2",
            "field",
            "Unreal",
            "signing",
            "deployment",
            "production",
            "playtest",
            "timeout",
            "cancellation",
            "rollback",
            "recovery",
            "isolation",
            "compatibility",
            "resource bound",
            "downstream batches must be rolled back first",
            "shared files must be edited selectively",
            "MATLAB_LEARNING_VERIFY_PROFILE=contract",
            "MATLAB_LEARNING_VERIFY_PROFILE=quick",
            "MATLAB_LEARNING_VERIFY_PROFILE=full",
            "test_ripple_control_has_exact_isolated_reference_behavior",
            "test_p09_to_p10_matched_residual_behavior_contract_is_regressed",
            "17 tests",
            "131 tests",
        ):
            self.assertIn(" ".join(marker.lower().split()), normalized_evidence)
        self.assertIn(
            "implemented; p10 is `implemented` with evidence level `simulated`",
            normalized_evidence,
        )
        for stale_marker in (
            "| pending |",
            "gate in progress",
            "manifest remains scaffolded",
            "will review",
        ):
            self.assertNotIn(stale_marker, normalized_evidence)
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
