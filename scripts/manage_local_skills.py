#!/usr/bin/env python3
"""Register repository skills for local Codex testing with safe symlinks."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
LOCAL_SKILLS_DIR = ROOT / ".agents" / "skills"


def discover_skills() -> dict[str, Path]:
    return {
        path.parent.name: path.parent
        for path in sorted(SKILLS_DIR.glob("*/SKILL.md"))
    }


def expected_target(source: Path) -> str:
    return os.path.relpath(source, LOCAL_SKILLS_DIR)


def link_is_correct(link: Path, source: Path) -> bool:
    return link.is_symlink() and link.resolve(strict=False) == source.resolve()


def setup() -> int:
    skills = discover_skills()
    LOCAL_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    errors = 0

    for name, source in skills.items():
        link = LOCAL_SKILLS_DIR / name
        if link_is_correct(link, source):
            print(f"ready: {name}")
            continue
        if link.exists() or link.is_symlink():
            print(
                f"error: refusing to replace existing path {link.relative_to(ROOT)}",
                file=sys.stderr,
            )
            errors += 1
            continue
        link.symlink_to(expected_target(source), target_is_directory=True)
        print(f"linked: {name} -> {link.readlink()}")

    if not skills:
        print("warning: no skills found", file=sys.stderr)
    return 1 if errors else 0


def check() -> int:
    skills = discover_skills()
    errors = 0

    for name, source in skills.items():
        link = LOCAL_SKILLS_DIR / name
        if link_is_correct(link, source):
            print(f"ready: {name}")
        else:
            print(
                f"error: {name} is not registered; run 'make setup-local-test'",
                file=sys.stderr,
            )
            errors += 1

    return 1 if errors else 0


def clean() -> int:
    removed = 0
    for name, source in discover_skills().items():
        link = LOCAL_SKILLS_DIR / name
        if link_is_correct(link, source):
            link.unlink()
            removed += 1
            print(f"removed: {name}")
        elif link.exists() or link.is_symlink():
            print(
                f"warning: preserving unmanaged path {link.relative_to(ROOT)}",
                file=sys.stderr,
            )

    print(f"Cleaned {removed} managed skill link(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("setup", "check", "clean"))
    args = parser.parse_args()

    return {"setup": setup, "check": check, "clean": clean}[args.action]()


if __name__ == "__main__":
    raise SystemExit(main())
