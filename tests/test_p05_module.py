from __future__ import annotations

import itertools
import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/05-build-a-fault-tree"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you build "
    "a Fault Tree?"
)


class P05ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P05"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p05_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 5)
        self.assertEqual(self.module["title"], "Build a Fault Tree")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 2)
        self.assertEqual(self.module["phase_title"], "Failure analysis")
        self.assertEqual(self.module["slug"], "build-a-fault-tree")
        self.assertEqual(self.module["folder"], "modules/05-build-a-fault-tree")
        self.assertEqual(self.module["prerequisites"], ["P04"])
        self.assertEqual(self.module["implementation_batch"], "P05")
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

    def test_guiding_question_and_p04_connection_are_visible(self):
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
        ):
            with self.subTest(name=name):
                self.assertIn("P04", self.text[name])

    def test_model_exposes_transparent_fault_tree_equations(self):
        model = self.text["model.m"]
        for token in (
            "sharedCutSetProbability = sharedSupplyFailureProbability",
            "pumpAFailureProbability*pumpBFailureProbability",
            "cutSetOverlapProbability = sharedSupplyFailureProbability*",
            "dualPumpExclusiveContribution = noSharedSupplyFailureProbability*",
            "topEventProbability = sharedCutSetProbability +",
            "coolingAvailableProbability = noSharedSupplyFailureProbability*",
            "pumpOrFailureProbability = pumpAFailureProbability +",
            "wrongGateTopEventProbability = sharedSupplyFailureProbability +",
        ):
            self.assertIn(token, model)
        for output in (
            "minimalCutSetProbabilities",
            "disjointContributionProbabilities",
            "topEventProbability",
            "coolingAvailableProbability",
            "topEventSensitivityToSharedSupply",
            "wrongGateTopEventProbability",
        ):
            self.assertIn(f"'{output}'", model)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "uifigure",
            "uiaxes",
            "uilabel",
        ):
            self.assertNotIn(presentation_call, model.lower())
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "dualPumpCutSetProbability=pumpAFailureProbability*pumpBFailureProbability;",
            "dualPumpExclusiveContribution=noSharedSupplyFailureProbability*dualPumpCutSetProbability;",
            "topEventProbability=sharedCutSetProbability+dualPumpExclusiveContribution;",
            "coolingAvailableProbability=noSharedSupplyFailureProbability*(1-dualPumpCutSetProbability);",
            "pumpOrFailureProbability=pumpAFailureProbability+(1-pumpAFailureProbability)*pumpBFailureProbability;",
        ):
            self.assertIn(equation, compact)
        self.assertEqual(
            model.count("{'real','finite','>=',0,'<=',1}"), 3
        )

    def test_reference_values_truth_table_and_broken_case_are_independently_known(self):
        shared = 0.005
        pump_a = 0.10
        pump_b = 0.10
        dual_cut_set = pump_a * pump_b
        dual_exclusive = (1 - shared) * dual_cut_set
        top_event = shared + dual_exclusive
        cooling_available = (1 - shared) * (1 - dual_cut_set)
        wrong_pump_or = pump_a + (1 - pump_a) * pump_b
        wrong_top_event = shared + (1 - shared) * wrong_pump_or

        self.assertAlmostEqual(dual_cut_set, 0.01, places=15)
        self.assertAlmostEqual(dual_exclusive, 0.00995, places=15)
        self.assertAlmostEqual(top_event, 0.01495, places=15)
        self.assertAlmostEqual(cooling_available, 0.98505, places=15)
        self.assertAlmostEqual(wrong_top_event, 0.19405, places=15)
        self.assertAlmostEqual(wrong_top_event - top_event, 0.17910, places=15)
        self.assertGreater(wrong_top_event / top_event, 10)

        states = list(itertools.product((0, 1), repeat=3))
        correct = [bool(s or (a and b)) for s, a, b in states]
        broken = [bool(s or a or b) for s, a, b in states]
        self.assertEqual(correct, [False, False, False, True, True, True, True, True])
        self.assertFalse(correct[1])
        self.assertTrue(broken[1])
        self.assertFalse(correct[2])
        self.assertTrue(broken[2])

        raw_cut_set_sum = 0.8 + 0.8 * 0.8
        exact_union = 0.8 + (1 - 0.8) * 0.8 * 0.8
        self.assertAlmostEqual(raw_cut_set_sum, 1.44, places=15)
        self.assertAlmostEqual(exact_union, 0.928, places=15)

    def test_two_levers_have_isolated_reference_behavior_and_limits(self):
        shared_sweep = [0, 0.005, 0.02, 0.05]
        shared_results = [value + (1 - value) * 0.10 * 0.10 for value in shared_sweep]
        for actual, expected in zip(
            shared_results, [0.01, 0.01495, 0.0298, 0.0595]
        ):
            self.assertAlmostEqual(actual, expected, places=15)

        pump_a_sweep = [0, 0.05, 0.10, 0.20, 0.40]
        pump_results = [0.005 + (1 - 0.005) * value * 0.10 for value in pump_a_sweep]
        expected_pump_results = [0.005, 0.009975, 0.01495, 0.0249, 0.0448]
        for actual, expected in zip(pump_results, expected_pump_results):
            self.assertAlmostEqual(actual, expected, places=15)

        self.assertEqual(0 + (1 - 0) * 0.2 * 0.3, 0.2 * 0.3)
        self.assertEqual(0.3 + (1 - 0.3) * 0 * 0.8, 0.3)
        self.assertEqual(0.3 + (1 - 0.3) * 0.8 * 0, 0.3)
        self.assertEqual(1 + (1 - 1) * 0.2 * 0.3, 1)
        self.assertEqual(0.005 + 0.995 * 0.10 * 0.25, 0.005 + 0.995 * 0.25 * 0.10)
        tiny_and = 1e-150 * 1e-150
        self.assertGreater(tiny_and, 0)
        self.assertTrue(math.isfinite(tiny_and))
        self.assertAlmostEqual(tiny_and / 1e-300, 1, places=14)

    def test_shared_supply_lever_moves_disjoint_paths_in_opposite_directions(self):
        shared_sweep = [0, 0.005, 0.02, 0.05]
        raw_dual_cut_sets = [0.10 * 0.10 for _ in shared_sweep]
        shared_paths = list(shared_sweep)
        dual_pump_disjoint_paths = [
            (1 - shared) * raw_dual
            for shared, raw_dual in zip(shared_sweep, raw_dual_cut_sets)
        ]
        top_events = [
            shared + dual
            for shared, dual in zip(shared_paths, dual_pump_disjoint_paths)
        ]

        for raw_dual in raw_dual_cut_sets:
            self.assertAlmostEqual(raw_dual, 0.01, places=15)
        self.assertTrue(
            all(
                earlier < later
                for earlier, later in zip(shared_paths, shared_paths[1:])
            )
        )
        self.assertTrue(
            all(
                earlier > later
                for earlier, later in zip(
                    dual_pump_disjoint_paths, dual_pump_disjoint_paths[1:]
                )
            )
        )
        self.assertTrue(
            all(
                earlier < later
                for earlier, later in zip(top_events, top_events[1:])
            )
        )
        for shared, dual, top in zip(
            shared_paths, dual_pump_disjoint_paths, top_events
        ):
            self.assertAlmostEqual(shared + dual, top, places=15)

        experiment = re.sub(r"\s+|\.\.\.", "", self.text["experiment.m"])
        self.assertIn(
            "sharedContributionSweep(k)=changed.sharedExclusiveContribution;",
            experiment,
        )
        self.assertIn(
            "dualPumpContributionSharedSweep(k)="
            "changed.dualPumpExclusiveContribution;",
            experiment,
        )
        checks = self.text["run_checks.m"]
        for token in (
            "The shared path must equal qS throughout the shared-supply sweep",
            "Increasing qS must raise the shared path while reducing the",
            "The swept disjoint paths must add to the exact top event",
        ):
            self.assertIn(token, checks)

    def test_experiment_has_two_independent_sweeps_metrics_views_and_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertIn("baseline = model(0.005,0.10,0.10)", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn(
            "sharedSupplyProbabilitySweep = [0 0.005 0.02 0.05]", experiment
        )
        self.assertIn(
            "changed = model(sharedSupplyProbabilitySweep(k),0.10,0.10)",
            experiment,
        )
        self.assertIn(
            "pumpAFailureProbabilitySweep = [0 0.05 0.10 0.20 0.40]",
            experiment,
        )
        self.assertIn(
            "changed = model(0.005,pumpAFailureProbabilitySweep(k),0.10)",
            experiment,
        )
        self.assertIn("Baseline metrics per 1000-hour mission:", experiment)
        self.assertIn("drawFaultTree(treeAxes,baseline)", experiment)
        self.assertIn("Disjoint contributions:", experiment)
        self.assertIn("brokenCase = model(0.005,0.10,0.10)", experiment)
        self.assertIn("wrong pump-OR gate", experiment)
        self.assertIn("S=0, A=1, B=0", experiment)
        for label in (
            "Shared-supply failure probability per mission (dimensionless)",
            "Pump-A failure probability per mission (dimensionless)",
            "Event probability per mission (dimensionless)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 5)
        self.assertNotIn("subplot(", experiment)

    def test_interactive_controls_have_units_reset_and_one_view_at_a_time(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertEqual(interactive.count("uispinner"), 3)
        self.assertEqual(interactive.count("'Limits',[0 1]"), 3)
        self.assertIn("Shared-supply failure per mission (dimensionless)", interactive)
        self.assertIn("Pump-A failure per mission (dimensionless)", interactive)
        self.assertIn("Pump-B failure per mission (dimensionless)", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn(
            "{'Fault-tree structure','Non-overlapping contributions'}", interactive
        )
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 4)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("T = S OR (A AND B)", interactive)
        joined_interactive = re.sub(
            r"'\s*\.\.\.\s*\n\s*'", "", interactive
        )
        self.assertIn(
            "Gate logic and the all-three-basic-event independence assumption "
            "are separate claims",
            joined_interactive,
        )
        self.assertIn("Mission boundary: fixed 1000 h, no repair", interactive)

    def test_checks_cover_invariants_truth_limits_malformed_recovery_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 35)
        for token in (
            "Identical inputs must produce identical outputs",
            "two fixed-size cut-set views",
            "probabilities must be complementary",
            "mutually exclusive contributions must add",
            "Inclusion-exclusion must agree",
            "cut-set probability must independently equal qA*qB",
            "baseline top-event probability must match",
            "baseline qS sensitivity must independently equal",
            "Each baseline pump sensitivity must equal",
            "Truth-state enumeration must implement S OR (A AND B)",
            "only the broken OR gate may activate the top event",
            "Independent Boolean-state probabilities must form a complete partition",
            "shared-supply sweep must match independent reference values",
            "Changing qS must not change the raw {A,B}",
            "pump-A sweep must match independent reference values",
            "Changing qA must leave the shared-event contribution unchanged",
            "Swapping pump A and pump B",
            "With qS=0",
            "Either zero pump probability",
            "certain shared-supply loss",
            "All-zero basic-event probabilities",
            "representable tiny AND probability",
            "raw cut-set sum may exceed one",
            "broken pump-OR gate",
            "negative shared-supply probability must be rejected",
            "shared-supply probability above one must be rejected",
            "nonfinite pump-A probability must be rejected",
            "complex pump-A probability must be rejected",
            "nonscalar pump-A probability must be rejected",
            "negative pump-B probability must be rejected",
            "pump-B probability above one must be rejected",
            "must not contaminate a later valid calculation",
            "P05 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertGreaterEqual(checks.count("assertRejects("), 18)

    def test_lesson_is_concept_first_with_interpretation_and_teach_back(self):
        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "mission boundary",
            "minimal cut sets",
            "shared supply",
            "and gate",
            "independence",
            "1000-hour",
            "teach back",
        ):
            self.assertIn(concept, combined)
        self.assertIn("answer one at a time", combined)
        self.assertIn("p04", combined)
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
            "opaque fault-tree toolbox": r"\b(ftree|faulttree|reliabilitymodel)\s*\(",
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
        self.assertEqual(model.count("(1,1) double"), 3)
        self.assertIsNone(re.search(r"(?m)^\s*(for|while)\b", model))

    def test_retained_evidence_maps_acceptance_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P05-*.md"))
        self.assertTrue(records, "P05 retained evidence is missing")
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
        ):
            self.assertIn(marker, evidence)
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
