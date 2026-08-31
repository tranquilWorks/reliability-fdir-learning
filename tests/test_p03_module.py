from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/03-compute-availability-from-failure-and-repair"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you compute "
    "Availability from Failure and Repair?"
)


class P03ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "curriculum/modules.json").read_text(encoding="utf-8"))
        cls.module = next(module for module in cls.manifest["modules"] if module["id"] == "P03")
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p03_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 3)
        self.assertEqual(self.module["title"], "Compute Availability from Failure and Repair")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 1)
        self.assertEqual(self.module["phase_title"], "Reliability fundamentals")
        self.assertEqual(self.module["slug"], "compute-availability-from-failure-and-repair")
        self.assertEqual(
            self.module["folder"],
            "modules/03-compute-availability-from-failure-and-repair",
        )
        self.assertEqual(self.module["prerequisites"], ["P02"])
        self.assertEqual(self.module["implementation_batch"], "P03")
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

    def test_guiding_question_and_p02_connection_are_visible(self):
        for name in ("README.md", "lesson.md", "walkthrough.md", "lesson.m", "experiment.m"):
            with self.subTest(name=name):
                normalized = " ".join(self.text[name].replace("%", " ").split())
                self.assertIn(QUESTION, normalized)
        for name in ("README.md", "lesson.md", "walkthrough.md", "checks.md", "lesson.m"):
            with self.subTest(name=name):
                self.assertIn("P02", self.text[name])

    def test_model_exposes_transparent_failure_repair_equations(self):
        model = self.text["model.m"]
        for token in (
            "repairRatePerHour = 1/meanRepairTimeHours",
            "transitionRatePerHour = failureRatePerHour+repairRatePerHour",
            "failureToRepairRatio = failureRatePerHour*meanRepairTimeHours",
            "steadyAvailability = 1/(1+failureToRepairRatio)",
            "steadyUnavailability = failureToRepairRatio/(1+failureToRepairRatio)",
            "equilibriumProgress = -expm1(-transitionRatePerHour*timeHours)",
            "equilibriumRemainder = exp(-transitionRatePerHour*timeHours)",
            "availabilityProbability = steadyAvailability*equilibriumProgress",
            "unavailabilityProbability = steadyUnavailability*equilibriumProgress",
            "failureTransitionFlowPerHour = failureRatePerHour*availabilityProbability",
            "repairTransitionFlowPerHour = repairRatePerHour*unavailabilityProbability",
        ):
            self.assertIn(token, model)
        for output in (
            "availabilityProbability",
            "unavailabilityProbability",
            "steadyAvailability",
            "steadyExpectedDowntimeHoursPerYear",
            "relaxationTimeHours",
            "endpointAvailability",
            "endpointUnavailability",
        ):
            self.assertIn(f"'{output}'", model)
        self.assertNotIn("'missionAvailability'", model)
        self.assertNotIn("'missionUnavailability'", model)
        for presentation_call in ("figure(", "plot(", "uifigure", "uiaxes", "uilabel"):
            self.assertNotIn(presentation_call, model.lower())

    def test_reference_values_limits_and_cancellation_are_independently_known(self):
        failure_rate = 1e-3
        repair_hours = 10
        repair_rate = 1 / repair_hours
        transition_rate = failure_rate + repair_rate
        steady = repair_rate / transition_rate
        unavailability = failure_rate / transition_rate
        endpoint = steady + (1 - steady) * math.exp(-transition_rate * 100)
        self.assertAlmostEqual(steady, 0.9900990099009901, places=15)
        self.assertAlmostEqual(unavailability, 0.009900990099009901, places=15)
        self.assertAlmostEqual(endpoint, 0.9900994166292596, places=15)
        self.assertAlmostEqual(8760 * unavailability, 86.73267326732673, places=12)
        self.assertAlmostEqual(1 / transition_rate, 9.900990099009901, places=14)

        self.assertEqual(1 / (1 + 0 * repair_hours), 1)
        self.assertEqual(0.1 / (0.1 + 0.1), 0.5)
        tiny_failure_rate = 1e-12
        tiny_transition_rate = tiny_failure_rate + repair_rate
        tiny_steady_unavailability = tiny_failure_rate / tiny_transition_rate
        tiny_unavailability = tiny_steady_unavailability * -math.expm1(
            -tiny_transition_rate * 1e-6
        )
        self.assertGreater(tiny_unavailability, 0)
        self.assertAlmostEqual(tiny_unavailability / 1e-18, 1, places=6)

        extreme_failure_rate = 1e6
        extreme_repair_hours = 1e9
        extreme_repair_rate = 1 / extreme_repair_hours
        extreme_steady = 1 / (1 + extreme_failure_rate * extreme_repair_hours)
        extreme_unavailability = (
            extreme_failure_rate * extreme_repair_hours
            / (1 + extreme_failure_rate * extreme_repair_hours)
        )
        self.assertEqual(math.exp(-(extreme_failure_rate + extreme_repair_rate) * 100), 0)
        self.assertGreater(extreme_steady, 0)
        self.assertAlmostEqual(
            extreme_failure_rate * extreme_steady,
            extreme_repair_rate * extreme_unavailability,
            places=23,
        )

        broken_reliability = math.exp(-failure_rate * 5000)
        correct_availability = steady + (1 - steady) * math.exp(-transition_rate * 5000)
        self.assertAlmostEqual(broken_reliability, 0.006737946999085467, places=15)
        self.assertAlmostEqual(correct_availability, steady, places=15)
        self.assertGreater(correct_availability - broken_reliability, 0.98)

    def test_initial_state_control_has_positive_rate_behavior_regression(self):
        checks = self.text["run_checks.m"]
        for token in (
            "initiallyDown = model(1e-3,10,100,601,0)",
            "An initially down item must start with availability zero",
            "Positive repair flow must move an initially down item upward toward balance",
            "The initial state must not change the rate-derived steady availability",
            "Initially up and down trajectories must approach one balance from opposite sides",
            "Net availability flow must point toward the common steady balance",
        ):
            self.assertIn(token, checks)

        failure_rate = 1e-3
        repair_rate = 1 / 10
        transition_rate = failure_rate + repair_rate
        steady = repair_rate / transition_rate
        endpoint_remainder = math.exp(-transition_rate * 100)
        initially_up_endpoint = steady + (1 - steady) * endpoint_remainder
        initially_down_endpoint = steady - steady * endpoint_remainder
        self.assertGreater(initially_up_endpoint, steady)
        self.assertLess(initially_down_endpoint, steady)
        self.assertLess(initially_up_endpoint - steady, steady - initially_down_endpoint)

    def test_experiment_has_two_independent_sweeps_metrics_and_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertIn("baseline = model(1e-3,10,100,601,1)", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn("failureRateSweepPerHour = [5e-4 1e-3 5e-3]", experiment)
        self.assertIn("changed = model(failureRateSweepPerHour(k),10,100,601,1)", experiment)
        self.assertIn("meanRepairTimeSweepHours = [2 10 40]", experiment)
        self.assertIn("changed = model(1e-3,meanRepairTimeSweepHours(k),100,601,1)", experiment)
        self.assertIn("Baseline metrics:", experiment)
        self.assertIn("downtime = %.2f h/year", experiment)
        self.assertIn("brokenCase = model(1e-3,10,5000,1001,1)", experiment)
        self.assertIn("brokenReliabilityAsAvailability = exp(", experiment)
        self.assertIn("repairable point availability", experiment)
        for label in (
            "Time since observation starts (h)",
            "State probability",
            "Expected transitions per hour",
            "Point availability A(t)",
            "Mean time to repair, MTTR (h)",
            "Steady expected downtime (h/year)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 5)
        self.assertNotIn("subplot(", experiment)

    def test_interactive_controls_have_units_and_immediate_isolated_feedback(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertGreaterEqual(interactive.count("uispinner"), 3)
        self.assertIn("uidropdown", interactive)
        self.assertIn("Failure rate lambda (failures/h)", interactive)
        self.assertIn("Mean time to repair, MTTR (h)", interactive)
        self.assertIn("Observation horizon (h)", interactive)
        self.assertIn("Initial state", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn("{'State occupancy','Transition flow'}", interactive)
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 5)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("A_inf = mu/(lambda+mu)", interactive)
        self.assertIn("Failure and repair flows become equal", interactive)

    def test_checks_cover_invariants_limits_malformed_inputs_and_resource_bound(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 25)
        for token in (
            "Identical inputs must produce identical outputs",
            "state probabilities must be complementary",
            "A_inf must independently equal mu/(lambda+mu)",
            "closed-form two-state transient",
            "transition flows must balance at steady state",
            "larger failure rate must lower steady availability",
            "longer MTTR must lower steady availability",
            "Zero failure rate with an initially up item",
            "Initial-state recovery",
            "Tiny-time unavailability must survive numerical cancellation",
            "fully decayed extreme-domain transient",
            "Extreme-domain failure and repair flows must balance",
            "Extreme-domain recovery must retain a tiny equilibrium unavailability",
            "Equal failure and repair rates must give A_inf=0.5",
            "Equal lambda*MTTR must preserve steady availability",
            "P02 no-repair survival law",
            "recognizable reliability-availability gap",
            "Negative failure rate must be rejected",
            "nonfinite failure rate must be rejected",
            "complex failure rate must be rejected",
            "nonscalar failure rate must be rejected",
            "Zero MTTR must be rejected",
            "nonfinite MTTR must be rejected",
            "zero observation horizon must be rejected",
            "complex observation horizon must be rejected",
            "fractional sample count must be rejected",
            "sample resource bound must be enforced",
            "Initial availability above one must be rejected",
            "nonfinite initial availability must be rejected",
            "maximum supported sample count must remain usable and exact",
            "P03 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertIn("tinyTime = model(1e-12,10,1e-6,3,1)", checks)
        mission_validation = self.text["model.m"].split(
            "validateattributes(missionHours", maxsplit=1
        )[1].split(");", maxsplit=1)[0]
        self.assertIn("{'real','finite','>=',1e-6,'<=',1e9}", mission_validation)
        self.assertGreaterEqual(checks.count("assertRejects("), 12)

    def test_lesson_is_concept_first_with_interpretation_and_teach_back(self):
        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "probability flow",
            "point availability",
            "mean time to repair",
            "no-first-failure",
            "teach back",
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
            for name in ("model.m", "experiment.m", "interactive.m", "lesson.m", "run_checks.m")
        ).lower()
        banned_patterns = {
            "randomness": r"\b(rand|randn|rng)\s*\(",
            "opaque state model": r"\b(ctmc|dtmc|expm)\s*\(",
            "dynamic evaluation": r"\b(eval|evalin|feval)\s*\(",
            "external process": r"\b(system|unix|dos)\s*\(",
            "network": r"\b(webread|webwrite|urlread)\s*\(",
            "file input": r"\b(load|readtable|readmatrix|fopen)\s*\(",
            "asynchronous work": r"\b(timer|parfeval|batch)\s*\(",
            "unbounded loop": r"(?m)^\s*while\b",
            "blocking prompt": r"\b(input|pause|uiwait)\s*\(",
            "global state": r"(?m)^\s*global\b",
            "unrelated figure closure": r"\bclose\s+all\b",
        }
        for name, pattern in banned_patterns.items():
            with self.subTest(boundary=name):
                self.assertIsNone(re.search(pattern, matlab))
        self.assertIn("'integer','>=',2,'<=',10000", self.text["model.m"])
        self.assertIn("'<=',1e9", self.text["model.m"])

    def test_retained_evidence_maps_acceptance_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P03-*.md"))
        self.assertTrue(records, "P03 retained evidence is missing")
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
