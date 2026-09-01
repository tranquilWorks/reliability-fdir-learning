from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/09-generate-a-diagnostic-residual"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you "
    "generate a Diagnostic Residual?"
)


class P09ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P09"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p09_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 9)
        self.assertEqual(self.module["title"], "Generate a Diagnostic Residual")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 3)
        self.assertEqual(self.module["phase_title"], "Detection and isolation")
        self.assertEqual(self.module["slug"], "generate-a-diagnostic-residual")
        self.assertEqual(
            self.module["folder"],
            "modules/09-generate-a-diagnostic-residual",
        )
        self.assertEqual(self.module["prerequisites"], ["P08"])
        self.assertEqual(self.module["implementation_batch"], "P09")
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
                self.assertIn("P08", self.text[name])
        combined = "\n".join(self.text.values())
        self.assertIn("A only", combined)
        self.assertIn("degraded mission success", combined)
        self.assertIn("occurrence probability", combined)
        for downstream in ("P10", "P11", "P12"):
            self.assertIn(downstream, combined)

    def test_model_exposes_transparent_command_conditioned_residual_equations(self):
        model = self.text["model.m"]
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "timeSeconds=(0:samplePeriodSeconds:30).';",
            "deterministicRippleLpm=rippleAmplitudeLpm*sin(2*pi*rippleFrequencyHz*timeSeconds);",
            "healthyFlowLpm=nominalGainLpmPerCommand*speedCommand;",
            "faultFlowLossLpm=nominalGainLpmPerCommand*effectivenessLossFraction*faultActive.*speedCommand;",
            "trueFlowLpm=healthyFlowLpm-faultFlowLossLpm;",
            "measuredFlowLpm=trueFlowLpm+deterministicRippleLpm;",
            "predictedFlowLpm=predictorGainLpmPerCommand*speedCommand;",
            "residualLpm=measuredFlowLpm-predictedFlowLpm;",
            "residualDecompositionErrorLpm=residualLpm-(modelMismatchResidualLpm+faultResidualLpm+deterministicRippleLpm);",
            "brokenResidualLpm=measuredFlowLpm-brokenPredictedFlowLpm;",
        ):
            self.assertIn(equation, compact)
        for output in (
            "speedCommand",
            "measuredFlowLpm",
            "predictedFlowLpm",
            "residualLpm",
            "modelMismatchResidualLpm",
            "faultResidualLpm",
            "deterministicRippleLpm",
            "faultResidualChangeLpm",
            "brokenCommandStepResidualChangeLpm",
            "residualEquation",
            "signConvention",
            "scopeBoundary",
        ):
            self.assertIn(output, model)
        self.assertEqual(model.count("(1,1) double"), 3)
        self.assertIn("{'real','finite','>=',0,'<=',1}", model)
        self.assertIn("{'real','finite','>=',0,'<=',20}", model)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "scatter(",
            "uifigure",
            "uiaxes",
        ):
            self.assertNotIn(presentation_call, model.lower())

    def test_baseline_signals_metrics_and_limits_are_independently_known(self):
        sample_period = 0.1
        sample_count = round(30 / sample_period) + 1
        self.assertEqual(sample_count, 301)
        nominal_gain = 10.0
        low_command = 0.5
        high_command = 0.8
        loss = 0.20
        self.assertEqual(nominal_gain * low_command, 5.0)
        self.assertEqual(nominal_gain * high_command, 8.0)
        faulted_flow = nominal_gain * (1 - loss) * high_command
        self.assertAlmostEqual(faulted_flow, 6.4, places=15)
        self.assertAlmostEqual(faulted_flow - nominal_gain * high_command, -1.6)
        self.assertAlmostEqual(0.1 / math.sqrt(2), 0.07071067811865475)
        self.assertAlmostEqual(
            math.sqrt(1.6**2 + 0.1**2 / 2),
            1.6015617378046967,
        )
        checks = self.text["run_checks.m"]
        for token in (
            "fixed 301-sample deterministic record",
            "exactly three ripple cycles",
            "Reference-window measured flows must be 5, 8, and 6.4 L/min",
            "Known command conditioning must reject the normal command step",
            "-1.6 L/min signature",
            "sinusoid amplitude over sqrt two",
            "components must close to the residual",
            "Full effectiveness loss",
            "Predictor mismatch cancellation",
        ):
            self.assertIn(token, checks)

    def test_effectiveness_loss_sweep_has_exact_isolated_reference_behavior(self):
        losses = [0, 0.05, 0.10, 0.20, 0.30]
        means = [-10 * loss * 0.8 for loss in losses]
        expected = [0, -0.4, -0.8, -1.6, -2.4]
        for actual, reference in zip(means, expected):
            self.assertAlmostEqual(actual, reference, places=15)
        experiment = self.text["experiment.m"]
        self.assertIn(
            "effectivenessLossSweep = [0 0.05 0.10 0.20 0.30]",
            experiment,
        )
        self.assertIn(
            "changed = model(effectivenessLossSweep(k),10,0.10)",
            experiment,
        )
        checks = self.text["run_checks.m"]
        self.assertIn("leave command and nominal prediction fixed", checks)
        self.assertIn("leave every pre-fault measurement fixed", checks)

    def test_predictor_gain_sweep_exposes_mismatch_and_fault_cancellation(self):
        gains = [8, 9, 10, 11, 12]
        healthy_means = [(10 - gain) * 0.8 for gain in gains]
        post_means = [value - 1.6 for value in healthy_means]
        command_changes = [(10 - gain) * 0.3 for gain in gains]
        self.assertEqual(healthy_means, [1.6, 0.8, 0.0, -0.8, -1.6])
        for actual, expected in zip(post_means, [0.0, -0.8, -1.6, -2.4, -3.2]):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            command_changes, [0.6, 0.3, 0.0, -0.3, -0.6]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        experiment = self.text["experiment.m"]
        self.assertIn(
            "predictorGainSweepLpmPerCommand = [8 9 10 11 12]", experiment
        )
        self.assertIn(
            "changed = model(0.20,predictorGainSweepLpmPerCommand(k),0.10)",
            experiment,
        )
        checks = self.text["run_checks.m"]
        self.assertIn("leave physical true and measured flow fixed", checks)
        self.assertIn("preserve the -1.6 L/min fault-induced shift", checks)
        self.assertIn("must not be mistaken for physical health", checks)

    def test_sweeps_preserve_pointwise_residual_component_attribution(self):
        times = [sample / 10 for sample in range(301)]
        command = [0.5 if time < 10 else 0.8 for time in times]
        fault_active = [0 if time < 20 else 1 for time in times]
        ripple = [
            0.1 * math.sin(2 * math.pi * 0.5 * time) for time in times
        ]

        loss_fault_components = []
        for loss in [0, 0.05, 0.10, 0.20, 0.30]:
            mismatch = [0.0 for _ in times]
            fault_component = [
                -10 * loss * active * speed
                for active, speed in zip(fault_active, command)
            ]
            residual = [
                model_error + fault_value + nuisance
                for model_error, fault_value, nuisance in zip(
                    mismatch, fault_component, ripple
                )
            ]
            self.assertTrue(all(value == 0 for value in mismatch))
            self.assertTrue(
                all(
                    abs(value - nuisance) < 1e-15
                    for value, nuisance, active in zip(
                        residual, ripple, fault_active
                    )
                    if not active
                )
            )
            self.assertTrue(
                all(
                    abs(value - (model_error + fault_value + nuisance)) < 1e-15
                    for value, model_error, fault_value, nuisance in zip(
                        residual, mismatch, fault_component, ripple
                    )
                )
            )
            self.assertTrue(all(value == 0 for value in fault_component[:200]))
            for value in fault_component[200:]:
                self.assertAlmostEqual(value, -8 * loss, places=15)
            loss_fault_components.append(fault_component)

        for earlier, later in zip(
            loss_fault_components, loss_fault_components[1:]
        ):
            self.assertTrue(
                all(
                    later_value < earlier_value
                    for earlier_value, later_value, active in zip(
                        earlier, later, fault_active
                    )
                    if active
                )
            )

        baseline_fault_component = [
            -10 * 0.20 * active * speed
            for active, speed in zip(fault_active, command)
        ]
        gain_mismatch_components = []
        for gain in [8, 9, 10, 11, 12]:
            prediction = [gain * speed for speed in command]
            mismatch = [(10 - gain) * speed for speed in command]
            residual = [
                model_error + fault_value + nuisance
                for model_error, fault_value, nuisance in zip(
                    mismatch, baseline_fault_component, ripple
                )
            ]
            self.assertAlmostEqual(prediction[0], 0.5 * gain, places=15)
            self.assertAlmostEqual(prediction[100], 0.8 * gain, places=15)
            self.assertAlmostEqual(mismatch[0], 0.5 * (10 - gain), places=15)
            self.assertAlmostEqual(mismatch[100], 0.8 * (10 - gain), places=15)
            self.assertTrue(all(value == mismatch[100] for value in mismatch[100:]))
            self.assertTrue(
                all(
                    abs(value - (model_error + fault_value + nuisance)) < 1e-15
                    for value, model_error, fault_value, nuisance in zip(
                        residual, mismatch, baseline_fault_component, ripple
                    )
                )
            )
            gain_mismatch_components.append(mismatch)

        self.assertTrue(
            all(
                later_value < earlier_value
                for earlier, later in zip(
                    gain_mismatch_components, gain_mismatch_components[1:]
                )
                for earlier_value, later_value in zip(earlier, later)
            )
        )

        interactive = self.text["interactive.m"]
        decomposition = interactive.split("function drawDecomposition", 1)[1]
        for output in (
            "out.modelMismatchResidualLpm",
            "out.faultResidualLpm",
            "out.deterministicRippleLpm",
            "out.residualLpm",
        ):
            self.assertIn(output, decomposition)

        checks = re.sub(
            r"\s+|\.\.\.",
            "",
            re.sub(r"'\s*\.\.\.\s*\n\s*'", "", self.text["run_checks.m"]),
        )
        for token in (
            "expectedFaultComponentLpm=-10*effectivenessLossSweep(k)*"
            "baseline.faultActive.*baseline.speedCommand;",
            "expectedLossResidualLpm=expectedFaultComponentLpm+"
            "baseline.deterministicRippleLpm;",
            "changed.residualLpm-expectedLossResidualLpm",
            "expectedPredictionLpm=predictorGainSweepLpmPerCommand(k)*"
            "baseline.speedCommand;",
            "expectedMismatchComponentLpm=(10-"
            "predictorGainSweepLpmPerCommand(k))*baseline.speedCommand;",
            "changed.residualLpm-expectedGainResidualLpm",
            "Everyloss-sweeppointmustretainthepointwiseresidualdecomposition.",
            "Everypredictor-gainsweeppointmustretainthepointwiseresidualdecomposition.",
        ):
            self.assertIn(token, checks)

    def test_broken_constant_predictor_has_a_recognizable_false_signature(self):
        low_flow = 10 * 0.5
        high_flow = 10 * 0.8
        correct_change = (high_flow - high_flow) - (low_flow - low_flow)
        broken_change = (high_flow - low_flow) - (low_flow - low_flow)
        self.assertEqual(correct_change, 0)
        self.assertEqual(broken_change, 3)
        for name in ("README.md", "lesson.md", "checks.md", "experiment.m"):
            with self.subTest(name=name):
                self.assertIn("known command", self.text[name].lower())
                self.assertIn("broken", self.text[name].lower())
        self.assertIn("brokenCase = model(0,10,0.10)", self.text["experiment.m"])
        self.assertIn("omitted-command symptom", self.text["run_checks.m"])

    def test_experiment_has_labeled_views_metrics_two_sweeps_and_broken_case(self):
        experiment = self.text["experiment.m"]
        joined = re.sub(r"'\s*\.\.\.\s*\n\s*'", "", experiment)
        self.assertIn("baseline = model(0.20,10,0.10)", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn("Baseline view 1", experiment)
        self.assertIn("Baseline view 2", experiment)
        self.assertIn("Baseline view 3", experiment)
        self.assertIn("Deliberately broken case", experiment)
        for label in (
            "Time (s)",
            "Pump-A cooling flow (L/min)",
            "Diagnostic residual r = y-y-hat (L/min)",
            "Residual contribution (L/min)",
            "Conditional Pump-A effectiveness loss after injection (%)",
            "Predictor gain K-hat (L/min per normalized command)",
            "Reference-window mean residual (L/min)",
        ):
            self.assertIn(label, joined)
        self.assertGreaterEqual(experiment.count("figure("), 6)
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
        self.assertIn("'Limits',[0 100]", interactive)
        self.assertIn("'Limits',[0 20]", interactive)
        self.assertIn("'Limits',[0 1]", interactive)
        self.assertIn("Conditional effectiveness loss after 20 s (%)", interactive)
        self.assertIn(
            "Predictor gain K-hat (L/min per normalized command)", interactive
        )
        self.assertIn("Deterministic ripple amplitude (L/min)", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn("Measured versus predicted flow", interactive)
        self.assertIn("Diagnostic residual", interactive)
        self.assertIn("Residual decomposition", interactive)
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 4)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(lossControl.Value/100", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("does not define an alarm threshold", interactive)
        self.assertIn(
            "flowValues = [out.measuredFlowLpm;out.predictedFlowLpm]", interactive
        )
        self.assertIn("min(0,lower-0.08*span)", interactive)
        self.assertNotIn("ylim(axesHandle,[0 upper])", interactive)
        self.assertIn("residualWithReference = [out.residualLpm;0]", interactive)

    def test_checks_cover_malformed_recovery_isolation_applicability_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 35)
        for token in (
            "Identical inputs must produce identical outputs",
            "fixed 301x1 column",
            "known speed command",
            "Residual equation, sign convention, and units",
            "conditional magnitude",
            "loss sweep",
            "Predictor-gain sweep",
            "Broken constant prediction",
            "Zero loss, matched gain, and zero ripple",
            "Full effectiveness loss",
            "nonscalar loss input",
            "negative effectiveness loss",
            "loss above one",
            "nonscalar predictor gain",
            "predictor gain above the resource bound",
            "nonscalar ripple amplitude",
            "ripple amplitude above the resource bound",
            "complex ripple amplitude",
            "must not contaminate exact recovery",
            "P09 checks passed",
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
        flow_position = lesson_script.index("baseline = model")
        first_plot_position = lesson_script.index("plot(", flow_position)
        residual_position = lesson_script.index("residualFigure")
        interactive_position = lesson_script.index("interactive;")
        self.assertLess(flow_position, first_plot_position)
        self.assertLess(first_plot_position, residual_position)
        self.assertLess(residual_position, interactive_position)
        self.assertEqual(lesson_script.count("Prediction:"), 1)

        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "measured flow",
            "known command",
            "prediction",
            "residual",
            "l/min",
            "sign convention",
            "effectiveness loss",
            "model mismatch",
            "deterministic ripple",
            "occurrence probability",
            "alarm threshold",
            "unique diagnosis",
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
            "opaque diagnostics toolbox": (
                r"\b(residualgenerator|faultdetector|kalman|ssest|arx|iddata)\s*\("
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
        self.assertIn("sampleCount',numel(timeSeconds)", model)
        self.assertIn("'<=',20", model)
        self.assertIn("'<=',1", model)

    def test_shared_entry_points_publish_p09_without_freezing_later_frontier(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        module_index = (ROOT / "modules/README.md").read_text(encoding="utf-8")
        for token in (
            "./bin/learn start P09",
            'launch_lesson("P09")',
            'run_module_checks("P09")',
        ):
            self.assertIn(token, readme)
        self.assertIn("P09", start_here)
        p09_row = next(
            line for line in module_index.splitlines() if line.startswith("| P09 |")
        )
        self.assertTrue(p09_row.endswith("| implemented |"))

    def test_retained_evidence_maps_acceptance_results_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P09-*.md"))
        self.assertTrue(records, "P09 retained evidence is missing")
        evidence = records[-1].read_text(encoding="utf-8")
        normalized_evidence = " ".join(evidence.lower().split())
        for marker in (
            "## Acceptance map",
            "## Exact validation commands and results",
            "## Figure, control, metric, and unit inventory",
            "## Runtime inventory",
            "## Focused behavior matrix",
            "## Independent system-risk review and repair",
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
            "MATLAB_LEARNING_VERIFY_PROFILE=contract",
            "MATLAB_LEARNING_VERIFY_PROFILE=quick",
            "MATLAB_LEARNING_VERIFY_PROFILE=full",
            "test_sweeps_preserve_pointwise_residual_component_attribution",
            "15 tests",
            "114 tests",
        ):
            self.assertIn(" ".join(marker.lower().split()), normalized_evidence)
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
