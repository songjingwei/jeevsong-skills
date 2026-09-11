#!/usr/bin/env python3
"""Validate plugin manifests and bundled skill metadata."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)


def load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing {path.relative_to(ROOT)}")
    except json.JSONDecodeError as error:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {error}")
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{path.relative_to(ROOT)} must start with YAML frontmatter")
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("'\"")

    fail(f"{path.relative_to(ROOT)} has unclosed YAML frontmatter")
    return {}


def main() -> int:
    errors_before = 0
    portable = load_json(ROOT / "plugin.json")
    codex = load_json(ROOT / ".codex-plugin" / "plugin.json")

    for field in ("name", "version", "description"):
        if not portable.get(field):
            fail(f"plugin.json is missing {field}")
            errors_before += 1
        if portable.get(field) != codex.get(field):
            fail(f"manifest field {field!r} does not match")
            errors_before += 1

    name = portable.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        fail("plugin name must use lowercase kebab-case")
        errors_before += 1

    version = portable.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        fail("plugin version must use x.y.z semantic versioning")
        errors_before += 1

    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    seen_names: set[str] = set()
    errors = errors_before

    for skill_file in skill_files:
        metadata = parse_frontmatter(skill_file)
        skill_name = metadata.get("name", "")
        description = metadata.get("description", "")

        if not NAME_PATTERN.fullmatch(skill_name):
            fail(f"{skill_file.relative_to(ROOT)} has an invalid name")
            errors += 1
        if skill_name != skill_file.parent.name:
            fail(f"{skill_file.relative_to(ROOT)} name must match its folder")
            errors += 1
        if skill_name in seen_names:
            fail(f"duplicate skill name: {skill_name}")
            errors += 1
        if not description:
            fail(f"{skill_file.relative_to(ROOT)} is missing description")
            errors += 1
        seen_names.add(skill_name)

    test_case_count = 0
    seen_case_ids: set[str] = set()
    tested_skills: set[str] = set()
    allowed_invocations = {"explicit", "implicit", "negative"}

    for suite_path in sorted((ROOT / "tests" / "cases").glob("*.json")):
        suite = load_json(suite_path)
        suite_skill = suite.get("skill")
        cases = suite.get("cases")

        if suite_skill not in seen_names:
            fail(
                f"{suite_path.relative_to(ROOT)} references unknown skill "
                f"{suite_skill!r}"
            )
            errors += 1
        elif suite_skill in tested_skills:
            fail(f"multiple test suites found for skill {suite_skill!r}")
            errors += 1
        else:
            tested_skills.add(suite_skill)
        if not isinstance(cases, list) or not cases:
            fail(f"{suite_path.relative_to(ROOT)} must contain a non-empty cases list")
            errors += 1
            continue

        for case in cases:
            test_case_count += 1
            if not isinstance(case, dict):
                fail(f"{suite_path.relative_to(ROOT)} contains a non-object case")
                errors += 1
                continue

            case_id = case.get("id")
            invocation = case.get("invocation")
            prompt = case.get("prompt")
            expected = case.get("expected_behaviors")
            forbidden = case.get("forbidden_behaviors", [])
            should_activate = case.get("should_activate")

            if not isinstance(case_id, str) or not case_id:
                fail(f"{suite_path.relative_to(ROOT)} contains a case without an id")
                errors += 1
            elif case_id in seen_case_ids:
                fail(f"duplicate test case id: {case_id}")
                errors += 1
            else:
                seen_case_ids.add(case_id)

            if invocation not in allowed_invocations:
                fail(f"test case {case_id!r} has an invalid invocation")
                errors += 1
            if not isinstance(should_activate, bool):
                fail(f"test case {case_id!r} must define should_activate as boolean")
                errors += 1
            elif invocation in allowed_invocations and should_activate != (
                invocation != "negative"
            ):
                fail(f"test case {case_id!r} has inconsistent activation metadata")
                errors += 1
            if not isinstance(prompt, str) or not prompt.strip():
                fail(f"test case {case_id!r} must contain a prompt")
                errors += 1
            elif isinstance(suite_skill, str):
                mention = f"${suite_skill}"
                if invocation == "explicit" and mention not in prompt:
                    fail(f"explicit test case {case_id!r} must mention {mention}")
                    errors += 1
                elif invocation != "explicit" and mention in prompt:
                    fail(f"non-explicit test case {case_id!r} cannot mention {mention}")
                    errors += 1
            if not isinstance(expected, list) or not expected or not all(
                isinstance(item, str) and item.strip() for item in expected
            ):
                fail(f"test case {case_id!r} must contain expected behaviors")
                errors += 1
            if not isinstance(forbidden, list) or not all(
                isinstance(item, str) and item.strip() for item in forbidden
            ):
                fail(f"test case {case_id!r} has invalid forbidden behaviors")
                errors += 1

    for untested_skill in sorted(seen_names - tested_skills):
        fail(f"skill {untested_skill!r} has no test suite under tests/cases")
        errors += 1

    if errors:
        return 1

    print(
        f"Validated plugin {name} {version} with {len(skill_files)} skill(s) "
        f"and {test_case_count} test case(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
