from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/08-prioritize-risk-quantitatively"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you "
    "prioritize Risk Quantitatively?"
)


class P08ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "curriculum/modules.json").read_text(encoding="utf-8")
        )
        cls.module = next(
            module for module in cls.manifest["modules"] if module["id"] == "P08"
        )
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p08_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 8)
        self.assertEqual(self.module["title"], "Prioritize Risk Quantitatively")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 2)
        self.assertEqual(self.module["phase_title"], "Failure analysis")
        self.assertEqual(self.module["slug"], "prioritize-risk-quantitatively")
        self.assertEqual(
            self.module["folder"],
            "modules/08-prioritize-risk-quantitatively",
        )
        self.assertEqual(self.module["prerequisites"], ["P07"])
        self.assertEqual(self.module["implementation_batch"], "P08")
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

    def test_guiding_question_and_prerequisite_chain_are_visible(self):
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
                self.assertIn("P07", self.text[name])
        combined = "\n".join(self.text.values())
        self.assertIn("P06", combined)
        self.assertIn("P05", combined)
        self.assertIn("fixed 1000-hour", combined)

    def test_model_exposes_transparent_probability_loss_and_rank_equations(self):
        model = self.text["model.m"]
        compact = re.sub(r"\s+|\.\.\.", "", model)
        for equation in (
            "scenarioProbabilities=[qS,rS*qA*qB,rS*rA*qB,rS*qA*rB];",
            "healthyProbability=rS*rA*rB;",
            "outcomeProbabilities=[scenarioProbabilitieshealthyProbability];",
            "systemFailureProbability=sum(outcomeProbabilities(1:2));",
            "systemReliability=sum(outcomeProbabilities(3:5));",
            "expectedLossKusdPerMission=scenarioProbabilities.*consequenceCostKusd;",
            "totalExpectedLossKusdPerMission=sum(expectedLossKusdPerMission);",
            "priorityOrder(priorityRanks)=scenarioIndexes;",
            "ordinalOccurrenceRatings=[2255];",
            "ordinalSeverityRatings=[5522];",
            "wrongOrdinalProductScores=ordinalOccurrenceRatings.*ordinalSeverityRatings;",
        ):
            self.assertIn(equation, compact)
        for output in (
            "scenarioProbabilities",
            "healthyProbability",
            "outcomeProbabilities",
            "systemFailureProbability",
            "systemReliability",
            "consequenceCostKusd",
            "expectedLossKusdPerMission",
            "riskShares",
            "priorityRanks",
            "priorityOrder",
            "totalLossSensitivityToSharedSupplyProbability",
            "wrongOrdinalProductScores",
            "riskUnit",
            "consequenceUnit",
        ):
            self.assertIn(output, model)
        self.assertEqual(model.count("(1,3) double"), 1)
        self.assertEqual(model.count("(1,4) double"), 1)
        self.assertIn("{'real','finite','>=',0,'<=',1}", model)
        self.assertIn("{'real','finite','>=',0,'<=',1e6}", model)
        for presentation_call in (
            "figure(",
            "plot(",
            "bar(",
            "scatter(",
            "uifigure",
            "uiaxes",
        ):
            self.assertNotIn(presentation_call, model.lower())

    def test_reference_outcomes_losses_shares_and_ranks_are_independently_known(self):
        q_s, q_a, q_b = 0.005, 0.10, 0.10
        outcomes = [
            q_s,
            (1 - q_s) * q_a * q_b,
            (1 - q_s) * (1 - q_a) * q_b,
            (1 - q_s) * q_a * (1 - q_b),
            (1 - q_s) * (1 - q_a) * (1 - q_b),
        ]
        expected_outcomes = [0.005, 0.00995, 0.08955, 0.08955, 0.80595]
        for actual, expected in zip(outcomes, expected_outcomes):
            self.assertAlmostEqual(actual, expected, places=15)
        self.assertAlmostEqual(sum(outcomes), 1, places=15)

        consequences = [120, 100, 8, 12]
        losses = [p * c for p, c in zip(outcomes[:4], consequences)]
        expected_losses = [0.6, 0.995, 0.7164, 1.0746]
        for actual, expected in zip(losses, expected_losses):
            self.assertAlmostEqual(actual, expected, places=15)
        total = sum(losses)
        self.assertAlmostEqual(total, 3.386, places=15)
        self.assertEqual(
            sorted(range(4), key=lambda index: (-losses[index], index)),
            [3, 1, 2, 0],
        )
        shares = [value / total for value in losses]
        self.assertAlmostEqual(sum(shares), 1, places=15)
        self.assertAlmostEqual(max(losses) - min(losses), 0.4746, places=15)

    def test_single_pump_loss_is_priced_without_becoming_mission_failure(self):
        q_s, q_a, q_b = 0.0, 1.0, 0.0
        outcomes = [
            q_s,
            (1 - q_s) * q_a * q_b,
            (1 - q_s) * (1 - q_a) * q_b,
            (1 - q_s) * q_a * (1 - q_b),
            (1 - q_s) * (1 - q_a) * (1 - q_b),
        ]
        self.assertEqual(outcomes, [0, 0, 0, 1, 0])
        self.assertEqual(sum(outcomes[:2]), 0)
        self.assertEqual(sum(outcomes[2:]), 1)
        self.assertEqual(
            [
                probability * consequence
                for probability, consequence in zip(
                    outcomes[:4], [120, 100, 8, 12]
                )
            ],
            [0, 0, 0, 12],
        )

        checks = re.sub(r"\s+|\.\.\.", "", self.text["run_checks.m"])
        for token in (
            "singlePumpFailure=model([010],baselineConsequences);",
            "singlePumpFailure.systemFailureProbability==0",
            "singlePumpFailure.systemReliability==1",
            "singlePumpFailure.healthyProbability==0",
            "singlePumpFailure.expectedLossKusdPerMission,[00012]",
        ):
            self.assertIn(token, checks)
        self.assertIn("degraded-operation loss", self.text["run_checks.m"])

        learner_text = "\n".join(
            self.text[name]
            for name in ("README.md", "lesson.md", "walkthrough.md", "checks.md")
        ).lower()
        self.assertIn("mission failure", learner_text)
        self.assertIn("degraded success", learner_text)

    def test_probability_sweep_reallocates_disjoint_scenarios_and_priority(self):
        q_s_sweep = [0, 0.005, 0.01, 0.02, 0.05]
        losses = []
        probabilities = []
        orders = []
        for q_s in q_s_sweep:
            scenario_probabilities = [
                q_s,
                (1 - q_s) * 0.10 * 0.10,
                (1 - q_s) * 0.90 * 0.10,
                (1 - q_s) * 0.10 * 0.90,
            ]
            scenario_losses = [
                probability * consequence
                for probability, consequence in zip(
                    scenario_probabilities, [120, 100, 8, 12]
                )
            ]
            probabilities.append(scenario_probabilities)
            losses.append(scenario_losses)
            orders.append(
                sorted(
                    range(4),
                    key=lambda index: (-scenario_losses[index], index),
                )
            )

        expected_probabilities = [
            [0, 0.01, 0.09, 0.09],
            [0.005, 0.00995, 0.08955, 0.08955],
            [0.01, 0.0099, 0.0891, 0.0891],
            [0.02, 0.0098, 0.0882, 0.0882],
            [0.05, 0.0095, 0.0855, 0.0855],
        ]
        expected_losses = [
            [0, 1.0, 0.72, 1.08],
            [0.6, 0.995, 0.7164, 1.0746],
            [1.2, 0.99, 0.7128, 1.0692],
            [2.4, 0.98, 0.7056, 1.0584],
            [6.0, 0.95, 0.684, 1.026],
        ]
        for actual_row, expected_row in zip(probabilities, expected_probabilities):
            for actual, expected in zip(actual_row, expected_row):
                self.assertAlmostEqual(actual, expected, places=15)
        for actual_row, expected_row in zip(losses, expected_losses):
            for actual, expected in zip(actual_row, expected_row):
                self.assertAlmostEqual(actual, expected, places=15)
        expected_totals = [2.8, 3.386, 3.972, 5.144, 8.66]
        for row, expected in zip(losses, expected_totals):
            self.assertAlmostEqual(sum(row), expected, places=14)
        self.assertEqual(orders[0], [3, 1, 2, 0])
        self.assertEqual(orders[2], [0, 3, 1, 2])

        experiment = self.text["experiment.m"]
        self.assertIn(
            "sharedSupplyFailureProbabilitySweep = [0 0.005 0.01 0.02 0.05]",
            experiment,
        )
        self.assertIn(
            "changed = model([sharedSupplyFailureProbabilitySweep(k) 0.10 0.10]",
            experiment,
        )
        checks = self.text["run_checks.m"]
        self.assertIn("Changing q_S must leave q_A and q_B unchanged", checks)
        self.assertIn("leave every consequence unchanged", checks)

    def test_consequence_sweep_isolates_probability_and_crosses_rank(self):
        scenario_probability = 0.995 * 0.10 * 0.10
        consequence_sweep = [0, 25, 50, 100, 200]
        dual_losses = [scenario_probability * value for value in consequence_sweep]
        expected_dual_losses = [0, 0.24875, 0.4975, 0.995, 1.99]
        for actual, expected in zip(dual_losses, expected_dual_losses):
            self.assertAlmostEqual(actual, expected, places=15)
        totals = [0.6 + value + 0.7164 + 1.0746 for value in dual_losses]
        for actual, expected in zip(
            totals, [2.391, 2.63975, 2.8885, 3.386, 4.381]
        ):
            self.assertAlmostEqual(actual, expected, places=15)
        self.assertAlmostEqual(scenario_probability * 108, 1.0746, places=15)

        experiment = self.text["experiment.m"]
        self.assertIn(
            "dualPumpConsequenceSweepKusd = [0 25 50 100 200]", experiment
        )
        self.assertIn(
            "[120 dualPumpConsequenceSweepKusd(k) 8 12]", experiment
        )
        checks = self.text["run_checks.m"]
        self.assertIn(
            "A consequence sweep must leave every scenario probability fixed", checks
        )
        self.assertIn("leave all non-target risks fixed", checks)

    def test_broken_ordinal_product_has_a_recognizable_nonquantitative_tie(self):
        occurrence_ratings = [2, 2, 5, 5]
        severity_ratings = [5, 5, 2, 2]
        products = [
            occurrence * severity
            for occurrence, severity in zip(occurrence_ratings, severity_ratings)
        ]
        self.assertEqual(products, [10, 10, 10, 10])
        self.assertEqual(max(products) - min(products), 0)
        self.assertAlmostEqual(1.0746 - 0.6, 0.4746, places=15)
        for name in ("README.md", "lesson.md", "checks.md", "experiment.m"):
            with self.subTest(name=name):
                self.assertIn("ordinal", self.text[name].lower())
        self.assertIn("no ratio-scale unit", self.text["experiment.m"])
        self.assertIn("all-tied symptom", self.text["run_checks.m"])

    def test_experiment_has_views_metrics_labels_two_sweeps_and_broken_case(self):
        experiment = self.text["experiment.m"]
        joined_experiment = re.sub(r"'\s*\.\.\.\s*\n\s*'", "", experiment)
        self.assertIn(
            "baseline = model([0.005 0.10 0.10],[120 100 8 12])", experiment
        )
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn("Baseline view 1", experiment)
        self.assertIn("Baseline view 2", experiment)
        self.assertIn("Baseline view 3", experiment)
        self.assertIn("Deliberately broken case", experiment)
        self.assertIn("brokenCase = model([0.005 0.10 0.10],[120 100 8 12])", experiment)
        self.assertIn("priority order", experiment.lower())
        for label in (
            "Scenario occurrence probability per fixed 1000-hour mission (dimensionless)",
            "Consequence cost (kUSD/scenario occurrence)",
            "Expected loss (kUSD/fixed 1000-hour mission)",
            "Shared-supply failure probability per fixed 1000-hour mission",
            "Dual-pump consequence cost (kUSD/scenario occurrence)",
            "Ordinal product score (no ratio-scale unit)",
        ):
            self.assertIn(label, joined_experiment)
        self.assertGreaterEqual(experiment.count("figure("), 6)
        self.assertNotIn("subplot(", experiment)
        sweep_one = experiment.split("%% Sweep 1", 1)[1].split("%% Sweep 2", 1)[0]
        sweep_two = experiment.split("%% Sweep 2", 1)[1].split(
            "%% Deliberately broken case", 1
        )[0]
        for section in (sweep_one, sweep_two):
            self.assertIn("scenarioIds = {'S','A&B','B only','A only'}", section)
            self.assertIn("colors = lines(4)", section)
            self.assertNotIn("baseline.", section)

    def test_interactive_controls_have_units_reset_and_one_view_at_a_time(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertEqual(interactive.count("uispinner"), 7)
        self.assertEqual(interactive.count("'Limits',[0 1]"), 3)
        self.assertEqual(interactive.count("'Limits',[0 1e6]"), 4)
        self.assertIn("q_S per fixed 1000 h mission (dimensionless)", interactive)
        self.assertIn("q_A per fixed 1000 h mission (dimensionless)", interactive)
        self.assertIn("q_B per fixed 1000 h mission (dimensionless)", interactive)
        self.assertIn("kUSD/scenario occurrence", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn(
            "{'Expected-loss priority','Probability-consequence plane'}", interactive
        )
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertIn("Reset baseline", interactive)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 8)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(probabilities,consequences)", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("does not waive a safety constraint", interactive)

    def test_checks_cover_positive_negative_malformed_recovery_isolation_and_bounds(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 35)
        for token in (
            "Identical inputs must produce identical outputs",
            "fixed 1x3 rows",
            "fixed 1x4 rows",
            "fixed 1x5 row",
            "retain P06 and P07 basic-event identity",
            "five mutually exclusive P07 outcomes must close to one",
            "first two outcomes must remain P07 mission failures",
            "expected losses must equal probability times consequence",
            "total expected loss must independently equal 3.3860",
            "Baseline priority must be A only, A&B, B only, then S",
            "Changing q_S must leave q_A and q_B unchanged",
            "q_S sweep totals must match independent references",
            "first post-crossover sample at 0.01",
            "cross at the exact q_S value",
            "consequence sweep must leave every scenario probability fixed",
            "cross at 108 kUSD",
            "No basic-event failures",
            "Certain supply failure",
            "Certain dual-pump loss",
            "certain Pump-A failure with Pump B working",
            "Zero consequences",
            "nonzero partial tie",
            "Swapping Pump A and B",
            "representable tiny scenario",
            "fixed consequence resource bound",
            "all-tied symptom",
            "wrong-length basic-event vector must be rejected",
            "negative basic-event probability must be rejected",
            "basic-event probability above one must be rejected",
            "nonfinite basic-event probability must be rejected",
            "wrong-length consequence vector must be rejected",
            "negative consequence must be rejected",
            "consequence above the resource bound must be rejected",
            "complex consequence must be rejected",
            "must not contaminate exact recovery",
            "P08 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertGreaterEqual(checks.count("assertRejects("), 14)

        applicability = self.text["checks.md"].lower()
        for token in (
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
        probability_position = lesson_script.index("bar(")
        ranking_position = lesson_script.index("bar(", probability_position + 1)
        interactive_position = lesson_script.index("interactive;")
        self.assertLess(probability_position, ranking_position)
        self.assertLess(ranking_position, interactive_position)

        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "disjoint",
            "probability",
            "consequence",
            "expected loss",
            "common",
            "kusd",
            "ordinal",
            "ratio-scale",
            "detection coverage",
            "safety constraint",
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
            "opaque risk toolbox": (
                r"\b(riskprioritynumber|riskmatrix|fmea|rbd|faulttree|reliabilitymodel)\s*\("
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
        self.assertIn("'<=',1e6", model)
        self.assertIn("scenarioIndexes = 1:4", model)

    def test_shared_entry_points_publish_p08_without_freezing_later_frontier(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
        module_index = (ROOT / "modules/README.md").read_text(encoding="utf-8")
        for token in (
            "./bin/learn start P08",
            'launch_lesson("P08")',
            'run_module_checks("P08")',
        ):
            self.assertIn(token, readme)
        self.assertIn("P08", start_here)
        p08_row = next(
            line for line in module_index.splitlines() if line.startswith("| P08 |")
        )
        self.assertTrue(p08_row.endswith("| implemented |"))

    def test_retained_evidence_maps_acceptance_results_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P08-*.md"))
        self.assertTrue(records, "P08 retained evidence is missing")
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
            "## Focused behavior matrix",
            "## Independent system-risk review and repair",
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
            "timeout",
            "cancellation",
            "rollback",
            "recovery",
            "isolation",
            "compatibility",
            "resource bound",
            "Disposition / evidence status:** implemented;",
            "15 tests, `OK`",
            "99 tests, `OK`",
            "VERIFY PASS: 24 modules",
            "MATLAB_LEARNING_VERIFY_PROFILE=contract",
            "MATLAB_LEARNING_VERIFY_PROFILE=quick",
            "MATLAB_LEARNING_VERIFY_PROFILE=full",
        ):
            self.assertIn(marker.lower(), evidence.lower())
        for obsolete in (
            "implementation candidate assembled",
            "real manifest remains unchanged",
            "lifecycle gate pending",
            "pending by design",
        ):
            self.assertNotIn(obsolete, evidence.lower())
        payload = records[-1].read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
