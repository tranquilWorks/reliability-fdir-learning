from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/02-relate-hazard-rate-to-survival"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you relate "
    "Hazard Rate to Survival?"
)


class P02ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "curriculum/modules.json").read_text(encoding="utf-8"))
        cls.module = next(module for module in cls.manifest["modules"] if module["id"] == "P02")
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p02_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 2)
        self.assertEqual(self.module["title"], "Relate Hazard Rate to Survival")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 1)
        self.assertEqual(self.module["phase_title"], "Reliability fundamentals")
        self.assertEqual(self.module["slug"], "relate-hazard-rate-to-survival")
        self.assertEqual(
            self.module["folder"], "modules/02-relate-hazard-rate-to-survival"
        )
        self.assertEqual(self.module["prerequisites"], ["P01"])
        self.assertEqual(self.module["implementation_batch"], "P02")
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

    def test_guiding_question_and_prerequisite_connection_are_visible(self):
        for name in ("README.md", "lesson.md", "walkthrough.md", "lesson.m", "experiment.m"):
            with self.subTest(name=name):
                normalized = " ".join(self.text[name].replace("%", " ").split())
                self.assertIn(QUESTION, normalized)
        for name in ("README.md", "lesson.md", "walkthrough.md", "run_checks.m"):
            with self.subTest(name=name):
                self.assertIn("P01", self.text[name])

    def test_model_exposes_the_transparent_hazard_survival_equations(self):
        model = self.text["model.m"]
        for token in (
            "hoursAtBaseHazard = min(timeHours,changeTimeHours)",
            "hoursAfterChange = max(timeHours-changeTimeHours,0)",
            "cumulativeHazard = baseHazardPerHour*hoursAtBaseHazard",
            "survivalProbability = exp(-cumulativeHazard)",
            "failureProbability = -expm1(-cumulativeHazard)",
        ):
            self.assertIn(token, model)
        for output in (
            "hazardPerHour",
            "cumulativeHazard",
            "missionSurvival",
            "expectedSurvivorsPerThousand",
        ):
            self.assertIn(f"'{output}'", model)
        for presentation_call in ("figure(", "plot(", "stairs(", "uifigure", "uilabel"):
            self.assertNotIn(presentation_call, model.lower())

    def test_reference_values_and_limiting_cases_are_independently_known(self):
        experiment = self.text["experiment.m"]
        self.assertIn("baseline = model(2e-4,1,1000,3000,601)", experiment)
        self.assertIn("brokenCase = model(1e-3,3,500,2000,601)", experiment)
        baseline_h = 2e-4 * 3000
        changed_h = 2e-4 * 1000 + 2e-4 * 4 * 2000
        broken_h = 1e-3 * 500 + 1e-3 * 3 * 1500
        self.assertAlmostEqual(baseline_h, 0.6, places=15)
        self.assertAlmostEqual(math.exp(-baseline_h), 0.5488116360940264, places=15)
        self.assertAlmostEqual(changed_h, 1.8, places=15)
        self.assertAlmostEqual(math.exp(-changed_h), 0.16529888822158653, places=15)
        self.assertAlmostEqual(broken_h, 5.0, places=15)
        self.assertAlmostEqual(math.exp(-broken_h), 0.006737946999085467, places=15)
        self.assertEqual(1 - broken_h, -4.0)
        self.assertEqual(math.exp(0), 1.0)
        self.assertGreater(-math.expm1(-1e-20), 0)

    def test_experiment_has_two_independent_sweeps_metrics_and_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn("baseHazardSweepPerHour = [1e-4 2e-4 5e-4]", experiment)
        self.assertIn("postChangeMultiplierSweep = [0.25 1 4]", experiment)
        self.assertIn("Baseline metrics:", experiment)
        self.assertIn("expected survivors", experiment)
        self.assertIn("linearSurvival = 1-brokenCase.cumulativeHazard", experiment)
        self.assertIn("linearSurvival < 0", experiment)
        for label in (
            "Mission time (h)",
            "Hazard rate (failures/h)",
            "Survival probability S(t)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 4)

    def test_interactive_controls_have_units_and_immediate_bounded_feedback(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertGreaterEqual(interactive.count("uispinner"), 4)
        self.assertIn("Baseline hazard rate (failures/h)", interactive)
        self.assertIn("Post-change multiplier (dimensionless)", interactive)
        self.assertIn("Condition-change time (h)", interactive)
        self.assertIn("Mission duration (h)", interactive)
        self.assertIn("ValueChangedFcn", interactive)
        self.assertIn("changeControl.Value = missionControl.Value", interactive)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("H(T) = integral lambda(t)dt", interactive)

    def test_checks_cover_invariants_limits_malformed_inputs_and_resource_bound(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 18)
        for token in (
            "Identical inputs must produce identical outputs",
            "-log(S)=H",
            "P01 exponential reliability law",
            "survival identical through the change time",
            "change at time zero",
            "change at mission end",
            "Zero hazard is the limiting case",
            "Survival must plateau",
            "hazard change must appear exactly on the sampled time grid",
            "without cancellation",
            "negative-probability symptom",
            "Negative hazard must be rejected",
            "Negative multiplier must be rejected",
            "condition change after mission end must be rejected",
            "nonfinite hazard must be rejected",
            "complex hazard must be rejected",
            "nonscalar hazard must be rejected",
            "fractional sample count must be rejected",
            "sample resource bound must be enforced",
            "sample count must remain usable and exact",
            "P02 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertGreaterEqual(checks.count("assertRejects("), 8)

    def test_lesson_is_concept_first_and_has_interpretation_and_teach_back(self):
        combined = "\n".join(
            self.text[name] for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "conditional failure rate",
            "cumulative hazard",
            "small-exposure",
            "teach back",
        ):
            self.assertIn(concept, combined)
        self.assertIn("answer one at a time", combined)
        self.assertNotIn("planned concept loop", combined)
        self.assertNotIn("this is the governed p02 scaffold", combined)
        self.assertNotIn("p02 is scaffolded", combined)

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
            "opaque survival toolbox": (
                r"\b(wblcdf|wblpdf|wblfit|fitdist|makedist|ecdf|ksdensity)\s*\("
            ),
            "dynamic evaluation": r"\b(eval|evalin|feval)\s*\(",
            "external process": r"\b(system|unix|dos)\s*\(",
            "network": r"\b(webread|webwrite|urlread)\s*\(",
            "file input": r"\b(load|readtable|readmatrix|fopen)\s*\(",
            "asynchronous timer": r"\b(timer|parfeval|batch)\s*\(",
            "unbounded loop": r"(?m)^\s*while\b",
            "blocking prompt": r"\b(input|pause|uiwait)\s*\(",
        }
        for name, pattern in banned_patterns.items():
            with self.subTest(boundary=name):
                self.assertIsNone(re.search(pattern, matlab))
        self.assertIn("'integer','>=',2,'<=',10000", self.text["model.m"])

    def test_retained_evidence_maps_acceptance_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P02-*.md"))
        self.assertTrue(records, "P02 retained evidence is missing")
        evidence = records[-1].read_text(encoding="utf-8")
        for marker in (
            "## Acceptance map",
            "## Exact validation commands and results",
            "## Changed and preserved invariants",
            "## Rollback",
            "## Residual risks",
            "## Unperformed validation",
            "MATLAB execution",
            "UI behavior",
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
