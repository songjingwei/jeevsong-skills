# Contributing

Contributions should keep each skill focused on one clear job.

## Add or update a skill

1. Create or edit `skills/<skill-name>/SKILL.md`.
2. Keep the folder name and frontmatter `name` identical and in lowercase kebab-case.
3. Make `description` specific enough to distinguish matching and non-matching requests.
4. Add scripts, references, or assets only when they materially improve the workflow.
5. Test the skill with representative prompts, including one prompt that should not activate it.
6. Run `python3 scripts/validate.py`.

Avoid committing secrets, credentials, generated output, or machine-specific paths.

## Pull requests

Explain the user problem, include example prompts, and describe how you verified the behavior. Keep unrelated skills out of the same change.
