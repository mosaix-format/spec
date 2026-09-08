---
mosaix: "1.0"
title: Conventions
updated: YYYY-MM-DD
tags: [meta]
summary: "Folder contract, reliability convention, tag taxonomy, and domain declarations for this vault — the single source of truth for the vault's structure."
keywords: [conventions, meta, vault structure, taxonomy, domain keys, reliability, folder contract]
entities:
  - {name: VAULT_NAME, type: project}
relations: []
links: [Open questions]
rev: 000000000000
folders:
  _meta: vault governance
  _synthesis: synthesis notes for agent context
reliability:
  key: status
  values: [sourced, to-confirm, superseded]
tags: [moc, meta, ledger]
domain_keys: {}
entity_types: []
relation_types: []
payload: []
maintainers:
  - {name: Your Name, area: all}
---

# Conventions

## Folder contract

| Folder | Question it answers |
|---|---|
| `_meta/` | Vault governance: this note, taxonomy, open questions |
| `_synthesis/` | Synthesis notes written to be read alone as context |

Add your content folders here, e.g. `01-Area/`.

## Reliability

Status is expressed with the `status` frontmatter key.

| Value | Meaning |
|---|---|
| `sourced` | Comes from a document or working conversation; source is named |
| `to-confirm` | Hypothesis, draft, or placeholder; not yet validated |
| `superseded` | No longer valid; kept in place (R7) |

## Tag taxonomy

Declare every tag in use. A tag used in a note and absent here is a conformance warning (§5.4).

| Tag | What it marks |
|---|---|
| `#moc` | Map of content — entry point for an area |
| `#meta` | Vault governance notes |
| `#ledger` | Open-questions ledger |

## Domain keys

Add vault-specific frontmatter keys here, e.g. `client`, `country`, `stage`.
Leave empty if no domain keys are needed beyond the CORE keys.
