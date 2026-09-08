# Mosaix Format

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](LICENSE.md) [![Version](https://img.shields.io/badge/version-v1.0.1-blue.svg)](CHANGELOG.md) ![Mosaix 1.0 conformant](https://mosaixformat.org/badge.svg)

**A file-level format for knowledge vaults made of atomic, self-describing notes — retrievable one at a time by machines, readable as composed documents by people.**

Every note is a tile that stands on its own. The picture exists only in the whole.

- Specification (normative, English): [`Mosaix-Format-v1.0.en.md`](Mosaix-Format-v1.0.en.md)
- Specifica (italiano): [`Mosaix-Format-v1.0.it.md`](Mosaix-Format-v1.0.it.md)
- Machine-readable spec: [`spec.yaml`](spec.yaml) — every CORE key, rule, conformance check and alias in one parseable file
- Reference conformance checker: [`audit_reference.py`](audit_reference.py) — Python 3.10+, standard library only, read-only, offline
- Conformance test corpus: [`tests/conformance/`](tests/conformance/) — 39 test cases with expected results and a runner
- Reference MCP server: [`mosaix_mcp/`](mosaix_mcp/) — stdlib-only, JSON-RPC 2.0 over stdio, 6 tools
- Vault scaffolding: [`mosaix_init.py`](mosaix_init.py) — create a new vault with the standard structure
- Vault migration: [`mosaix_migrate.py`](mosaix_migrate.py) — bring existing Markdown vaults toward Mosaix conformance
- Example vault (the specification itself, as a conformant vault): [`example-vault/`](example-vault/)
- Second example vault (a fictional bakery, ordinary knowledge): [`example-vault-bakery/`](example-vault-bakery/)
- Obsidian plugin spec: [`OBSIDIAN-PLUGIN-SPEC.md`](OBSIDIAN-PLUGIN-SPEC.md) — functional requirements for `obsidian-mosaix`
- Governance: [`GOVERNANCE.md`](GOVERNANCE.md) · Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md) · License: [CC BY-SA 4.0](LICENSE.md)
- Site: https://mosaixformat.org

## What it is

Markdown + YAML frontmatter + wikilinks, with a small set of rules on top: one note answers one question; every note carries a summary, keywords, typed entities and relations, and a revision hash; contradictions are recorded, never silently resolved; superseded notes are marked, never deleted; automated writes are proposed, never applied. A note type (`document`) composes many atomic notes into one readable document without duplicating them.

Any Markdown tool can read a Mosaix vault. Obsidian is the reference host, not a dependency. Vaults written with other key names (the Italian `mcp_entita`, `tipo`, `stato`… of the source vaults) are conformant unchanged: they are default aliases, and any other alias can be declared in the vault's meta note.

## Repository layout

```
Mosaix-Format-v1.0.en.md   the specification (normative)
Mosaix-Format-v1.0.it.md   courtesy translation
spec.yaml                  machine-readable spec: keys, rules, conformance checks, aliases
audit_reference.py         reference checker, stdlib only
tests/conformance/         39 test cases + runner for the checker
mosaix_mcp/                reference MCP server (6 tools, stdlib only, JSON-RPC 2.0)
mosaix_init.py             scaffold a new vault
mosaix_migrate.py          migrate an existing Markdown vault toward conformance
action.yml                 GitHub Action wrapping the checker
example-vault/             the specification itself as a conformant vault (+ Obsidian templates)
example-vault-bakery/      a fictional bakery: the format on ordinary knowledge
site/                      mosaixformat.org, served by GitHub Pages from this folder
brand/                     mark, favicon, wordmark and identity notes
skill/                     6 Claude skills: agent instructions for reading and writing conformant notes
GOVERNANCE.md              versioning policy, RFC process, backward compat guarantee
OBSIDIAN-PLUGIN-SPEC.md    functional spec for the obsidian-mosaix plugin
```

Both example vaults are generated from a single `vault-data.js` by `export_vault.py`, which also runs the checker and refreshes the copies the site serves. Edit the `.js`, not the `.md` files.

## Check a vault

```
python audit_reference.py /path/to/vault
python audit_reference.py /path/to/vault --verbose --exclude=exports/
python audit_reference.py /path/to/vault --json > report.json
```

Exit code 0 means conformant. Errors and warnings map to §10 of the specification. The checker reads the vault from disk, writes nothing and opens no network connection.

## Start a new vault

```
python mosaix_init.py my-vault
python mosaix_init.py my-vault --with-examples
```

Creates the standard directory structure (`_meta/`, `_synthesis/`, `_inbox/`), a meta note with an empty taxonomy, an open-questions ledger, and a GitHub Actions workflow. Pass `--with-examples` to copy the example vault as a reference.

## Migrate an existing vault

```
python mosaix_migrate.py /path/to/existing/vault --dry-run
python mosaix_migrate.py /path/to/existing/vault --git-dates
```

Reads every `.md` file, preserves existing frontmatter, and adds the missing CORE keys with best-effort inference (title from H1, summary from body, keywords from term frequency, tags from Obsidian `#tags`, links from wikilinks, rev from body hash). The body is never modified. Every migrated note gets `reliability: to-confirm`. Use `--dry-run` to preview without writing. Use `--git-dates` to pull `updated` from `git log` instead of filesystem mtime.

## Reference MCP server

```
python -m mosaix_mcp /path/to/vault
```

A minimal MCP server (JSON-RPC 2.0 over stdio, stdlib-only Python) that exposes six tools: `read_note`, `write_note`, `search`, `compose`, `check`, `list_notes`. Writes validate against §10 before persisting. No external dependencies, no vector DB, no network — the "SQLite" of Mosaix, not the "PostgreSQL".

## Status

v1.0.1 — September 2026. Extracted from three vaults in production use (code documentation, industrial market intelligence, education marketing).

Mosaix is an open format. The specification is open (CC BY-SA 4.0); how vaults are produced, enriched, searched or composed is out of scope by design (§8) and not part of this repository. `skill/` is the one exception: optional, non-normative instructions for one agent (Claude) to read and write conformant notes. Nothing in the specification or the checker depends on it.

## Check on every push

Add this workflow to your repository. The action runs the reference checker and comments the result on every pull request.

```yaml
name: Mosaix
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: write }
    steps:
      - uses: actions/checkout@v4
      - uses: mosaix-format/spec@v1.0.1
        with: { vault: ., exclude: "exports/" }
```

The conformance badge `https://mosaixformat.org/badge.svg` should only be displayed when this check is green.

## Skills

Six optional skills teach Claude how to read and write Mosaix-conformant notes. Each skill is a folder with a `SKILL.md` file — install only the ones you need.

| Skill | What it does |
|---|---|
| `skill/` (base) | Write conformant notes — the foundation |
| `skill/mosaix-audit/` | Verify a vault with the checker |
| `skill/mosaix-compose/` | Assemble notes into composed documents |
| `skill/mosaix-onboard/` | Bootstrap a vault from scratch |
| `skill/mosaix-ingest/` | Split documents into atomic notes |
| `skill/mosaix-enrich/` | Fill CORE frontmatter, validate quality |

**Install a skill** (personal, all projects):

```bash
npx degit mosaix-format/spec/skill ~/.claude/skills/mosaix-format
npx degit mosaix-format/spec/skill/mosaix-audit ~/.claude/skills/mosaix-audit
```

**Install for one project** (shared via repo):

```bash
npx degit mosaix-format/spec/skill .claude/skills/mosaix-format
```

Skills are non-normative: they encode the specification as agent instructions but add no rules beyond it. Nothing in the checker or the format depends on them.

## Contributing

Open an issue with a concrete case, then a pull request against the English file, which is normative. The full process, and what counts as a MINOR or MAJOR change, is in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citing

> Fiorino, A. (2026). *Mosaix Format — Specification v1.0.1*. https://mosaixformat.org — source: `mosaix-format/spec@v1.0.1`

Cite the tag, not the branch: tags are immutable.
