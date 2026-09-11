from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT
    / "skills"
    / "doctoral-field-training"
    / "scripts"
    / "build_tutorial.py"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "doctoral-field-training"
    / "tutorial.json"
)


class BuildTutorialTest(unittest.TestCase):
    def run_builder(
        self,
        output: Path,
        *extra: str,
        input_path: Path = FIXTURE,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(BUILDER),
                "--input",
                str(input_path),
                "--output",
                str(output),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_builds_complete_offline_site(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "tutorial-site"
            result = self.run_builder(output)

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative_path in (
                "index.html",
                "assets/styles.css",
                "data/tutorial.json",
            ):
                self.assertTrue((output / relative_path).is_file(), relative_path)

            self.assertFalse((output / "assets/app.js").exists())

            page = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("A Problem History of Distributed Coordination", page)
            self.assertIn("Field admission", page)
            self.assertIn("Become a backend engineer", page)
            self.assertIn("Distributed Systems", page)
            self.assertIn("Chosen By User", page)
            self.assertIn("SOSP and OSDI", page)
            self.assertIn("From primary artifacts to the frontier", page)
            self.assertIn("Primary-artifact investigation", page)
            self.assertIn("Trace the agreement threshold", page)
            self.assertIn('id="coordination-crisis"', page)
            self.assertIn("Cross-period synthesis", page)
            self.assertIn("Doctoral capability rubric", page)
            self.assertIn("Foundational Coordination &lt;Study&gt;", page)
            self.assertNotIn("Foundational Coordination <Study>", page)
            self.assertNotIn("data-progress", page)
            self.assertNotIn("Mark complete", page)

            copied_data = json.loads(
                (output / "data/tutorial.json").read_text(encoding="utf-8")
            )
            self.assertEqual(copied_data["field"], "Distributed Systems")
            self.assertEqual(
                copied_data["fieldQualification"]["decision"], "reframed"
            )
            self.assertEqual(
                copied_data["fieldQualification"]["selectionMethod"],
                "chosen-by-user",
            )

    def test_refuses_to_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "tutorial-site"
            self.assertEqual(self.run_builder(output).returncode, 0)

            second_result = self.run_builder(output)
            self.assertNotEqual(second_result.returncode, 0)
            self.assertIn("--force", second_result.stderr)

            forced_result = self.run_builder(output, "--force")
            self.assertEqual(forced_result.returncode, 0, forced_result.stderr)

    def test_refuses_agent_selected_reframed_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            data = json.loads(FIXTURE.read_text(encoding="utf-8"))
            data["fieldQualification"]["selectionMethod"] = "accepted-as-stated"
            invalid_input = temporary / "invalid-selection.json"
            invalid_input.write_text(
                json.dumps(data, ensure_ascii=False),
                encoding="utf-8",
            )

            result = self.run_builder(
                temporary / "tutorial-site",
                input_path=invalid_input,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("chosen-by-user", result.stderr)


if __name__ == "__main__":
    unittest.main()
