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
PROGRESS = (
    ROOT
    / "skills"
    / "doctoral-field-training"
    / "scripts"
    / "manage_progress.py"
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

    def test_builds_first_chapter_and_durable_learning_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "tutorial-site"
            result = self.run_builder(output)

            self.assertEqual(result.returncode, 0, result.stderr)
            for relative_path in (
                "index.html",
                "assets/styles.css",
                "data/tutorial.json",
                "data/learning-state.json",
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
            self.assertIn("Coordination under weaker assumptions", page)
            self.assertIn("planned", page)
            self.assertIn("I finished this chapter", page)
            self.assertNotIn("Cross-period synthesis", page)
            self.assertNotIn("Doctoral capability rubric", page)
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
            self.assertEqual(len(copied_data["chapterPlan"]), 2)
            self.assertEqual(len(copied_data["chapters"]), 1)

            state = json.loads(
                (output / "data/learning-state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["status"], "awaiting-reading")
            self.assertEqual(state["currentChapterId"], "coordination-crisis")
            self.assertEqual(
                [item["status"] for item in state["chapters"]],
                ["available", "planned"],
            )

    def test_acknowledgement_unlocks_exactly_one_next_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            output = temporary / "tutorial-site"
            self.assertEqual(self.run_builder(output).returncode, 0)

            remembered = subprocess.run(
                [
                    sys.executable,
                    str(PROGRESS),
                    "remember",
                    "--output",
                    str(output),
                    "--question",
                    "Which failure assumption is doing the real work?",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(remembered.returncode, 0, remembered.stderr)
            self.assertEqual(
                json.loads(remembered.stdout)["status"], "awaiting-reading"
            )

            progress = subprocess.run(
                [
                    sys.executable,
                    str(PROGRESS),
                    "complete",
                    "--output",
                    str(output),
                    "--acknowledgement",
                    "读完了",
                    "--reflection",
                    "The failure model changed, not merely the implementation.",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(progress.returncode, 0, progress.stderr)
            progress_data = json.loads(progress.stdout)
            self.assertEqual(progress_data["status"], "ready-to-generate")
            self.assertEqual(
                progress_data["currentChapter"]["id"], "weaker-assumptions"
            )

            tutorial = json.loads(FIXTURE.read_text(encoding="utf-8"))
            next_chapter = dict(tutorial["chapters"][0])
            next_chapter.update(
                {
                    "id": "weaker-assumptions",
                    "title": "Coordination under weaker assumptions",
                    "period": "Expansion period",
                }
            )
            tutorial["chapters"].append(next_chapter)
            next_input = temporary / "tutorial-next.json"
            next_input.write_text(
                json.dumps(tutorial, ensure_ascii=False), encoding="utf-8"
            )
            rebuilt = self.run_builder(output, "--force", input_path=next_input)
            self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)

            state = json.loads(
                (output / "data/learning-state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(state["status"], "awaiting-reading")
            self.assertEqual(state["currentChapterId"], "weaker-assumptions")
            self.assertEqual(
                [item["status"] for item in state["chapters"]],
                ["read", "available"],
            )
            acknowledgement = state["memory"]["chapterRecords"][
                "coordination-crisis"
            ]["acknowledgements"][0]
            self.assertEqual(acknowledgement["text"], "读完了")
            unresolved = state["memory"]["chapterRecords"][
                "coordination-crisis"
            ]["unresolvedQuestions"]
            self.assertEqual(
                unresolved[0]["text"],
                "Which failure assumption is doing the real work?",
            )
            page = (output / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("Cross-period synthesis", page)

            final_progress = subprocess.run(
                [
                    sys.executable,
                    str(PROGRESS),
                    "complete",
                    "--output",
                    str(output),
                    "--acknowledgement",
                    "I finished this chapter.",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(final_progress.returncode, 0, final_progress.stderr)
            final_build = self.run_builder(output, "--force", input_path=next_input)
            self.assertEqual(final_build.returncode, 0, final_build.stderr)
            final_page = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("Cross-period synthesis", final_page)
            self.assertIn("Doctoral capability rubric", final_page)

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
