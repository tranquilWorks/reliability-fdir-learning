from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "modules/04-expose-common-cause-failure"
QUESTION = (
    "What inputs, observable effects, and failure modes matter when you expose "
    "Common-Cause Failure?"
)


class P04ModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "curriculum/modules.json").read_text(encoding="utf-8"))
        cls.module = next(module for module in cls.manifest["modules"] if module["id"] == "P04")
        cls.text = {
            path.name: path.read_text(encoding="utf-8")
            for path in FOLDER.iterdir()
            if path.is_file()
        }

    def test_p04_identity_and_complete_artifact_set_are_permanent(self):
        self.assertEqual(self.module["number"], 4)
        self.assertEqual(self.module["title"], "Expose Common-Cause Failure")
        self.assertEqual(self.module["guiding_question"], QUESTION)
        self.assertEqual(self.module["phase"], 1)
        self.assertEqual(self.module["phase_title"], "Reliability fundamentals")
        self.assertEqual(self.module["slug"], "expose-common-cause-failure")
        self.assertEqual(
            self.module["folder"], "modules/04-expose-common-cause-failure"
        )
        self.assertEqual(self.module["prerequisites"], ["P03"])
        self.assertEqual(self.module["implementation_batch"], "P04")
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

    def test_guiding_question_and_p03_connection_are_visible(self):
        for name in ("README.md", "lesson.md", "walkthrough.md", "lesson.m", "experiment.m"):
            with self.subTest(name=name):
                normalized = " ".join(self.text[name].replace("%", " ").split())
                self.assertIn(QUESTION, normalized)
        for name in ("README.md", "lesson.md", "walkthrough.md", "checks.md", "lesson.m"):
            with self.subTest(name=name):
                self.assertIn("P03", self.text[name])

    def test_model_exposes_transparent_beta_factor_equations(self):
        model = self.text["model.m"]
        for token in (
            "commonCauseRatePerHour = commonCauseFraction*channelFailureRatePerHour",
            "(1-commonCauseFraction)*channelFailureRatePerHour",
            "commonCauseEventProbability = -expm1(-commonCauseExposure)",
            "independentChannelFailureProbability =",
            "-expm1(-independentExposure)",
            "parallelFailureAndLogSurvival(independentExposure,channelCount)",
            "independentExhaustionProbability = noCommonCauseProbability.*",
            "systemFailureProbability = commonCauseEventProbability +",
            "systemReliability = exp(-commonCauseExposure+",
            "parallelFailureAndLogSurvival(marginalChannelExposure,channelCount)",
            "logAllFailed(useFailureForm) = channelCount*",
            "log(-expm1(-exposure(useFailureForm)))",
            "log1p(-exp(-exposure(useSurvivalForm)))",
            "atLeastOneSurvivalProbability = -expm1(logAllFailed)",
            "logAtLeastOneSurvival(largeExposure) =",
        ):
            self.assertIn(token, model)
        for output in (
            "systemReliability",
            "systemFailureProbability",
            "commonCauseEventProbability",
            "independentExhaustionProbability",
            "marginalChannelSurvivalProbability",
            "assumedIndependentSystemFailureProbability",
            "endpointSystemReliability",
            "endpointSystemFailureProbability",
        ):
            self.assertIn(f"'{output}'", model)
        for presentation_call in ("figure(", "plot(", "semilogy(", "uifigure", "uiaxes"):
            self.assertNotIn(presentation_call, model.lower())

    def test_reference_values_limits_and_broken_case_are_independently_known(self):
        rate = 1e-4
        beta = 0.05
        channels = 2
        mission = 1000
        common_rate = beta * rate
        independent_rate = (1 - beta) * rate
        no_common = math.exp(-common_rate * mission)
        common_failure = -math.expm1(-common_rate * mission)
        independent_channel_failure = -math.expm1(-independent_rate * mission)
        independent_exhaustion = no_common * independent_channel_failure**channels
        system_failure = common_failure + independent_exhaustion
        system_reliability = no_common * (1 - independent_channel_failure**channels)
        assumed_failure = (-math.expm1(-rate * mission)) ** channels

        self.assertAlmostEqual(common_rate, 5e-6, places=20)
        self.assertAlmostEqual(independent_rate, 9.5e-5, places=20)
        self.assertAlmostEqual(system_reliability, 0.9868401780159008, places=15)
        self.assertAlmostEqual(system_failure, 0.013159821984099238, places=15)
        self.assertAlmostEqual(common_failure, 0.004987520807317687, places=15)
        self.assertAlmostEqual(independent_exhaustion, 0.008172301176781551, places=15)
        self.assertAlmostEqual(assumed_failure, 0.009055917006062713, places=15)
        self.assertAlmostEqual(system_reliability + system_failure, 1, places=15)

        self.assertEqual(math.exp(-0 * mission), 1)
        self.assertAlmostEqual(
            math.exp(-rate * mission),
            math.exp(-rate * mission) * (1 - 0**6),
            places=15,
        )
        self.assertGreater(-math.expm1(-2e-19), 0)

        high_exposure_one = math.exp(-40)
        high_exposure_parallel = -math.expm1(
            128 * math.log1p(-high_exposure_one)
        )
        high_exposure_failure = math.exp(
            128 * math.log1p(-high_exposure_one)
        )
        self.assertEqual(-math.expm1(-40), 1)
        self.assertGreater(high_exposure_one, 0)
        self.assertAlmostEqual(
            high_exposure_parallel, 5.437893446773233e-16, places=30
        )
        self.assertAlmostEqual(
            high_exposure_failure, 0.9999999999999994, places=15
        )
        self.assertEqual(high_exposure_failure + high_exposure_parallel, 1)
        self.assertGreater(math.exp(math.log(128) - 746), 0)

        broken_channels = 6
        broken_failure = common_failure + no_common * (
            independent_channel_failure**broken_channels
        )
        broken_assumed = (-math.expm1(-rate * mission)) ** broken_channels
        optimism_factor = broken_failure / broken_assumed
        self.assertAlmostEqual(broken_failure, 0.004988072092139172, places=15)
        self.assertAlmostEqual(broken_assumed, 7.426724285218982e-7, places=20)
        self.assertGreater(optimism_factor, 6000)

    def test_channel_count_changes_only_independent_exhaustion_reference_behavior(self):
        rate = 1e-4
        beta = 0.05
        mission = 1000
        channel_counts = (1, 2, 3, 4, 6)
        no_common = math.exp(-(beta * rate) * mission)
        independent_channel_failure = -math.expm1(
            -((1 - beta) * rate) * mission
        )

        shared_terms = []
        independent_terms = []
        total_terms = []
        for channel_count in channel_counts:
            shared = -math.expm1(-(beta * rate) * mission)
            independent = (
                no_common * independent_channel_failure**channel_count
            )
            shared_terms.append(shared)
            independent_terms.append(independent)
            total_terms.append(shared + independent)

        self.assertEqual(len(set(shared_terms)), 1)
        self.assertTrue(
            all(
                earlier > later
                for earlier, later in zip(
                    independent_terms, independent_terms[1:]
                )
            )
        )
        self.assertTrue(
            all(
                earlier > later
                for earlier, later in zip(total_terms, total_terms[1:])
            )
        )
        for shared, independent, total in zip(
            shared_terms, independent_terms, total_terms
        ):
            self.assertAlmostEqual(total - shared, independent, places=18)

    def test_experiment_has_two_independent_sweeps_metrics_and_broken_case(self):
        experiment = self.text["experiment.m"]
        self.assertIn("baseline = model(1e-4,0.05,2,1000,601)", experiment)
        self.assertGreaterEqual(experiment.lower().count("%% sweep"), 2)
        self.assertIn("commonCauseFractionSweep = [0 0.01 0.05 0.2]", experiment)
        self.assertIn(
            "changed = model(1e-4,commonCauseFractionSweep(k),2,1000,601)",
            experiment,
        )
        self.assertIn("channelCountSweep = [1 2 3 4 6]", experiment)
        self.assertIn(
            "changed = model(1e-4,0.05,channelCountSweep(k),1000,601)",
            experiment,
        )
        self.assertIn("Baseline metrics:", experiment)
        self.assertIn("Q_common(T)", experiment)
        self.assertIn("Q_independent(T)", experiment)
        self.assertIn("brokenCase = model(1e-4,0.05,6,1000,601)", experiment)
        self.assertIn("optimism factor", experiment)
        for label in (
            "Mission time (h)",
            "Reliability probability",
            "System failure probability",
            "Channels in one-out-of-n redundant group",
            "Mission failure probability Q(T)",
        ):
            self.assertIn(label, experiment)
        self.assertGreaterEqual(experiment.count("figure("), 5)
        self.assertNotIn("subplot(", experiment)

    def test_interactive_controls_have_units_and_immediate_isolated_feedback(self):
        interactive = self.text["interactive.m"]
        self.assertIn("uifigure", interactive)
        self.assertGreaterEqual(interactive.count("uispinner"), 4)
        self.assertIn("Channel hazard lambda (failures/h)", interactive)
        self.assertIn("Common-cause fraction beta (dimensionless)", interactive)
        self.assertIn("Channels in one-out-of-n group", interactive)
        self.assertIn("Mission duration (h)", interactive)
        self.assertIn("Visible view (one at a time)", interactive)
        self.assertIn(
            "{'Reliability comparison','Failure-mode decomposition'}", interactive
        )
        self.assertEqual(interactive.count("uiaxes("), 1)
        self.assertGreaterEqual(interactive.count("ValueChangedFcn"), 5)
        self.assertIn("channelControl.Value = channels", interactive)
        self.assertIn("modelForThisModule = @model", interactive)
        self.assertIn("out = modelForThisModule(", interactive)
        self.assertNotIn("out = model(", interactive)
        self.assertIn("lambda_c = beta*lambda", interactive)
        self.assertIn("it is not a correlation coefficient", interactive)

    def test_checks_cover_invariants_limits_malformed_recovery_and_resources(self):
        checks = self.text["run_checks.m"]
        self.assertGreaterEqual(checks.count("assert("), 35)
        for token in (
            "Identical inputs must produce identical outputs",
            "Reliability and failure probability must be complementary",
            "must decompose system failure",
            "shared hazard must independently equal beta times lambda",
            "independent hazard must independently equal (1-beta) times lambda",
            "same marginal channel hazard",
            "Beta zero must recover ordinary independent redundancy",
            "larger common-cause fraction must lower redundant-system reliability",
            "preserve the stated marginal channel reliability",
            "Adding channels must reduce one-out-of-n failure probability",
            "Changing channel count must not change the shared-event contribution",
            "Adding channels must reduce the independent-exhaustion term",
            "cannot reduce failure probability below the shared-event contribution",
            "Beta one must make the shared shock equal the full marginal hazard",
            "extra channels must provide no benefit",
            "Zero hazard must give certain mission success",
            "Tiny shared-event probability must survive numerical cancellation",
            "Equal lambda*T exposure",
            "one-channel survival must not be lost to subtraction",
            "parallel survival must not be lost to subtraction",
            "parallel failure must retain its representable complement",
            "consistent probability pair",
            "retain group survival after channel survival underflows",
            "Subnormal group survival must match",
            "fully decayed finite-domain mission",
            "recognizable optimism factor",
            "Negative channel failure rate must be rejected",
            "nonfinite channel failure rate must be rejected",
            "complex channel failure rate must be rejected",
            "nonscalar channel failure rate must be rejected",
            "negative common-cause fraction must be rejected",
            "common-cause fraction above one must be rejected",
            "fractional channel count must be rejected",
            "channel-count resource bound must be enforced",
            "zero mission duration must be rejected",
            "fractional sample count must be rejected",
            "sample resource bound must be enforced",
            "Maximum supported channel and sample counts",
            "must not contaminate a later valid calculation",
            "P04 checks passed",
        ):
            self.assertIn(token, checks)
        self.assertGreaterEqual(checks.count("assertRejects("), 18)

    def test_lesson_is_concept_first_with_interpretation_and_teach_back(self):
        combined = "\n".join(
            self.text[name]
            for name in ("lesson.md", "walkthrough.md", "checks.md", "lesson.m")
        ).lower()
        for concept in (
            "marginal hazard",
            "shared event",
            "independent-exhaustion",
            "mission reliability",
            "correlation coefficient",
            "teach back",
        ):
            self.assertIn(concept, combined)
        self.assertIn("answer one at a time", combined)
        self.assertIn("p03", combined)
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
            "opaque reliability toolbox": (
                r"\b(ctmc|dtmc|expm|wblcdf|wblpdf|fitdist|makedist)\s*\("
            ),
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
        self.assertIn("'integer','>=',1,'<=',128", self.text["model.m"])
        self.assertIn("'integer','>=',2,'<=',10000", self.text["model.m"])
        self.assertIn("'<=',1e9", self.text["model.m"])

    def test_retained_evidence_maps_acceptance_and_claim_boundaries(self):
        records = sorted((ROOT / "docs/evidence").glob("P04-*.md"))
        self.assertTrue(records, "P04 retained evidence is missing")
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
