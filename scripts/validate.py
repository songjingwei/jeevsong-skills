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

    if errors:
        return 1

    print(f"Validated plugin {name} {version} with {len(skill_files)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
