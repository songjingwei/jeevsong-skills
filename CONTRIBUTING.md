# Contributing

Contributions should keep each skill focused on one clear job.

## Add or update a skill

1. Create or edit `skills/<skill-name>/SKILL.md`.
2. Keep the folder name and frontmatter `name` identical and in lowercase kebab-case.
3. Make `description` specific enough to distinguish matching and non-matching requests.
4. Add scripts, references, or assets only when they materially improve the workflow.
5. Add or update `tests/cases/<skill-name>.json` with explicit, implicit, and negative prompts.
6. Test the skill with representative prompts in fresh conversations.
7. Run `make test`.

Skills that generate files must include an executable fixture test. Verify the output contract and overwrite behavior rather than matching incidental prose.

Avoid committing secrets, credentials, user-generated artifacts, or machine-specific paths. Dependency-free JavaScript CLIs compiled from a skill's TypeScript sources are committed intentionally so an installed skill can run without development dependencies; keep them synchronized with `npm run build`.

## Pull requests

Explain the user problem, include example prompts, and describe how you verified the behavior. Keep unrelated skills out of the same change.
