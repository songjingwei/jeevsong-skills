#!/usr/bin/env python3
"""Inspect or advance a doctoral tutorial's durable learning state."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing canonical file: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def write_json(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_workspace(output: Path) -> tuple[dict[str, object], dict[str, object]]:
    tutorial = read_json(output / "data/tutorial.json")
    state = read_json(output / "data/learning-state.json")
    if state.get("schemaVersion") != "doctoral-field-training/state/v1":
        raise ValueError("unsupported learning-state schemaVersion")
    if tutorial.get("field") != state.get("field"):
        raise ValueError("tutorial and learning state disagree about the field")
    plan = tutorial.get("chapterPlan")
    chapters = state.get("chapters")
    if not isinstance(plan, list) or not isinstance(chapters, list):
        raise ValueError("tutorial plan or learning-state chapters are invalid")
    if [item.get("id") for item in plan] != [item.get("id") for item in chapters]:
        raise ValueError("tutorial plan and learning-state chapter IDs disagree")
    return tutorial, state


def status_summary(tutorial: dict[str, object], state: dict[str, object]) -> dict[str, object]:
    plan = tutorial["chapterPlan"]
    chapters = state["chapters"]
    memory = state.get("memory", {})
    assert isinstance(plan, list)
    assert isinstance(chapters, list)
    titles = {item["id"]: item["title"] for item in plan}
    read = [item["id"] for item in chapters if item.get("status") == "read"]
    current_id = state.get("currentChapterId")
    unresolved: list[dict[str, object]] = []
    if isinstance(memory, dict):
        records = memory.get("chapterRecords", {})
        if isinstance(records, dict):
            for chapter_id, record in records.items():
                if isinstance(record, dict) and record.get("unresolvedQuestions"):
                    unresolved.append(
                        {
                            "chapterId": chapter_id,
                            "questions": record["unresolvedQuestions"],
                        }
                    )
    return {
        "field": state["field"],
        "thesis": tutorial.get("thesis"),
        "status": state["status"],
        "lastReadChapter": (
            {"id": read[-1], "title": titles[read[-1]]} if read else None
        ),
        "currentChapter": (
            {"id": current_id, "title": titles[current_id]}
            if isinstance(current_id, str)
            else None
        ),
        "unresolvedQuestions": unresolved,
    }


def append_memory(record: dict[str, object], key: str, values: list[str]) -> None:
    target = record.setdefault(key, [])
    if not isinstance(target, list):
        raise ValueError(f"memory record {key} must be an array")
    target.extend(
        {"text": value, "source": "learner", "at": utc_now()} for value in values
    )


def complete_current(
    state: dict[str, object],
    acknowledgement: str,
    reflections: list[str],
    questions: list[str],
    misconceptions: list[str],
    mastery_evidence: list[str],
) -> None:
    if state.get("status") != "awaiting-reading":
        raise ValueError("no available chapter is awaiting reading acknowledgement")
    current_id = state.get("currentChapterId")
    if not isinstance(current_id, str):
        raise ValueError("learning state has no current chapter")
    chapters = state["chapters"]
    memory = state["memory"]
    assert isinstance(chapters, list)
    assert isinstance(memory, dict)
    current_index = next(
        (index for index, item in enumerate(chapters) if item["id"] == current_id),
        None,
    )
    if current_index is None or chapters[current_index].get("status") != "available":
        raise ValueError("current chapter is not available")

    now = utc_now()
    chapters[current_index]["status"] = "read"
    chapters[current_index]["readAt"] = now
    records = memory.get("chapterRecords")
    if not isinstance(records, dict) or not isinstance(records.get(current_id), dict):
        raise ValueError("current chapter has no memory record")
    record = records[current_id]
    assert isinstance(record, dict)
    append_memory(record, "acknowledgements", [acknowledgement])
    append_memory(record, "reflections", reflections)
    append_memory(record, "questions", questions)
    append_memory(record, "unresolvedQuestions", questions)
    append_memory(record, "misconceptions", misconceptions)
    append_memory(record, "masteryEvidence", mastery_evidence)

    events = state.setdefault("events", [])
    if not isinstance(events, list):
        raise ValueError("learning-state events must be an array")
    events.append(
        {
            "type": "chapter-read",
            "chapterId": current_id,
            "at": now,
            "acknowledgement": acknowledgement,
        }
    )
    if current_index + 1 < len(chapters):
        next_item = chapters[current_index + 1]
        next_item["status"] = "ready"
        state["currentChapterId"] = next_item["id"]
        state["status"] = "ready-to-generate"
    else:
        state["currentChapterId"] = None
        state["status"] = "complete"
    state["updatedAt"] = now


def remember(
    state: dict[str, object],
    chapter_id: str | None,
    reflections: list[str],
    questions: list[str],
    misconceptions: list[str],
    mastery_evidence: list[str],
) -> None:
    target_id = chapter_id or state.get("currentChapterId")
    if not isinstance(target_id, str):
        raise ValueError("no chapter was supplied and the workspace has no current chapter")
    memory = state.get("memory")
    if not isinstance(memory, dict):
        raise ValueError("learning state has no memory object")
    records = memory.get("chapterRecords")
    if not isinstance(records, dict) or not isinstance(records.get(target_id), dict):
        raise ValueError(f"unknown chapter memory record: {target_id}")
    record = records[target_id]
    assert isinstance(record, dict)
    append_memory(record, "reflections", reflections)
    append_memory(record, "questions", questions)
    append_memory(record, "unresolvedQuestions", questions)
    append_memory(record, "misconceptions", misconceptions)
    append_memory(record, "masteryEvidence", mastery_evidence)
    now = utc_now()
    events = state.setdefault("events", [])
    if not isinstance(events, list):
        raise ValueError("learning-state events must be an array")
    events.append(
        {
            "type": "memory-recorded",
            "chapterId": target_id,
            "at": now,
            "counts": {
                "reflections": len(reflections),
                "questions": len(questions),
                "misconceptions": len(misconceptions),
                "masteryEvidence": len(mastery_evidence),
            },
        }
    )
    state["updatedAt"] = now


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--output", required=True, type=Path)
    remember_parser = subparsers.add_parser("remember")
    remember_parser.add_argument("--output", required=True, type=Path)
    remember_parser.add_argument("--chapter")
    remember_parser.add_argument("--reflection", action="append", default=[])
    remember_parser.add_argument("--question", action="append", default=[])
    remember_parser.add_argument("--misconception", action="append", default=[])
    remember_parser.add_argument("--mastery-evidence", action="append", default=[])
    complete_parser = subparsers.add_parser("complete")
    complete_parser.add_argument("--output", required=True, type=Path)
    complete_parser.add_argument("--acknowledgement", required=True)
    complete_parser.add_argument("--reflection", action="append", default=[])
    complete_parser.add_argument("--question", action="append", default=[])
    complete_parser.add_argument("--misconception", action="append", default=[])
    complete_parser.add_argument("--mastery-evidence", action="append", default=[])
    args = parser.parse_args()
    output = args.output.resolve()
    try:
        tutorial, state = load_workspace(output)
        if args.command == "complete":
            complete_current(
                state,
                args.acknowledgement,
                args.reflection,
                args.question,
                args.misconception,
                args.mastery_evidence,
            )
            write_json(output / "data/learning-state.json", state)
        elif args.command == "remember":
            if not any(
                (
                    args.reflection,
                    args.question,
                    args.misconception,
                    args.mastery_evidence,
                )
            ):
                raise ValueError("remember requires at least one memory value")
            remember(
                state,
                args.chapter,
                args.reflection,
                args.question,
                args.misconception,
                args.mastery_evidence,
            )
            write_json(output / "data/learning-state.json", state)
        print(json.dumps(status_summary(tutorial, state), ensure_ascii=False, indent=2))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
