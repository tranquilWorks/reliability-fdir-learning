from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/07-construct-a-reliability-block-diagram"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you "
    "construct a Reliability Block Diagram?"
)


class P07ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P07"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p07_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 7)
        self.assertEqual(self.module["title"], "Construct a Reliability Block Diagram")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 2)
        self.assertEqual(self.module["phase_title"], "Failure analysis")
        self.assertEqual(self.module["slug"], "construct-a-reliability-block-diagram")
        self.assertEqual(
            self.module["folder"],
            "modules/07-construct-a-reliability-block-diagram",
        )
        self.assertEqual(self.module["prerequisites"], ["P06"])
        self.assertEqual(self.module["implementation_batch"], "P07")
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

    def test_guiding_question_and_p06_connection_are_visible(self):
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
                self.assertIn("P06", self.text[name])
        combined = "\n".join(self.text.values())
        self.assertIn("S AND (A OR B)", combined)
        self.assertIn("P05", combined)
        self.assertIn("P04", combined)

    def test_model_exposes_transparent_rbd_and_overlap_equations(self):
        model = self.text["model.m"]
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "pumpGroupReliability=pumpAReliability+"
            "pumpAFailureProbability*pumpBReliability;",
            "pumpGroupFailureProbability=pumpAFailureProbability*"
            "pumpBFailureProbability;",
            "systemReliability=sharedSupplyReliability*pumpGroupReliability;",
            "dualPumpFailureContribution=sharedSupplyReliability*"
            "pumpGroupFailureProbability;",
            "systemFailureProbability=sharedSupplyFailureContribution+"
            "dualPumpFailureContribution;",
            "successPathOverlapProbability=sharedSupplyReliability*"
            "pumpAReliability*pumpBReliability;",
            "inclusionExclusionReliability=rawSuccessPathSum-"
            "successPathOverlapProbability;",
            "wrongReliabilityOverstatement=sharedSupplyReliability*"
            "sharedSupplyFailureProbability*pumpAReliability*"
            "pumpBReliability;",
            "wrongIndependentPathReliability=systemReliability+"
            "wrongReliabilityOverstatement;",
        ):
            self.assertIn(equation, compact)
        for output in (
            "blockReliabilities",
            "pumpGroupReliability",
            "systemReliability",
            "systemFailureProbability",
            "minimalPathReliabilities",
            "successPathOverlapProbability",
            "outcomeProbabilities",
            "wrongIndependentPathReliability",
            "wrongReliabilityOverstatement",
            "pathIncidence",
            "successLogic",
        ):
            self.assertIn(output, model)
        self.assertEqual(model.count("(1,1) double"), 3)
        self.assertEqual(model.count("{'real','finite','>=',0,'<=',1}"), 3)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "rectangle(",
            "uifigure",
            "uiaxes",
        ):
            self.assertNotIn(presentation_call, model.lower())

    def test_reference_values_outcomes_and_p05_complement_are_independently_known(self):
        rs, ra, rb = 0.995, 0.90, 0.90
        pump_group = ra + (1 - ra) * rb
        reliability = rs * pump_group
        failure = (1 - rs) + rs * (1 - ra) * (1 - rb)
        outcomes = [
            1 - rs,
            rs * (1 - ra) * (1 - rb),
            rs * ra * (1 - rb),
            rs * (1 - ra) * rb,
            rs * ra * rb,
        ]
        expected = [0.00500, 0.00995, 0.08955, 0.08955, 0.80595]
        self.assertAlmostEqual(pump_group, 0.99, places=15)
        self.assertAlmostEqual(reliability, 0.98505, places=15)
        self.assertAlmostEqual(failure, 0.01495, places=15)
        self.assertAlmostEqual(reliability + failure, 1, places=15)
        for actual, reference in zip(outcomes, expected):
            self.assertAlmostEqual(actual, reference, places=15)
        self.assertAlmostEqual(sum(outcomes), 1, places=15)
        self.assertAlmostEqual(sum(outcomes[2:]), reliability, places=15)
        self.assertAlmostEqual(sum(outcomes[:2]), failure, places=15)
        self.assertAlmostEqual(failure, 0.005 + 0.995 * 0.10 * 0.10, places=15)

    def test_success_paths_overlap_and_broken_case_have_recognizable_symptoms(self):
        rs, ra, rb = 0.995, 0.90, 0.90
        path_a, path_b = rs * ra, rs * rb
        overlap = rs * ra * rb
        correct = path_a + path_b - overlap
        wrong_independent = path_a + (1 - path_a) * path_b
        self.assertAlmostEqual(path_a, 0.89550, places=15)
        self.assertAlmostEqual(path_b, 0.89550, places=15)
        self.assertGreater(path_a + path_b, 1)
        self.assertAlmostEqual(overlap, 0.80595, places=15)
        self.assertAlmostEqual(correct, 0.98505, places=15)
        self.assertAlmostEqual(wrong_independent, 0.98907975, places=15)

        stressed_rs = 0.80
        stressed_path = stressed_rs * 0.90
        stressed_correct = stressed_rs * (0.90 + 0.10 * 0.90)
        stressed_wrong = stressed_path + (1 - stressed_path) * stressed_path
        self.assertAlmostEqual(stressed_correct, 0.7920, places=15)
        self.assertAlmostEqual(stressed_wrong, 0.9216, places=15)
        self.assertAlmostEqual(stressed_wrong - stressed_correct, 0.1296, places=15)
        self.assertAlmostEqual(
            stressed_wrong - stressed_correct,
            stressed_rs * (1 - stressed_rs) * 0.90 * 0.90,
            places=15,
        )
        near_rs = 1 - math.ulp(1.0)
        near_gap = near_rs * (1 - near_rs) * 0.10 * 0.50
        self.assertGreater(near_gap, 0)
        self.assertGreaterEqual(
            near_rs * (0.10 + 0.90 * 0.50) + near_gap,
            near_rs * (0.10 + 0.90 * 0.50),
        )
        self.assertGreater(2 * stressed_path, 1)

    def test_two_sweeps_have_independent_reference_behavior(self):
        supply_sweep = [0, 0.50, 0.90, 0.995, 1]
        supply_results = [rs * (0.90 + 0.10 * 0.90) for rs in supply_sweep]
        supply_failures = [
            (1 - rs) + rs * 0.10 * 0.10 for rs in supply_sweep
        ]
        for actual, expected in zip(
            supply_results, [0, 0.495, 0.891, 0.98505, 0.99]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        for actual, expected in zip(
            supply_failures, [1, 0.505, 0.109, 0.01495, 0.01]
        ):
            self.assertAlmostEqual(actual, expected, places=15)

        pump_a_sweep = [0, 0.25, 0.50, 0.75, 1]
        pump_a_results = [0.995 * (ra + (1 - ra) * 0.90) for ra in pump_a_sweep]
        for actual, expected in zip(
            pump_a_results, [0.8955, 0.920375, 0.94525, 0.970125, 0.995]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        self.assertTrue(all(a < b for a, b in zip(supply_results, supply_results[1:])))
        self.assertTrue(all(a < b for a, b in zip(pump_a_results, pump_a_results[1:])))

        experiment = self.text["experiment.m"]
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn(
            "sharedSupplyReliabilitySweep = [0 0.50 0.90 0.995 1]", experiment
        )
        self.assertIn("changed = model(sharedSupplyReliabilitySweep(k),0.90,0.90)", experiment)
        self.assertIn("pumpAReliabilitySweep = [0 0.25 0.50 0.75 1]", experiment)
        self.assertIn("changed = model(0.995,pumpAReliabilitySweep(k),0.90)", experiment)

    def test_outcome_ledger_tracks_each_lever_without_stale_or_coupled_states(self):
        def outcome_ledger(rs, ra, rb):
            return [
                1 - rs,
                rs * (1 - ra) * (1 - rb),
                rs * ra * (1 - rb),
                rs * (1 - ra) * rb,
                rs * ra * rb,
            ]

        supply_sweep = [0, 0.50, 0.90, 0.995, 1]
        supply_ledgers = [outcome_ledger(rs, 0.90, 0.90) for rs in supply_sweep]
        expected_supply_ledgers = [
            [1, 0, 0, 0, 0],
            [0.50, 0.005, 0.045, 0.045, 0.405],
            [0.10, 0.009, 0.081, 0.081, 0.729],
            [0.005, 0.00995, 0.08955, 0.08955, 0.80595],
            [0, 0.01, 0.09, 0.09, 0.81],
        ]
        for actual, expected in zip(supply_ledgers, expected_supply_ledgers):
            for value, reference in zip(actual, expected):
                self.assertAlmostEqual(value, reference, places=15)
            self.assertAlmostEqual(sum(actual), 1, places=15)
            self.assertAlmostEqual(sum(actual[:2]), 1 - sum(actual[2:]), places=15)
        self.assertTrue(
            all(
                earlier[0] > later[0]
                for earlier, later in zip(supply_ledgers, supply_ledgers[1:])
            )
        )
        for outcome_index in range(1, 5):
            self.assertTrue(
                all(
                    earlier[outcome_index] < later[outcome_index]
                    for earlier, later in zip(
                        supply_ledgers, supply_ledgers[1:]
                    )
                )
            )

        pump_a_sweep = [0, 0.25, 0.50, 0.75, 1]
        pump_a_ledgers = [outcome_ledger(0.995, ra, 0.90) for ra in pump_a_sweep]
        expected_pump_a_ledgers = [
            [0.005, 0.0995, 0, 0.8955, 0],
            [0.005, 0.074625, 0.024875, 0.671625, 0.223875],
            [0.005, 0.04975, 0.04975, 0.44775, 0.44775],
            [0.005, 0.024875, 0.074625, 0.223875, 0.671625],
            [0.005, 0, 0.0995, 0, 0.8955],
        ]
        for actual, expected in zip(pump_a_ledgers, expected_pump_a_ledgers):
            for value, reference in zip(actual, expected):
                self.assertAlmostEqual(value, reference, places=15)
            self.assertAlmostEqual(sum(actual), 1, places=15)
            self.assertAlmostEqual(sum(actual[:2]), 1 - sum(actual[2:]), places=15)
            self.assertAlmostEqual(actual[0], 0.005, places=15)
        for outcome_index in (1, 3):
            self.assertTrue(
                all(
                    earlier[outcome_index] > later[outcome_index]
                    for earlier, later in zip(
                        pump_a_ledgers, pump_a_ledgers[1:]
                    )
                )
            )
        for outcome_index in (2, 4):
            self.assertTrue(
                all(
                    earlier[outcome_index] < later[outcome_index]
                    for earlier, later in zip(
                        pump_a_ledgers, pump_a_ledgers[1:]
                    )
                )
            )

        interactive = re.sub(r"\s+|\.\.\.", "", self.text["interactive.m"])
        self.assertIn("bar(displayAxes,1:5,out.outcomeProbabilities,0.68);", interactive)
        checks = re.sub(r"\s+|\.\.\.", "", self.text["run_checks.m"])
        for token in (
            "actualOutcomeSupplySweep(k,:)=changed.outcomeProbabilities;",
            "actualOutcomePumpASweep(k,:)=changed.outcomeProbabilities;",
            "EveryR_Ssweeppointmustretaintheexactfive-stateoutcomeledger.",
            "EveryR_Asweeppointmustretaintheexactfive-stateoutcomeledger.",
        ):
            self.assertIn(token, checks)

    def test_experiment_has_views_metrics_labels_and_one_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertIn("baseline = model(0.995,0.90,0.90)", experiment)
        self.assertIn("drawCorrectRbd(topologyAxes,baseline)", experiment)
        self.assertIn("baseline.outcomeProbabilities", experiment)
        self.assertIn("Baseline R_pumps", experiment)
        self.assertIn("Deliberately broken case", experiment)
        self.assertIn("brokenCase = model(0.80,0.90,0.90)", experiment)
        self.assertIn("drawDuplicatedSupplyRbd(wrongAxes,brokenCase)", experiment)
        self.assertIn("wrong independent-path R", experiment)
        self.assertIn("raw path sum", experiment)
        self.assertIn("P05 top-event probability = %.5f", experiment)
        self.assertNotIn("P05 top-event complement = %.5f", experiment)
        for label in (
            "Outcome probability per fixed 1000-hour mission (dimensionless)",
            "Shared-supply block reliability per fixed mission (dimensionless)",
            "Pump-A block reliability per fixed mission (dimensionless)",
            "Success probability (dimensionless)",
            "Claimed mission reliability (dimensionless)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 6)
        self.assertNotIn("subplot(", experiment)

    def test_interactive_controls_have_units_reset_and_one_view_at_a_time(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertEqual(interactive.count("uispinner"), 3)
        self.assertEqual(interactive.count("'Limits',[0 1]"), 3)
        self.assertIn(
            "Shared-supply reliability per fixed 1000 h (dimensionless)", interactive
        )
        self.assertIn("Pump-A reliability per fixed 1000 h (dimensionless)", interactive)
        self.assertIn("Pump-B reliability per fixed 1000 h (dimensionless)", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn("{'RBD topology','Disjoint outcome ledger'}", interactive)
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 4)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("success is S AND (A OR B)", interactive)
        self.assertIn("P06 detection coverage", interactive)

    def test_checks_cover_invariants_limits_malformed_recovery_isolation_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 50)
        for token in (
            "Identical inputs must produce identical outputs",
            "fixed 1x3 rows",
            "fixed 2x3 incidence",
            "fixed 1x5 row",
            "shared-supply and two-pump block identity",
            "S AND (A OR B)",
            "independent block-event assumption",
            "System reliability and failure probability must close to one",
            "baseline RBD reliability must independently equal 0.98505",
            "P05 failure terms",
            "complete probability partition",
            "Inclusion-exclusion must recover",
            "Eight-state truth enumeration",
            "Changing R_S must leave both pump block inputs unchanged",
            "parallel pump group must remain fixed throughout sweep 1",
            "Changing R_A must leave the shared supply and Pump B unchanged",
            "shared-supply failure contribution must remain fixed in sweep 2",
            "certainly failed shared supply",
            "Either perfect pump",
            "Swapping Pump A and Pump B",
            "representable tiny success contribution",
            "tiny dual-pump failure product",
            "Duplicated independent supply drawings",
            "missing shared-path overlap",
            "nonscalar shared-supply reliability must be rejected",
            "negative Pump-A reliability must be rejected",
            "Pump-B reliability above one must be rejected",
            "Rejected malformed calls must not contaminate",
            "P07 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertGreaterEqual(checks.count("assertRejects("), 18)

        check_text = self.text["checks.md"]
        for applicability in (
            "timeout",
            "cancellation",
            "variable-resource",
            "not applicable",
            "exact recovery",
        ):
            self.assertIn(applicability, check_text)

    def test_lesson_is_concept_first_with_interpretation_and_teach_back(self):
        lesson_script = self.text["lesson.m"]
        topology_position = lesson_script.index("drawCorrectRbd(")
        ledger_position = lesson_script.index("bar(")
        interactive_position = lesson_script.index("interactive;")
        self.assertLess(topology_position, ledger_position)
        self.assertLess(ledger_position, interactive_position)

        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "functional success",
            "mission boundary",
            "series",
            "parallel",
            "minimal success paths",
            "inclusion-exclusion",
            "independence",
            "detection coverage",
            "duplicated",
            "teach-back",
        ):
            self.assertIn(concept, combined)
        self.assertIn("answer one at a time", combined)
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
            "opaque reliability toolbox": (
                r"\b(rbd|reliabilityblockdiagram|reliabilitymodel|ftree|faulttree)\s*\("
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
        self.assertIn("out.pathIncidence = [1 1 0;1 0 1]", model)
        self.assertIn("outcomeProbabilities = [", model)

    def test_shared_entry_points_publish_p07_without_freezing_later_frontier(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        module_index = (ROOT / "modules/README.md").read_text(encoding="utf-8")
        for token in (
            "./bin/learn start P07",
            'launch_lesson("P07")',
            'run_module_checks("P07")',
        ):
            self.assertIn(token, readme)
        self.assertIn("P07", start_here)
        p07_row = next(line for line in module_index.splitlines() if line.startswith("| P07 |"))
        self.assertTrue(p07_row.endswith("| implemented |"))

    def test_retained_evidence_maps_acceptance_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P07-*.md"))
        self.assertTrue(records, "P07 retained evidence is missing")
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
            "Disposition / evidence status:** implemented",
            "13 tests, `OK`",
            "83 tests, `OK`",
            "14 tests, `OK`",
            "84 tests, `OK`",
            "VERIFY PASS: 24 modules",
            "Isolated implemented-candidate gate",
            "Final real-worktree gates after manifest transition",
            "Independent system-risk review repair",
            "test_outcome_ledger_tracks_each_lever_without_stale_or_coupled_states",
        ):
            self.assertIn(marker, evidence)
        for stale_marker in (
            "candidate verification in progress",
            "lifecycle gate pending",
            "Pending candidate gate",
            "Exact commands and results will be recorded",
        ):
            self.assertNotIn(stale_marker, evidence)
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
