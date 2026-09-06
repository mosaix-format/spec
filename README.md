# Mosaix Format

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC_BY--SA_4.0-lightgrey.svg)](LICENSE.md) [![Version](https://img.shields.io/badge/version-v1.0.0-blue.svg)](CHANGELOG.md) ![Mosaix 1.0 conformant](https://mosaixformat.org/badge.svg)

**A file-level format for knowledge vaults made of atomic, self-describing notes — retrievable one at a time by machines, readable as composed documents by people.**

Every note is a tile that stands on its own. The picture exists only in the whole.

- Specification (normative, English): [`Mosaix-Format-v1.0.en.md`](Mosaix-Format-v1.0.en.md)
- Specifica (italiano): [`Mosaix-Format-v1.0.it.md`](Mosaix-Format-v1.0.it.md)
- Reference conformance checker: [`audit_reference.py`](audit_reference.py) — Python 3.10+, standard library only, read-only, offline
- Example vault (the specification itself, as a conformant vault): [`example-vault/`](example-vault/)
- Second example vault (a fictional bakery, ordinary knowledge): [`example-vault-bakery/`](example-vault-bakery/)
- Changelog: [`CHANGELOG.md`](CHANGELOG.md) · License: [CC BY-SA 4.0](LICENSE.md)
- Site: https://mosaixformat.org

## What it is

Markdown + YAML frontmatter + wikilinks, with a small set of rules on top: one note answers one question; every note carries a summary, keywords, typed entities and relations, and a revision hash; contradictions are recorded, never silently resolved; superseded notes are marked, never deleted; automated writes are proposed, never applied. A note type (`document`) composes many atomic notes into one readable document without duplicating them.

Any Markdown tool can read a Mosaix vault. Obsidian is the reference host, not a dependency. Vaults written with other key names (the Italian `mcp_entita`, `tipo`, `stato`… of the source vaults) are conformant unchanged: they are default aliases, and any other alias can be declared in the vault's meta note.

## Repository layout

```
Mosaix-Format-v1.0.en.md   the specification (normative)
Mosaix-Format-v1.0.it.md   courtesy translation
audit_reference.py         reference checker, stdlib only
action.yml                 GitHub Action wrapping the checker
example-vault/             the specification itself as a conformant vault (+ Obsidian templates)
example-vault-bakery/      a fictional bakery: the format on ordinary knowledge
site/                      mosaixformat.org, served by GitHub Pages from this folder
brand/                     mark, favicon, wordmark and identity notes
skill/                     optional Claude Skill: agent instructions for reading and writing conformant notes
```

Both example vaults are generated from a single `vault-data.js` by `export_vault.py`, which also runs the checker and refreshes the copies the site serves. Edit the `.js`, not the `.md` files.

## Check a vault

```
python audit_reference.py /path/to/vault
python audit_reference.py /path/to/vault --verbose --exclude=exports/
python audit_reference.py /path/to/vault --json > report.json
```

Exit code 0 means conformant. Errors and warnings map to §10 of the specification. The checker reads the vault from disk, writes nothing and opens no network connection.

## Status

v1.0.0 — September 2026. Extracted from three vaults in production use (code documentation, industrial market intelligence, education marketing).

Mosaix is a format by SLIM, maintained by Boom Digital. The specification is open (CC BY-SA 4.0); how vaults are produced, enriched, searched or composed is out of scope by design (§8) and not part of this repository. `skill/` is the one exception: optional, non-normative instructions for one agent (Claude) to read and write conformant notes. Nothing in the specification or the checker depends on it.

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
      - uses: mosaix-format/spec@v1.0.0
        with: { vault: ., exclude: "exports/" }
```

The conformance badge `https://mosaixformat.org/badge.svg` should only be displayed when this check is green.

## Contributing

Open an issue with a concrete case, then a pull request against the English file, which is normative. The full process, and what counts as a MINOR or MAJOR change, is in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Citing

> Fiorino, A. (2026). *Mosaix Format — Specification v1.0.0*. Boom Digital. https://mosaixformat.org — source: `mosaix-format/spec@v1.0.0`

Cite the tag, not the branch: tags are immutable.
