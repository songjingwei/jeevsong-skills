# Jeevsong Skills

A collection of focused, reusable agent skills by [jeevsong](https://github.com/jeevsong).

The repository is packaged as a skills-only plugin for ChatGPT, Codex, and compatible agents. Each skill remains self-contained under `skills/`, so it can also be installed or copied independently.

## Available skills

- [`doctoral-field-training`](skills/doctoral-field-training/SKILL.md): guides a resumable doctoral reading process through an offline HTML textbook, revealing one interconnected review-paper chapter at a time after the learner confirms the preceding chapter was read.

## Repository structure

```text
.
├── plugin.json                 # Portable Agent Plugin manifest
├── .codex-plugin/plugin.json   # Codex compatibility manifest
├── skills/                     # Installable skills
├── templates/basic-skill/      # Copyable starting point
├── tests/cases/                # Routing and behavior test cases
├── docs/testing.md             # Local testing strategy
├── scripts/                    # Validation and local registration
└── .github/workflows/          # GitHub Actions
```

## Create a skill

Copy the template, then replace its metadata and instructions:

```bash
cp -R templates/basic-skill skills/my-skill
```

The directory name and the `name` in `SKILL.md` must match and use lowercase kebab-case. Write a concise `description` that explains both what the skill does and when it should activate.

Use `scripts/` only for deterministic or repeated operations, `references/` for detailed material loaded on demand, and `assets/` for templates or output resources.

Validate the collection and its test cases before committing:

```bash
make test
```

## Local development

Register every skill for repository-local Codex discovery:

```bash
make setup-local-test
make check-local-test
```

Then start a new Codex conversation from this repository, run `/skills`, and execute the cases under `tests/cases/`. The generated `.agents/skills/` links are ignored by Git and always point to the canonical skill sources.

See [docs/testing.md](docs/testing.md) for explicit, implicit, negative, and behavior testing. Clean the generated links with `make clean-local-test`.

## HTML tutorial output

`doctoral-field-training` plans a complete review-paper textbook in a folder chosen by the user, generates Chapter 1, and waits for the learner to return to the agent with an explicit reading acknowledgement before generating each next chapter. Its bundled tools produce and maintain:

```text
<output-folder>/
├── index.html
├── assets/
│   └── styles.css
└── data/
    ├── tutorial.json
    └── learning-state.json
```

The HTML works directly from the filesystem and has no remote runtime dependencies. The JSON files are the portable source of truth for resuming in a later conversation; RAG, Wiki views, and Skill UI Studio are optional adapters. See the skill's [tutorial contract](skills/doctoral-field-training/references/tutorial-contract.md) and [learning-memory contract](skills/doctoral-field-training/references/learning-loop-and-memory.md).

## Installation

Ask Codex to install the complete plugin from this GitHub repository, or use `$skill-installer` to install an individual directory under `skills/`.

Installation commands and release links will be added after the repository is published on GitHub.

## Versioning

The plugin follows [Semantic Versioning](https://semver.org/). Keep the `name`, `version`, and `description` fields synchronized between both plugin manifests; the validator enforces this.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
