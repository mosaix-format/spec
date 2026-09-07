# Mosaix Format — Skill for Claude

You are working inside a **Mosaix vault**: a folder of Markdown notes that follow the Mosaix Format v1.0 specification. This skill teaches you the rules. Follow them whenever you create, edit, or navigate notes in this vault.

---

## 1. What a note is

A note is a `.md` file that answers **one question**. If your draft answers two, split it into two notes. The body length is free; the scope is not.

## 2. Frontmatter — CORE keys

Every note MUST have YAML frontmatter with these keys, in this order:

```yaml
---
title: Name of the node
updated: YYYY-MM-DD
# (domain keys go here, if any)
summary: "One declarative sentence, 120–240 characters. Does NOT repeat the title. Does NOT start with 'This note…'."
keywords: [6 to 8 lowercase strings — synonyms, spoken phrasings, questions; must not duplicate tags]
entities:
  - {name: Entity Name, type: person}   # at most 12 items
relations:
  - {from: Entity A, type: verb phrase, to: Entity B}
links: [Target Note A, Target Note B]   # wikilink targets — each must resolve
rev: 000000000000                        # 12 hex chars; placeholder until computed
---
```

### Key details

- **`title`** — the name of the node. Usually matches the filename.
- **`updated`** — date of last substantive change.
- **`summary`** — written for a reader who has NOT opened the note. One sentence, 120–240 chars.
- **`keywords`** — how someone would *search* for this note. Not tags.
- **`entities`** — named things cited in the note. `type` must be one of: `person`, `company`, `product`, `project`, `tool`, `place`, `document`, `event` — or a custom type declared in the meta note.
- **`relations`** — typed links between named entities. `type` is a present-tense verb phrase (`owns`, `depends on`, `supplies`).
- **`links`** — wikilink targets this note points to. Every entry must resolve to an existing note.
- **`rev`** — hash of the body when metadata was last computed. Write `000000000000` as placeholder when creating a note by hand.
- **Entity limit** — at most 12 entities per note. More than 12 is a warning that the note may answer more than one question. MOCs and the meta note are exempt.

### Aliases

A vault may use Italian key names from pre-1.0 vaults. These are default aliases — always accepted:

| Alias | Canonical |
|---|---|
| `titolo` | `title` |
| `aggiornato` | `updated` |
| `riassunto` | `summary` |
| `parole_chiave` | `keywords` |
| `mcp_entita` | `entities` |
| `mcp_relazioni` | `relations` |
| `mcp_collegamenti` | `links` |
| `mcp_rev` | `rev` |
| `tipo` | `type` |
| `stato` | `status` |

Inside items: `nome` → `name`, `da` → `from`, `a` → `to`. Entity types: `persona` → `person`, `azienda` → `company`, etc. Status values: `ok` → `sourced`, `confermare` → `to-confirm`, `superato` → `superseded`.

A vault may declare additional aliases in its meta note.

## 3. Reliability axes

Two independent markers. The recommended convention is a `status` key:

| Value | Meaning |
|---|---|
| `sourced` | comes from a document, system, or working conversation; source is named |
| `to-confirm` | hypothesis, draft, placeholder; not yet validated |
| `superseded` | no longer valid, kept in place (R7) |

A second axis (does the thing exist?) uses inline markers: 🟢 implemented · 🟡 decided · ⚠️ open · ❌ excluded.

A fact can be `sourced` and 🟡 not implemented: a verified fact about something that doesn't exist yet.

## 4. Note types

Three types have format-level meaning:

| `type` | Role |
|---|---|
| `moc` | Map of Content: entry point that narrates an area and lists its notes |
| `synthesis` | condensed view of an area, written to be read alone; lives in `_synthesis/` |
| `document` | composed document: a view that joins atomic notes without duplicating them (see §6) |

## 5. Vault structure

Folders are free. Three names are reserved:

- **`_meta/`** — governance: meta note, taxonomy, open questions
- **`_synthesis/`** — synthesis notes (alias `_sintesi/`)
- **`_inbox/`** — unprocessed material; not checked for conformance

Optional: `_private/` (excluded from version control, not part of the vault).

### The meta note

The vault MUST have a meta note (`_meta/Conventions.md`, or `README.md` / `CLAUDE.md` at root) declaring:

```yaml
mosaix: "1.0"
folders: {01-Company: who they are, 02-Market: where they sell}
reliability: {key: status, values: [sourced, to-confirm, superseded]}
tags: [moc, meta, player, market]
domain_keys: {client: string, country: ISO-3166 alpha-2}
aliases: {}
entity_types: [department, regulation]       # custom types beyond the 8 defaults
relation_types: [owns, supplies, depends on] # optional closed vocabulary
payload: [exports/]                          # folders excluded from checks
maintainers: [{name: A. Fiorino, area: market}]
```

