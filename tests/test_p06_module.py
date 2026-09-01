from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/06-run-an-fmea"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you run "
    "an FMEA?"
)


class P06ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P06"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p06_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 6)
        self.assertEqual(self.module["title"], "Run an FMEA")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 2)
        self.assertEqual(self.module["phase_title"], "Failure analysis")
        self.assertEqual(self.module["slug"], "run-an-fmea")
        self.assertEqual(self.module["folder"], "modules/06-run-an-fmea")
        self.assertEqual(self.module["prerequisites"], ["P05"])
        self.assertEqual(self.module["implementation_batch"], "P06")
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

    def test_guiding_question_and_p05_connection_are_visible(self):
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
            "run_checks.m",
        ):
            with self.subTest(name=name):
                self.assertIn("P05", self.text[name])
        combined = "\n".join(self.text.values()).lower()
        self.assertIn("top-down", combined)
        self.assertIn("bottom-up", combined)

    def test_model_exposes_transparent_fmea_chain_rule_and_fixed_rows(self):
        model = self.text["model.m"]
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "detectedOccurrence=failureModeOccurrence.*detectionCoverage;",
            "latentOccurrence=failureModeOccurrence.*(1-detectionCoverage);",
            "expectedModeCount=sum(failureModeOccurrence);",
            "expectedDetectedCount=sum(detectedOccurrence);",
            "expectedLatentCount=sum(latentOccurrence);",
            "wrongReportedOccurrence=detectedOccurrence;",
            "wrongUndercount=expectedModeCount-wrongExpectedModeCount;",
        ):
            self.assertIn(equation, compact)
        for output in (
            "failureModeOccurrence",
            "detectionCoverage",
            "detectedOccurrence",
            "latentOccurrence",
            "expectedModeCount",
            "wrongReportedOccurrence",
            "effectAnalysisPremise",
            "loggingPremise",
            "modeIds",
            "itemFunctions",
            "failureModes",
            "exampleCauses",
            "localEffects",
            "nextHigherEffects",
            "endEffects",
            "observableEffects",
            "preventionControls",
            "detectionControls",
            "consequenceClasses",
        ):
            self.assertIn(output, model)
        self.assertEqual(model.count("(1,3) double"), 2)
        self.assertEqual(model.count("{'real','finite','>=',0,'<=',1}"), 2)
        self.assertNotIn("riskpriority", model.lower())
        self.assertIsNone(re.search(r"\brpn\b", model, re.IGNORECASE))
        self.assertIn(
            "Only the row-under-analysis mode is present", model
        )
        self.assertIn("perfect specificity and unique mode attribution", model)
        self.assertIn("With Pump B available", model)
        self.assertIn("With Pump A available", model)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "uitable",
            "uifigure",
            "uiaxes",
            "uilabel",
        ):
            self.assertNotIn(presentation_call, model.lower())

    def test_reference_rows_partitions_and_counts_are_independently_known(self):
        occurrence = [0.005, 0.10, 0.10]
        coverage = [0.98, 0.70, 0.90]
        detected = [q * c for q, c in zip(occurrence, coverage)]
        latent = [q * (1 - c) for q, c in zip(occurrence, coverage)]
        expected_detected = [0.0049, 0.0700, 0.0900]
        expected_latent = [0.0001, 0.0300, 0.0100]
        for actual, expected in zip(detected, expected_detected):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(latent, expected_latent):
            self.assertAlmostEqual(actual, expected, places=15)
        for q, seen, hidden in zip(occurrence, detected, latent):
            self.assertAlmostEqual(seen + hidden, q, places=15)
        self.assertAlmostEqual(sum(occurrence), 0.2050, places=15)
        self.assertAlmostEqual(sum(detected), 0.1649, places=15)
        self.assertAlmostEqual(sum(latent), 0.0401, places=15)
        self.assertAlmostEqual(sum(detected) + sum(latent), sum(occurrence), places=15)
        self.assertEqual(sum([1, 1, 1]), 3)
        self.assertGreater(1e-300 * 0.5, 0)
        self.assertGreater(1e-300 * (1 - 0.5), 0)

    def test_two_levers_have_isolated_reference_behavior(self):
        pump_a_occurrence = [0, 0.05, 0.10, 0.20, 0.40]
        pump_a_detected = [0.70 * value for value in pump_a_occurrence]
        pump_a_latent = [0.30 * value for value in pump_a_occurrence]
        expected_mode_counts = [0.105 + value for value in pump_a_occurrence]
        expected_detected_counts = [0.0949 + 0.70 * value for value in pump_a_occurrence]
        expected_latent_counts = [0.0101 + 0.30 * value for value in pump_a_occurrence]
        for actual, expected in zip(
            pump_a_detected, [0, 0.035, 0.070, 0.140, 0.280]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            pump_a_latent, [0, 0.015, 0.030, 0.060, 0.120]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            expected_mode_counts, [0.105, 0.155, 0.205, 0.305, 0.505]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            expected_detected_counts, [0.0949, 0.1299, 0.1649, 0.2349, 0.3749]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            expected_latent_counts, [0.0101, 0.0251, 0.0401, 0.0701, 0.1301]
        ):
            self.assertAlmostEqual(actual, expected, places=15)

        pump_a_coverage = [0, 0.25, 0.50, 0.70, 1]
        coverage_detected_counts = [0.0949 + 0.10 * value for value in pump_a_coverage]
        coverage_latent_counts = [0.1101 - 0.10 * value for value in pump_a_coverage]
        for actual, expected in zip(
            coverage_detected_counts, [0.0949, 0.1199, 0.1449, 0.1649, 0.1949]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            coverage_latent_counts, [0.1101, 0.0851, 0.0601, 0.0401, 0.0101]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        physical_counts = [
            0.005 + 0.10 + 0.10 for _ in pump_a_coverage
        ]
        for actual in physical_counts:
            self.assertAlmostEqual(actual, 0.205, places=15)

    def test_pump_a_levers_preserve_non_target_observability_rows(self):
        baseline_occurrence = [0.005, 0.10, 0.10]
        baseline_coverage = [0.98, 0.70, 0.90]

        def partition(occurrence, coverage):
            detected = [q * c for q, c in zip(occurrence, coverage)]
            latent = [q * (1 - c) for q, c in zip(occurrence, coverage)]
            return detected, latent

        baseline_detected, baseline_latent = partition(
            baseline_occurrence, baseline_coverage
        )
        cases = []
        for value in [0, 0.05, 0.10, 0.20, 0.40]:
            occurrence = baseline_occurrence.copy()
            occurrence[1] = value
            cases.append(partition(occurrence, baseline_coverage))
        for value in [0, 0.25, 0.50, 0.70, 1]:
            coverage = baseline_coverage.copy()
            coverage[1] = value
            cases.append(partition(baseline_occurrence, coverage))

        for detected, latent in cases:
            for index in (0, 2):
                self.assertAlmostEqual(
                    detected[index], baseline_detected[index], places=15
                )
                self.assertAlmostEqual(
                    latent[index], baseline_latent[index], places=15
                )

        checks = self.text["run_checks.m"]
        self.assertIn(
            "Changing qA must leave the supply and Pump-B detected and ", checks
        )
        self.assertIn(
            "Changing cA must leave the supply and Pump-B detected and ", checks
        )

    def test_broken_log_only_inventory_has_a_recognizable_symptom(self):
        physical_pump_a = 0.10
        no_coverage = 0
        full_coverage = 1
        wrong_no_coverage = physical_pump_a * no_coverage
        latent_no_coverage = physical_pump_a * (1 - no_coverage)
        wrong_full_coverage = physical_pump_a * full_coverage
        self.assertEqual(wrong_no_coverage, 0)
        self.assertEqual(latent_no_coverage, physical_pump_a)
        self.assertEqual(wrong_full_coverage, physical_pump_a)
        self.assertGreater(wrong_full_coverage, wrong_no_coverage)
        self.assertEqual(physical_pump_a, 0.10)
        self.assertAlmostEqual(0.2050 - 0.0949, 0.1101, places=15)
        model = self.text["model.m"]
        experiment = self.text["experiment.m"]
        self.assertIn("wrongReportedOccurrence = detectedOccurrence", model)
        self.assertIn(
            "brokenCase = model([0.005 0.10 0.10],[0.98 0 0.90])", experiment
        )
        self.assertIn(
            "filtered true-positive logs as the whole inventory", experiment
        )
        self.assertIn("perfect specificity", experiment)
        self.assertIn("unique attribution", experiment)

    def test_experiment_has_worksheet_two_sweeps_metrics_and_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertIn(
            "baseline = model([0.005 0.10 0.10],[0.98 0.70 0.90])", experiment
        )
        self.assertIn("uitable(worksheetFigure", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn(
            "pumpAOccurrenceSweep = [0 0.05 0.10 0.20 0.40]", experiment
        )
        self.assertIn(
            "changed = model([0.005 pumpAOccurrenceSweep(k) 0.10]", experiment
        )
        self.assertIn(
            "pumpADetectionCoverageSweep = [0 0.25 0.50 0.70 1]", experiment
        )
        self.assertIn(
            "[0.98 pumpADetectionCoverageSweep(k) 0.90]", experiment
        )
        self.assertIn("Baseline FMEA metrics per fixed 1000-hour mission", experiment)
        self.assertIn("detected and latent occurrence", experiment)
        self.assertIn("expected listed mode occurrences", experiment.lower())
        self.assertIn("Deliberately broken case", experiment)
        for label in (
            "FMEA failure-mode row",
            "Probability per fixed 1000-hour mission (dimensionless)",
            "Expected listed mode occurrences per mission (count/mission)",
            "Pump-A detection coverage P(annunciates | mode) (dimensionless)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 5)
        self.assertNotIn("subplot(", experiment)
        self.assertIn(
            "{'FMEA field','S - Shared supply','A - Pump A','B - Pump B'}",
            experiment,
        )
        self.assertIn("'ColumnWidth',{180,340,340,340}", experiment)
        self.assertNotIn("'Position',[50 120 1800 560]", experiment)

    def test_interactive_controls_have_units_reset_and_one_view_at_a_time(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertEqual(interactive.count("uispinner"), 2)
        self.assertEqual(interactive.count("'Limits',[0 1]"), 2)
        self.assertIn("Occurrence probability per fixed 1000 h (dimensionless)", interactive)
        self.assertIn(
            "Detection coverage P(annunciates | mode) (dimensionless)", interactive
        )
        self.assertIn("FMEA row to inspect", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn("{'Effect chain','Occurrence partition'}", interactive)
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 4)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("count, not a union probability or risk-priority score", interactive)
        self.assertIn("P05 combined events top-down; P06 follows each mode bottom-up", interactive)
        self.assertGreaterEqual(interactive.count("out.preventionControls{index}"), 2)
        self.assertIn("companion items available", interactive)

    def test_checks_cover_invariants_limits_malformed_recovery_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 35)
        for token in (
            "Identical inputs must produce identical outputs",
            "three fixed rows",
            "fixed 1x3 row vectors",
            "metadata column must contain exactly three rows",
            "distinct failure mode",
            "fixed 1000-hour mission boundary",
            "standard single-row analysis premise",
            "favorable logging premise",
            "Detected plus latent occurrence must equal physical occurrence",
            "expected listed mode count must independently equal 0.2050",
            "baseline expected detected count must independently equal 0.1649",
            "baseline expected latent count must independently equal 0.0401",
            "occurrence sweep expected mode counts must match references",
            "Changing qA must leave the supply and Pump-B occurrences unchanged",
            "Changing qA must not rewrite the FMEA effect chain",
            "Changing cA must leave every physical occurrence unchanged",
            "Detection coverage must not change expected physical mode occurrence",
            "Increasing cA must transfer expected count from latent to detected",
            "Zero occurrence must give zero detected and latent paths",
            "Zero coverage must make Pump-A occurrence entirely latent",
            "Full coverage must make Pump-A occurrence entirely detected",
            "expected mode count three, not a probability",
            "representable tiny occurrence must survive",
            "log-only inventory must falsely omit",
            "Wrong reported occurrence must rise with coverage despite fixed physics",
            "raw detector logs are error-free",
            "wrong-length occurrence vector must be rejected",
            "column occurrence vector must be rejected",
            "negative occurrence probability must be rejected",
            "occurrence probability above one must be rejected",
            "nonfinite occurrence probability must be rejected",
            "complex occurrence probability must be rejected",
            "wrong-length coverage vector must be rejected",
            "column coverage vector must be rejected",
            "negative detection coverage must be rejected",
            "detection coverage above one must be rejected",
            "nonfinite detection coverage must be rejected",
            "complex detection coverage must be rejected",
            "must not contaminate a later valid calculation",
            "P06 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertGreaterEqual(checks.count("assertRejects("), 14)

    def test_lesson_is_concept_first_with_interpretation_and_teach_back(self):
        lesson_script = self.text["lesson.m"]
        worksheet_position = lesson_script.index("uitable(")
        partition_position = lesson_script.index("bar(")
        interactive_position = lesson_script.index("interactive;")
        self.assertLess(worksheet_position, partition_position)
        self.assertLess(partition_position, interactive_position)
        self.assertIn("Item / required function", lesson_script)
        self.assertIn("Next-higher effect", lesson_script)

        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "item function",
            "failure mode",
            "local effect",
            "next-higher effect",
            "end effect",
            "conditional",
            "detected",
            "latent",
            "expected counts",
            "teach back",
            "row-under-analysis premise",
            "perfect specificity",
            "unique attribution",
        ):
            self.assertIn(concept, combined)
        self.assertIn("answer one at a time", combined)
        self.assertIn("p05", combined)
        self.assertIn("p08", self.text["lesson.md"].lower())
        self.assertNotIn("planned concept loop", combined)

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
            "opaque FMEA toolbox": r"\b(fmea|riskprioritynumber|reliabilitymodel)\s*\(",
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
        self.assertIn("modeCount',3", model)

    def test_shared_entry_points_publish_p06_without_freezing_the_frontier(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        module_index = (ROOT / "modules/README.md").read_text(encoding="utf-8")
        for token in (
            "./bin/learn start P06",
            'launch_lesson("P06")',
            'run_module_checks("P06")',
        ):
            self.assertIn(token, readme)
        self.assertIn("P06", start_here)
        p06_row = next(line for line in module_index.splitlines() if line.startswith("| P06 |"))
        self.assertTrue(p06_row.endswith("| implemented |"))

    def test_retained_evidence_maps_acceptance_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P06-*.md"))
        self.assertTrue(records, "P06 retained evidence is missing")
        evidence = records[-1].read_text(encoding="utf-8")
        for marker in (
            "## Acceptance map",
            "## Exact validation commands and results",
            "## Figure, control, metric, and unit inventory",
            "## Runtime inventory",
            "## Changed and preserved invariants",
            "## Rollback",
            "## Residual risks",
            "## Unperformed validation",
            "MATLAB execution",
            "UI behavior",
            "numerical fidelity",
            "bench",
            "HIL",
            "field",
            "production",
            "**Disposition / evidence status:** pass",
            "Isolated candidate focused tests",
            "Final real-worktree full verification",
            "Post-review full verification",
            "Independent system-risk review repair",
            "test_pump_a_levers_preserve_non_target_observability_rows",
            "verify-20260901-010735.log",
            "70 tests, `OK`",
            "VERIFY PASS: 24 modules",
        ):
            self.assertIn(marker, evidence)
        self.assertNotIn("implementation candidate assembled", evidence)
        self.assertNotIn("real manifest remains `scaffolded`", evidence.lower())
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
