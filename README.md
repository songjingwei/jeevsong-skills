# Jeevsong Skills

A collection of focused, reusable agent skills by [jeevsong](https://github.com/jeevsong).

The repository is packaged as a skills-only plugin for ChatGPT, Codex, and compatible agents. Each skill remains self-contained under `skills/`, so it can also be installed or copied independently.

## Available skills

- [`review-driven-learning`](skills/review-driven-learning/SKILL.md): a PhD-oriented learning coach that builds a field map, paper-review syllabus, historical problem lineage, active-recall exercises, and structured learning-package content.

## Repository structure

```text
.
├── plugin.json                 # Portable Agent Plugin manifest
├── .codex-plugin/plugin.json   # Codex compatibility manifest
├── skills/                     # Installable skills
├── templates/basic-skill/      # Copyable starting point
├── scripts/validate.py         # Local and CI validation
└── .github/workflows/          # GitHub Actions
```

## Create a skill

Copy the template, then replace its metadata and instructions:

```bash
cp -R templates/basic-skill skills/my-skill
```

The directory name and the `name` in `SKILL.md` must match and use lowercase kebab-case. Write a concise `description` that explains both what the skill does and when it should activate.

Use `scripts/` only for deterministic or repeated operations, `references/` for detailed material loaded on demand, and `assets/` for templates or output resources.

Validate the collection before committing:

```bash
python3 scripts/validate.py
```

## Local development

Codex can load repository-scoped skills from `.agents/skills`. During development, symlink a skill there instead of maintaining a second copy:

```bash
mkdir -p .agents/skills
ln -s ../../skills/my-skill .agents/skills/my-skill
```

Remove development symlinks before committing unless the repository intentionally needs them.

## Installation

Ask Codex to install the complete plugin from this GitHub repository, or use `$skill-installer` to install an individual directory under `skills/`.

Installation commands and release links will be added after the repository is published on GitHub.

## Versioning

The plugin follows [Semantic Versioning](https://semver.org/). Keep the `name`, `version`, and `description` fields synchronized between both plugin manifests; the validator enforces this.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