**Read the meta note first** when entering a vault. It tells you the custom types, aliases, tags, and domain keys this vault uses.

### Open questions ledger

The vault MUST have `_meta/Open questions.md` (aliases: `Assunzioni da confermare.md`, `Domande aperte.md`) listing what is unknown or contradictory: the question, competing versions with dates and sources, practical consequence, who resolves it.

## 6. Composed documents

A note with `type: document` joins atomic notes into a readable document:

```yaml
type: document
fragments: [Note A, Note B, Note C]  # reading order
pool: [Note D]                       # considered but not included
layout:
  cover: {title: Report title, date: 2026-09-03}
  page: A4
  sections:
    - {title: Section name, fragments: [Note A, Note B]}
  show: [summary, status]
```

The fragments stay atomic and separate. The document is only the view. An edit belongs to the fragment, not to the document.

## 7. Rules R1–R8

Follow these whenever you write or modify notes:

1. **R1 — Atomicity.** One note, one question. If you're writing a note that answers two questions, split it.
2. **R2 — Self-description.** Every note carries the CORE frontmatter.
3. **R3 — Connectedness.** No orphans (every note must have at least one incoming link). No broken links.
4. **R4 — Declared taxonomy.** Every tag and domain key is declared in the meta note. If you introduce a new tag, add it to the taxonomy in the same change.
5. **R5 — Composition over duplication.** Content that must be read together is joined with a composed document or a synthesis, never copied.
6. **R6 — Record, don't resolve.** A contradiction between notes goes into the open-questions ledger with both versions. Never pick a winner silently. Never choose numbers, prices, dates, or commitments on behalf of the owner.
7. **R7 — Supersede, don't delete.** A note that is no longer valid gets `status: superseded` and stays in place — other notes link to it. Delete only notes created in error.
8. **R8 — Propose, don't apply.** You never write directly to the vault's main line. You write to a branch, a PR, or a staging area. Present your changes for human review.

## 8. Links and wikilinks

- Use `[[Note title]]` to link. Optionally `[[Note title|display text]]` or `[[Note title#Section]]`.
- Embeds use `![[Note title]]`.
- Every wikilink must resolve to an existing note (by filename without extension, case-sensitive).
- The `links` frontmatter key is the machine-readable mirror of outbound wikilinks.

## 9. When you navigate a vault

When asked to explore, find, or understand a vault:

1. **Start from the meta note** — it tells you the structure, conventions, and taxonomy.
2. **Read MOCs** — they are the maps. Follow them to find the notes you need.
3. **Use `entities` and `tags`** to find notes about a specific thing or topic.
4. **Follow `links`** to trace dependencies between notes.
5. **Check `status`** to know whether information is sourced or needs confirmation.
6. **Read `summary` first** — it tells you what the note contains without opening the body.
7. **Check `rev`** — if you can compute it, a mismatch means the metadata is stale.

## 10. When you write a note

Checklist before presenting a note:

- [ ] Answers exactly one question (R1)
- [ ] Has all CORE keys in canonical order (R2)
- [ ] `summary` is 120–240 chars, does not repeat title, does not start with "This note…"
- [ ] `keywords` has 6–8 items, lowercase, no overlap with `tags`
- [ ] `entities` has ≤12 items with valid types
- [ ] Every `links` entry resolves to an existing note
- [ ] Every new tag is added to the taxonomy (R4)
- [ ] No content is duplicated from another note (R5)
- [ ] Contradictions are logged, not resolved (R6)
- [ ] Body contains `[[wikilinks]]` to related notes (R3)
- [ ] `rev` is `000000000000` (placeholder) unless you can compute the hash

## 11. What this skill does NOT cover

The following are out of scope (§8 of the specification) and are not part of this skill:

- How summary, keywords, entities, relations, and links are generated (enrichment)
- How documents are turned into notes (ingest, splitting)
- How notes are retrieved for a task (search, ranking, embeddings)
- How composed documents are printed or paginated (editors)
- How the vault is exposed to agents (MCP tools, APIs)

A vault produced by hand, with no tooling, can be fully conformant.

## 12. The checker

The reference checker `audit_reference.py` validates a vault from disk. It is read-only and offline:

```
python audit_reference.py /path/to/vault
python audit_reference.py /path/to/vault --verbose --check-rev
python audit_reference.py /path/to/vault --json > report.json
```

Exit code 0 = conformant. If the checker is available in the vault or in `spec/`, run it after making changes and report the result.

---

*Mosaix Format v1.0 — specification at https://mosaixformat.org — CC BY-SA 4.0*
