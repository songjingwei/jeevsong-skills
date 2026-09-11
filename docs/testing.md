# Local skill testing

This repository tests skills at four layers: structure, discovery, routing, and behavior. Structural checks are automated. Routing and behavior checks use representative prompts because exact model wording is intentionally not treated as a stable test contract.

## 1. Validate repository structure

Run:

```bash
make validate
```

This checks both plugin manifests, every `SKILL.md`, and every JSON test suite under `tests/cases/`.

## 2. Register skills for local Codex discovery

Run:

```bash
make setup-local-test
make check-local-test
```

The setup command creates repository-local symlinks under `.agents/skills/`. The links point back to the canonical directories under `skills/`, so edits are visible immediately and no second copy can drift.

Codex scans `.agents/skills` from the current working directory toward the repository root. Start a new Codex conversation from this repository after setup. If a new or renamed skill does not appear, restart Codex.

In Codex CLI or the IDE extension, run `/skills` and confirm the expected skill name is present.

## 3. Run routing tests

Test cases live in `tests/cases/<skill-name>.json`. Run each case in a fresh conversation so prior context does not affect routing.

- `explicit`: include `$skill-name` and confirm the skill follows its complete workflow.
- `implicit`: omit the skill name and confirm its `description` routes the request correctly.
- `negative`: use an adjacent or unrelated request and confirm the skill does not activate.

Evaluate semantic behavior against `expected_behaviors` and confirm that none of the optional `forbidden_behaviors` occur. Do not require exact headings or exact prose unless the skill defines a machine-readable output contract.

## 4. Review behavior quality

For each positive case, check that the response:

1. Preserves the user's stated scope and inputs.
2. Uses the skill's non-obvious workflow rather than generic advice.
3. Loads supporting references only when their routing condition applies.
4. Verifies claims when the skill requires verification.
5. Produces the requested observable artifact or next action.

For each negative case, check that the skill is absent from the response behavior and does not pull the task into its own domain.

When a case fails, fix the narrowest relevant part of the skill: usually its `description`, a routing sentence, or one workflow constraint. Add a regression case that represents the observed failure.

## 5. Test generated artifacts

Artifact-producing skills require executable tests in addition to prompt cases. `make test` runs the standard-library unit tests under `tests/test_*.py`.

For `doctoral-field-training`, the automated test builds a tutorial in a temporary directory and verifies:

- HTML, CSS, canonical tutorial data, and durable learning state are created.
- The complete chapter plan is visible, while only the first chapter body is initially available.
- Explicit reading acknowledgement marks the current chapter read and unlocks exactly one next chapter.
- Rebuilding after next-chapter generation preserves memory and makes that chapter available.
- Source text is HTML-escaped.
- Existing managed output is not overwritten without `--force`.
- `--force` updates managed files without deleting unrelated files.

To inspect resume state:

```bash
python3 skills/doctoral-field-training/scripts/manage_progress.py status \
  --output "$output_dir"
```

Record a question without advancing the chapter:

```bash
python3 skills/doctoral-field-training/scripts/manage_progress.py remember \
  --output "$output_dir" \
  --question "Which assumption is doing the real work?"
```

To inspect a generated fixture manually:

```bash
output_dir="$(mktemp -d)/doctoral-tutorial"
python3 skills/doctoral-field-training/scripts/build_tutorial.py \
  --input tests/fixtures/doctoral-field-training/tutorial.json \
  --output "$output_dir"
echo "$output_dir/index.html"
```

## 6. Clean the local registration

Run:

```bash
make clean-local-test
```

The cleaner removes only symlinks managed by this repository. It preserves unexpected files, directories, and links.

## Test case format

Each file under `tests/cases/` has this shape:

```json
{
  "skill": "skill-name",
  "cases": [
    {
      "id": "unique-case-id",
      "invocation": "explicit",
      "should_activate": true,
      "prompt": "$skill-name Complete a realistic task.",
      "expected_behaviors": [
        "Produces an observable outcome"
      ],
      "forbidden_behaviors": [
        "Falls back to a known failure pattern"
      ]
    }
  ]
}
```

Allowed invocation values are `explicit`, `implicit`, and `negative`.
