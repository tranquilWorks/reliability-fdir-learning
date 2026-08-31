from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LearnCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "curriculum/modules.json").read_text(encoding="utf-8"))

    def make_fixture(self, temporary: str) -> tuple[Path, dict[str, str]]:
        fixture = Path(temporary) / "repo"
        shutil.copytree(ROOT / "bin", fixture / "bin")
        shutil.copytree(ROOT / "curriculum", fixture / "curriculum")
        for module in self.manifest["modules"]:
            source = ROOT / module["folder"]
            target = fixture / module["folder"]
            target.mkdir(parents=True, exist_ok=True)
            for name in ("README.md", "lesson.md", "walkthrough.md", "checks.md", "run_checks.m"):
                if (source / name).exists():
                    shutil.copy2(source / name, target / name)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return fixture, environment

    def invoke(
        self, fixture: Path, environment: dict[str, str], *args: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(fixture / "bin/learn"), *args],
            cwd=fixture,
            text=True,
            capture_output=True,
            env=environment,
            timeout=10,
        )

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            fixture, environment = self.make_fixture(temporary)
            return self.invoke(fixture, environment, *args)

    def test_status_and_list(self):
        status = self.run_cli("status")
        self.assertEqual(status.returncode, 0, status.stderr)
        implemented = sum(
            module["status"] == "implemented" for module in self.manifest["modules"]
        )
        self.assertIn(f"24 total, {implemented} implemented", status.stdout)
        listing = self.run_cli("list")
        self.assertEqual(listing.returncode, 0, listing.stderr)
        self.assertEqual(len([line for line in listing.stdout.splitlines() if line.strip()]), 24)

    def test_all_implemented_modules_start_while_a_scaffold_refuses(self):
        for module in self.manifest["modules"]:
            if module["status"] != "implemented":
                continue
            with self.subTest(implemented=module["id"]):
                started = self.run_cli("start", module["id"])
                self.assertEqual(started.returncode, 0, started.stderr)
                self.assertIn(f"{module['id']} — {module['title']}", started.stdout)
                self.assertIn(
                    f"Guiding question: {module['guiding_question']}",
                    started.stdout,
                )

        scaffold_module = next(
            (module for module in self.manifest["modules"] if module["status"] == "scaffolded"),
            None,
        )
        if scaffold_module is None:
            self.skipTest("The canonical curriculum no longer has a scaffolded module.")
        scaffold = self.run_cli("start", scaffold_module["id"])
        self.assertEqual(scaffold.returncode, 2)
        self.assertIn("Activate its governed implementation batch", scaffold.stdout)

    def test_all_implemented_executable_checks_are_discoverable(self):
        for module in self.manifest["modules"]:
            if module["status"] != "implemented":
                continue
            with self.subTest(implemented=module["id"]):
                check = self.run_cli("check", module["id"])
                self.assertEqual(check.returncode, 0, check.stderr)
                self.assertIn(f"run_module_checks('{module['id']}')", check.stdout)

    def test_rejected_scaffold_does_not_replace_current_module(self):
        scaffold_module = next(
            (module for module in self.manifest["modules"] if module["status"] == "scaffolded"),
            None,
        )
        if scaffold_module is None:
            self.skipTest("The canonical curriculum no longer has a scaffolded module.")

        with tempfile.TemporaryDirectory() as temporary:
            fixture, environment = self.make_fixture(temporary)
            implemented_module = next(
                module
                for module in reversed(self.manifest["modules"])
                if module["status"] == "implemented"
            )
            selected = self.invoke(fixture, environment, "start", implemented_module["id"])
            self.assertEqual(selected.returncode, 0, selected.stderr)
            rejected = self.invoke(fixture, environment, "start", scaffold_module["id"])
            self.assertEqual(rejected.returncode, 2)
            resumed = self.invoke(fixture, environment, "continue")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertIn(
                f"{implemented_module['id']} — {implemented_module['title']}",
                resumed.stdout,
            )

    def test_rejected_scaffold_does_not_create_fresh_progress_state(self):
        scaffold_module = next(
            (module for module in self.manifest["modules"] if module["status"] == "scaffolded"),
            None,
        )
        if scaffold_module is None:
            self.skipTest("The canonical curriculum no longer has a scaffolded module.")

        with tempfile.TemporaryDirectory() as temporary:
            fixture, environment = self.make_fixture(temporary)
            state_dir = fixture / ".learning"
            self.assertFalse(state_dir.exists())
            rejected = self.invoke(fixture, environment, "start", scaffold_module["id"])
            self.assertEqual(rejected.returncode, 2)
            self.assertIn("Activate its governed implementation batch", rejected.stdout)
            self.assertFalse(state_dir.exists())

    def test_unknown_module_is_rejected_without_touching_repository_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture, environment = self.make_fixture(temporary)
            state_dir = fixture / ".learning"
            self.assertFalse(state_dir.exists())
            unknown = self.invoke(fixture, environment, "start", "P99")
            self.assertNotEqual(unknown.returncode, 0)
            self.assertIn("Unknown module: P99", unknown.stderr)
            self.assertFalse(state_dir.exists())


if __name__ == "__main__":
    unittest.main()
