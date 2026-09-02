from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/11-isolate-competing-faults"
P10_FOLDER = ROOT / "modules/10-move-a-fault-threshold"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you "
    "isolate Competing Faults?"
)
CANDIDATES = ([0, 0], [1, 1], [1, 0])


def reference_case(loss_fraction: float, sensor_bias_lpm: float) -> dict[str, object]:
    times = [sample / 10 for sample in range(301)]
    command = [0.5 if time < 10 else 0.8 for time in times]
    active = [time >= 20 for time in times]
    flow_ripple = [
        0.10 * math.sin(2 * math.pi * 0.5 * time) for time in times
    ]
    pressure_ripple = [
        0.50 * math.sin(2 * math.pi * 0.5 * time) for time in times
    ]
    pump_flow = [
        -10 * loss_fraction * enabled * speed
        for enabled, speed in zip(active, command)
    ]
    sensor_flow = [-sensor_bias_lpm * enabled for enabled in active]
    flow = [
        pump + sensor + ripple
        for pump, sensor, ripple in zip(pump_flow, sensor_flow, flow_ripple)
    ]
    pump_pressure = [
        -50 * loss_fraction * enabled * speed
        for enabled, speed in zip(active, command)
    ]
    pressure = [
        pump + ripple for pump, ripple in zip(pump_pressure, pressure_ripple)
    ]
    consistency = [
        pressure_value - 5 * flow_value
        for pressure_value, flow_value in zip(pressure, flow)
    ]
    healthy_window = [12 <= time < 18 for time in times]
    fault_window = [22 <= time < 28 for time in times]

    def window_mean(values: list[float], window: list[bool]) -> float:
        selected = [value for value, included in zip(values, window) if included]
        return sum(selected) / len(selected)

    flow_mean = window_mean(flow, fault_window)
    pressure_mean = window_mean(pressure, fault_window)
    consistency_mean = window_mean(consistency, fault_window)
    flow_tolerance = 16 * math.ulp(max(1.0, 0.50, abs(flow_mean)))
    pressure_tolerance = 16 * math.ulp(max(1.0, 4.0, abs(pressure_mean)))
    signature = [
        int(flow_mean <= -0.50 + flow_tolerance),
        int(pressure_mean <= -4.0 + pressure_tolerance),
    ]
    distances = [
        sum(abs(actual - expected) for actual, expected in zip(signature, candidate))
        for candidate in CANDIDATES
    ]
    exact_indexes = [index for index, distance in enumerate(distances) if distance == 0]
    broken_distances = [abs(candidate[0] - signature[0]) for candidate in CANDIDATES]
    return {
        "times": times,
        "command": command,
        "active": active,
        "flow_ripple": flow_ripple,
        "pressure_ripple": pressure_ripple,
        "pump_flow": pump_flow,
        "sensor_flow": sensor_flow,
        "flow": flow,
        "pump_pressure": pump_pressure,
        "pressure": pressure,
        "consistency": consistency,
        "healthy_window": healthy_window,
        "fault_window": fault_window,
        "flow_mean": flow_mean,
        "pressure_mean": pressure_mean,
        "consistency_mean": consistency_mean,
        "flow_tolerance": flow_tolerance,
        "pressure_tolerance": pressure_tolerance,
        "signature": signature,
        "distances": distances,
        "exact_indexes": exact_indexes,
        "broken_distances": broken_distances,
        "broken_exact_count": sum(distance == 0 for distance in broken_distances),
    }


class P11ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P11"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p11_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 11)
        self.assertEqual(self.module["title"], "Isolate Competing Faults")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 3)
        self.assertEqual(self.module["phase_title"], "Detection and isolation")
        self.assertEqual(self.module["slug"], "isolate-competing-faults")
        self.assertEqual(
            self.module["folder"], "modules/11-isolate-competing-faults"
        )
        self.assertEqual(self.module["prerequisites"], ["P10"])
        self.assertEqual(self.module["implementation_batch"], "P11")
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
            "run_checks.m",
        ):
            with self.subTest(name=name):
                self.assertIn("P10", self.text[name])
        combined = "\n".join(self.text.values())
        for token in (
            "r_Q",
            "L/min",
            "r_P",
            "kPa",
            "P12",
            "posterior probability",
            "single-fault",
        ):
            self.assertIn(token.lower(), combined.lower())

    def test_model_exposes_transparent_residual_and_signature_equations(self):
        model = self.text["model.m"]
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "timeSeconds=(0:samplePeriodSeconds:30).';",
            "deterministicFlowRippleLpm=rippleAmplitudeLpm*sin(2*pi*rippleFrequencyHz*timeSeconds);",
            "pumpLossFlowResidualLpm=-nominalGainLpmPerCommand*effectivenessLossFraction*faultActive.*speedCommand;",
            "sensorBiasFlowResidualLpm=-flowSensorBiasLpm*faultActive;",
            "flowResidualLpm=pumpLossFlowResidualLpm+sensorBiasFlowResidualLpm+deterministicFlowRippleLpm;",
            "pumpLossPressureResidualKpa=-nominalPressureGainKpaPerCommand*effectivenessLossFraction*faultActive.*speedCommand;",
            "pressureResidualKpa=measuredPressureKpa-predictedPressureKpa;",
            "biasConsistencyResidualKpa=pressureResidualKpa-pressureToFlowScaleKpaPerLpm*flowResidualLpm;",
            "candidateSignatureMatrix=[00;11;10];",
            "hammingDistances=sum(abs(candidateSignatureMatrix-observedSignature),2);",
        ):
            self.assertIn(equation, compact)
        for output in (
            "observedSignature",
            "candidateSignatureMatrix",
            "hammingDistances",
            "exactMatchCount",
            "decodedCandidateLabel",
            "singleFaultLibraryApplicable",
            "isCorrectIsolation",
            "brokenFlowOnlyExactMatchCount",
            "scopeBoundary",
            "flowFeatureComparisonToleranceLpm",
            "pressureFeatureComparisonToleranceKpa",
        ):
            self.assertIn(f"out.{output}", model)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "uifigure",
            "uiaxes",
            "uilabel",
        ):
            self.assertNotIn(presentation_call, model.lower())

    def test_baseline_competing_faults_and_signatures_are_independently_known(self):
        pump = reference_case(0.20, 0)
        sensor = reference_case(0, 1.60)
        self.assertEqual(len(pump["times"]), 301)
        self.assertEqual(sum(pump["healthy_window"]), 60)
        self.assertEqual(sum(pump["fault_window"]), 60)
        self.assertAlmostEqual(pump["flow_mean"], -1.6, places=14)
        self.assertAlmostEqual(pump["pressure_mean"], -8.0, places=14)
        self.assertAlmostEqual(pump["consistency_mean"], 0.0, places=14)
        self.assertEqual(pump["signature"], [1, 1])
        self.assertEqual(pump["distances"], [2, 0, 1])
        self.assertEqual(pump["exact_indexes"], [1])

        for pump_value, sensor_value in zip(pump["flow"], sensor["flow"]):
            self.assertAlmostEqual(pump_value, sensor_value, places=14)
        self.assertAlmostEqual(sensor["flow_mean"], -1.6, places=14)
        self.assertAlmostEqual(sensor["pressure_mean"], 0.0, places=14)
        self.assertAlmostEqual(sensor["consistency_mean"], 8.0, places=14)
        self.assertEqual(sensor["signature"], [1, 0])
        self.assertEqual(sensor["distances"], [1, 1, 0])
        self.assertEqual(sensor["exact_indexes"], [2])

    def test_pump_loss_sweep_has_exact_isolated_coverage_behavior(self):
        losses = [0, 0.04, 0.08, 0.12, 0.20]
        cases = [reference_case(loss, 0) for loss in losses]
        expected_flow = [0, -0.32, -0.64, -0.96, -1.6]
        expected_pressure = [0, -1.6, -3.2, -4.8, -8]
        for case, flow, pressure in zip(cases, expected_flow, expected_pressure):
            self.assertAlmostEqual(case["flow_mean"], flow, places=14)
            self.assertAlmostEqual(case["pressure_mean"], pressure, places=14)
            self.assertTrue(all(value == 0 for value in case["sensor_flow"]))
        self.assertEqual(
            [case["signature"] for case in cases],
            [[0, 0], [0, 0], [1, 0], [1, 1], [1, 1]],
        )
        self.assertEqual(cases[2]["exact_indexes"], [2])
        experiment = self.text["experiment.m"]
        self.assertIn("pumpLossSweep = [0 0.04 0.08 0.12 0.20]", experiment)
        self.assertIn("changed = model(pumpLossSweep(k),0)", experiment)
        self.assertIn("coverage gap", experiment.lower())

    def test_sensor_bias_sweep_has_exact_isolated_behavior(self):
        biases = [0, 0.30, 0.60, 1.00, 1.60]
        cases = [reference_case(0, bias) for bias in biases]
        for case, expected in zip(cases, [0, -0.30, -0.60, -1.00, -1.60]):
            self.assertAlmostEqual(case["flow_mean"], expected, places=14)
            self.assertAlmostEqual(case["pressure_mean"], 0.0, places=14)
            self.assertTrue(all(value == 0 for value in case["pump_flow"]))
            self.assertTrue(all(value == 0 for value in case["pump_pressure"]))
        self.assertEqual(
            [case["signature"] for case in cases],
            [[0, 0], [0, 0], [1, 0], [1, 0], [1, 0]],
        )
        experiment = self.text["experiment.m"]
        self.assertIn(
            "sensorBiasSweepLpm = [0 0.30 0.60 1.00 1.60]", experiment
        )
        self.assertIn("changed = model(0,sensorBiasSweepLpm(k))", experiment)

    def test_consistency_identity_limits_and_combined_fault_boundary(self):
        for loss, bias in ((0, 0), (0.20, 0), (0, 1.60), (0.20, 1.60)):
            case = reference_case(loss, bias)
            for actual, enabled in zip(case["consistency"], case["active"]):
                self.assertAlmostEqual(actual, 5 * bias * enabled, places=14)
        full_loss = reference_case(1, 0)
        maximum_bias = reference_case(0, 10)
        self.assertAlmostEqual(full_loss["flow_mean"], -8, places=14)
        self.assertAlmostEqual(full_loss["pressure_mean"], -40, places=12)
        self.assertEqual(full_loss["signature"], [1, 1])
        self.assertAlmostEqual(maximum_bias["flow_mean"], -10, places=14)
        self.assertAlmostEqual(maximum_bias["pressure_mean"], 0, places=14)
        self.assertEqual(maximum_bias["signature"], [1, 0])
        inclusive_flow = reference_case(0, 0.50)
        inclusive_pressure = reference_case(0.10, 0)
        self.assertAlmostEqual(inclusive_flow["flow_mean"], -0.50, places=14)
        self.assertLess(
            abs(inclusive_flow["flow_mean"] + 0.50),
            inclusive_flow["flow_tolerance"],
        )
        self.assertEqual(inclusive_flow["signature"], [1, 0])
        self.assertAlmostEqual(
            inclusive_pressure["pressure_mean"], -4.0, places=14
        )
        self.assertLess(
            abs(inclusive_pressure["pressure_mean"] + 4.0),
            inclusive_pressure["pressure_tolerance"],
        )
        self.assertEqual(inclusive_pressure["signature"], [1, 1])
        model = self.text["model.m"]
        self.assertIn("Combined fault outside single-fault library", model)
        self.assertIn("Not applicable: both injected faults are active", model)
        self.assertIn("16*eps", re.sub(r"\s+|\.\.\.", "", model))

    def test_numerical_tolerance_does_not_widen_the_decision_band(self):
        input_margin = 128 * math.ulp(1.0)
        just_clear_flow = reference_case(0, 0.50 - input_margin)
        self.assertGreater(
            just_clear_flow["flow_mean"],
            -0.50 + just_clear_flow["flow_tolerance"],
        )
        self.assertEqual(just_clear_flow["signature"], [0, 0])

        just_clear_pressure = reference_case(0.10 - input_margin, 0)
        self.assertGreater(
            just_clear_pressure["pressure_mean"],
            -4.0 + just_clear_pressure["pressure_tolerance"],
        )
        self.assertEqual(just_clear_pressure["signature"], [1, 0])

        checks = self.text["run_checks.m"].lower()
        self.assertIn(
            "just outside the numerical flow tolerance must", checks
        )
        self.assertIn(
            "just outside the numerical pressure tolerance must", checks
        )

    def test_broken_flow_only_decoder_has_recognizable_ambiguity(self):
        pump = reference_case(0.20, 0)
        sensor = reference_case(0, 1.60)
        self.assertEqual(pump["broken_distances"], [1, 0, 0])
        self.assertEqual(sensor["broken_distances"], [1, 0, 0])
        self.assertEqual(pump["broken_exact_count"], 2)
        for name in ("README.md", "lesson.md", "checks.md", "experiment.m"):
            with self.subTest(name=name):
                self.assertIn("flow-only", self.text[name].lower())
                self.assertIn("distinct signatures", self.text[name].lower())
        self.assertIn("brokenCase = model(0.20,0)", self.text["experiment.m"])
        self.assertIn("two-exact-match ambiguity", self.text["run_checks.m"])

    def test_experiment_has_labeled_views_metrics_two_sweeps_and_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertIn("baseline = model(0.20,0)", experiment)
        self.assertIn("competingFault = model(0,1.60)", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        for view in ("Baseline view 1", "Baseline view 2", "Baseline view 3"):
            self.assertIn(view, experiment)
        self.assertIn("Deliberately broken case", experiment)
        for label in (
            "Time (s)",
            "Flow residual r_Q (L/min)",
            "Discharge-pressure residual r_P (kPa)",
            "Thresholded residual test (0 or 1)",
            "Conditional Pump-A effectiveness loss (%)",
            "Negative flow-sensor bias magnitude (L/min)",
            "Signed evidence magnitude / threshold (dimensionless)",
            "Flow-only Hamming distance (bits)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 6)
        self.assertNotIn("subplot(", experiment)
        sweep_one = experiment.split("%% Sweep 1", 1)[1].split("%% Sweep 2", 1)[0]
        sweep_two = experiment.split("%% Sweep 2", 1)[1].split(
            "%% Deliberately broken case", 1
        )[0]
        self.assertIn("model(pumpLossSweep(k),0)", sweep_one)
        self.assertNotIn("sensorBiasSweepLpm", sweep_one)
        self.assertIn("model(0,sensorBiasSweepLpm(k))", sweep_two)
        self.assertNotIn("pumpLossSweep", sweep_two)

    def test_interactive_controls_have_units_reset_and_one_view_at_a_time(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertEqual(interactive.count("uispinner"), 2)
        self.assertIn("'Limits',[0 100]", interactive)
        self.assertIn("'Limits',[0 5]", interactive)
        self.assertIn(
            "Conditional Pump-A effectiveness loss after 20 s (%)", interactive
        )
        self.assertIn(
            "Negative flow-sensor bias magnitude after 20 s (L/min)", interactive
        )
        self.assertIn("Visible view (one at a time)", interactive)
        for view in (
            "Flow residual",
            "Pressure residual",
            "Residual signature",
            "Pump-loss coverage sweep",
            "Sensor-bias sweep",
        ):
            self.assertIn(view, interactive)
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset Pump-A baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 3)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn(
            "out = modelForThisModule(lossControl.Value/100,biasControl.Value)",
            interactive,
        )
        self.assertNotIn("out = model(", interactive)
        self.assertIn("single-fault library", interactive)

    def test_checks_cover_malformed_recovery_isolation_applicability_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 35)
        for token in (
            "Identical inputs must produce identical outputs",
            "fixed 301-sample deterministic record",
            "Flow and pressure residual equations",
            "P10 pointwise flow threshold behavior",
            "fixed and distinct",
            "one correct exact signature match",
            "weak-fault 10 coverage gap",
            "two-exact-match ambiguity",
            "Simultaneous faults",
            "Full effectiveness loss",
            "Maximum bounded bias",
            "nonscalar effectiveness loss",
            "effectiveness loss above one",
            "nonscalar flow-sensor bias",
            "flow-sensor bias above the resource bound",
            "must not contaminate exact recovery",
            "P11 checks passed",
        ):
            self.assertIn(token.lower(), checks.lower())
        self.assertGreaterEqual(checks.count("assertRejects("), 12)
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
        model_position = lesson_script.index("pumpFault = model")
        flow_position = lesson_script.index("plot(", model_position)
        pressure_position = lesson_script.index("pressureFigure")
        signature_position = lesson_script.index("signatureFigure")
        interactive_position = lesson_script.index("interactive;")
        self.assertLess(model_position, flow_position)
        self.assertLess(flow_position, pressure_position)
        self.assertLess(pressure_position, signature_position)
        self.assertLess(signature_position, interactive_position)
        self.assertEqual(lesson_script.count("Prediction:"), 1)
        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "detection",
            "isolation",
            "flow residual",
            "pressure residual",
            "signature",
            "hamming",
            "coverage gap",
            "diagnosability",
            "posterior",
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
                r"\b(residualgenerator|faultdetector|faultdiagnos|kalman|ssest|arx|iddata)\s*\("
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
        self.assertIn("out.sampleCount = numel(timeSeconds)", model)
        self.assertIn("{'real','finite','>=',0,'<=',1}", model)
        self.assertIn("{'real','finite','>=',0,'<=',10}", model)

    def test_p10_to_p11_flow_residual_compatibility_is_regressed(self):
        p10_model = (P10_FOLDER / "model.m").read_text(encoding="utf-8")
        p11_model = self.text["model.m"]
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
            contract: dict[str, float] = {}
            for name in shared_names:
                matches = re.findall(
                    rf"(?m)^\s*{re.escape(name)}\s*=\s*"
                    r"(-?(?:\d+(?:\.\d*)?|\.\d+))\s*;",
                    source,
                )
                self.assertEqual(len(matches), 1, name)
                contract[name] = float(matches[0])
            return contract

        self.assertEqual(scalar_contract(p11_model), scalar_contract(p10_model))
        p10_compact = re.sub(r"\s+|\.\.\.", "", p10_model)
        p11_compact = re.sub(r"\s+|\.\.\.", "", p11_model)
        for source in (p10_compact, p11_compact):
            self.assertIn("timeSeconds=(0:samplePeriodSeconds:30).';", source)
            self.assertIn(
                "speedCommand(timeSeconds>=commandStepTimeSeconds)=highCommand;",
                source,
            )
            self.assertIn("faultActive=double(timeSeconds>=faultTimeSeconds);", source)
        self.assertIn(
            "residualLpm=faultResidualLpm+deterministicRippleLpm;",
            p10_compact,
        )
        self.assertIn(
            "flowResidualLpm=pumpLossFlowResidualLpm+sensorBiasFlowResidualLpm+deterministicFlowRippleLpm;",
            p11_compact,
        )
        self.assertIn("rippleAmplitudeLpm=0.10;", p11_compact)
        self.assertIn("flowThresholdMagnitudeLpm=0.50;", p11_compact)
        self.assertIn(
            "p10Alarm=flowResidualLpm<=p10SignedThresholdLpm;", p11_compact
        )
        self.assertIn("out.residualUnit='L/min'", p10_compact)
        self.assertIn("out.flowResidualUnit='L/min'", p11_compact)

        for loss, ripple in (
            (0, 0.10),
            (0.06, 0.10),
            (0.0625, 0.10),
            (0.20, 0.10),
            (1, 0.10),
        ):
            times = [sample / 10 for sample in range(301)]
            command = [0.5 if time < 10 else 0.8 for time in times]
            active = [time >= 20 for time in times]
            p10_residual = [
                -10 * loss * enabled * speed
                + ripple * math.sin(2 * math.pi * 0.5 * time)
                for time, speed, enabled in zip(times, command, active)
            ]
            p11 = reference_case(loss, 0)
            for p10_value, p11_value in zip(p10_residual, p11["flow"]):
                self.assertEqual(p10_value, p11_value)
            self.assertEqual(
                [value <= -0.50 for value in p10_residual],
                [value <= -0.50 for value in p11["flow"]],
            )

    def test_shared_entry_points_publish_p11_without_freezing_later_frontier(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        module_index = (ROOT / "modules/README.md").read_text(encoding="utf-8")
        for token in (
            "./bin/learn start P11",
            'launch_lesson("P11")',
            'run_module_checks("P11")',
        ):
            self.assertIn(token, readme)
        self.assertIn("P11", start_here)
        p11_row = next(
            line for line in module_index.splitlines() if line.startswith("| P11 |")
        )
        self.assertTrue(p11_row.endswith("| implemented |"))

    def test_retained_evidence_maps_acceptance_results_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P11-*.md"))
        self.assertTrue(records, "P11 retained evidence is missing")
        evidence = records[-1].read_text(encoding="utf-8")
        normalized = " ".join(evidence.lower().split())
        for marker in (
            "## Claim boundary",
            "## Acceptance map",
            "## Independent deterministic references",
            "## Figure, control, metric, and unit inventory",
            "## Runtime inventory",
            "## Focused behavior matrix",
            "## Repository, ownership, concurrency, runtime, and CI inspection",
            "## Independent audit findings",
            "## Exact validation commands and results",
            "## Changed and preserved invariants",
            "## Rollback",
            "## Residual risks",
            "## Unperformed validation",
            "implemented; p11 is `implemented` with evidence level `simulated`",
            "matlab execution",
            "ui behavior",
            "numerical fidelity",
            "static",
            "simulated",
            "protocol",
            "bench",
            "hil",
            "rt1/rt2",
            "field",
            "unreal",
            "signing",
            "deployment",
            "production",
            "timeout",
            "cancellation",
            "rollback",
            "recovery",
            "isolation",
            "compatibility",
            "resource bound",
            "downstream batches must be rolled back first",
            "shared files must be edited selectively",
            "matlab_learning_verify_profile=contract",
            "matlab_learning_verify_profile=quick",
            "matlab_learning_verify_profile=full",
        ):
            self.assertIn(" ".join(marker.lower().split()), normalized)
        for stale_marker in (
            "| pending |",
            "gate in progress",
            "manifest remains scaffolded",
            "will review",
        ):
            self.assertNotIn(stale_marker, normalized)
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
