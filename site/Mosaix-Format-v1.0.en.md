---
title: Mosaix Format — Specification v1.0
version: 1.0.0
status: published
updated: 2026-09-04
license: CC BY-SA 4.0
author: Andrea Fiorino
summary: "A file-level format for knowledge vaults made of atomic, self-describing notes that machines can retrieve one at a time and humans can read as composed documents."
keywords: [knowledge vault, atomic notes, frontmatter, wikilinks, markdown, LLM context, bounded context, specification]
---

# Mosaix Format — Specification v1.0

## 0. Status of this document

This document specifies the **Mosaix Format**, version 1.0. The name comes from the mosaic: every note is a tile that stands on its own, and the picture exists only in the whole. It is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): you may copy, adapt and redistribute it, including commercially, provided you credit the author and release derivatives under the same license. The name "Mosaix Format" and its version numbering are part of the specification: a vault may claim conformance to "Mosaix 1.0" only if it satisfies §10.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in RFC 2119.

## 1. Purpose

A vault in this format is a body of knowledge about one domain (a client, a product, a codebase, a project) written so that:

1. **a machine can retrieve one note at a time** and have enough context to act, without reading the rest of the vault;
2. **a human can read many notes as one document**, without opening them one by one;
3. **nothing is silently lost or overwritten**: contradictions are recorded, superseded notes are marked, machine edits are proposed rather than applied.

The format is deliberately small. It fixes *what a note carries* and *which rules the vault obeys*. It does not fix how notes are produced, enriched, searched, ranked, composed or edited: those are implementations (§8).

## 2. Substrate

A Mosaix vault is a directory tree of plain-text files.

- Notes are UTF-8 files with the `.md` extension containing CommonMark Markdown.
- Each note MAY start with a YAML frontmatter block delimited by `---` lines.
- Notes reference each other with **wikilinks**: `[[Note title]]`, optionally `[[Note title|display text]]`, optionally with a heading `[[Note title#Heading]]`. A wikilink resolves by the target note's **basename without extension**, matched case-sensitively, anywhere in the vault.
- Embeds use `![[Note title]]` and `![[file.ext]]`, resolved the same way.
- Tags are `#tag` or `#namespace/tag` tokens in the body, or entries of the `tags` frontmatter list. The two forms are equivalent.

Any tool that reads Markdown files from disk can read a Mosaix vault. No application is required. Obsidian is the reference host application (§9), not a dependency.

## 3. The note (the "tile")

A **note** answers one question. If a draft answers two, it is two notes. The body length is not constrained; the *scope* is.

### 3.1 Frontmatter — CORE (required for conformance)

| Key | Type | Written by | Purpose |
|---|---|---|---|
| `title` | string | human, or derived from the filename | the name of the node |
| `updated` | date `YYYY-MM-DD` | human or system | last substantive change; drives staleness of the note |
| `tags` | list of strings | human | taxonomy and filtering |
| `summary` | string, 120–240 characters | human or enrichment | one declarative sentence saying what the note contains; the unit a machine reads first |
| `keywords` | list of 6–8 lowercase strings | human or enrichment | how someone would search for this note: synonyms, spoken-language phrasings, questions. MUST NOT duplicate `tags` |
| `entities` | list of `{name, type}`, at most 12 | enrichment or human | named things in the note; `type` MUST be one of `person`, `company`, `product`, `project`, `tool`, `place`, `document`, `event`, or a type declared in the meta note (§5.4) |
| `relations` | list of `{from, type, to}` | enrichment or human | typed links between named entities; `type` is a short verb phrase in the present tense (`owns`, `depends on`, `supplies`), or a value from the vault's relation vocabulary if one is declared |
| `links` | list of strings | enrichment or human | wikilink targets this note points to; each MUST resolve to an existing note |
| `rev` | string, 12 hex chars | system | hash of the body at the time `entities`, `relations` and `links` were last computed; a mismatch with the current body means the metadata is stale |

Notes:

- `summary` MUST NOT repeat the title and MUST NOT begin with "This note…" or its equivalent. It is written for a reader who has not opened the note.
- **Aliases.** A vault MAY write any CORE key under an alias declared in its meta note (§5.4); checkers treat a declared alias as the canonical key. The following aliases are recognised by default, so that vaults created before this version remain conformant: `mcp_entita` → `entities`, `mcp_relazioni` → `relations`, `mcp_collegamenti` → `links`, `mcp_rev` → `rev`, `aggiornato` → `updated`, `titolo` → `title`, `riassunto` → `summary`, `parole_chiave` → `keywords`; inside entity and relation items, `nome` → `name`, `tipo` → `type`, `da` → `from`, `a` → `to`; and the entity type values `persona azienda prodotto progetto strumento luogo documento evento` → `person company product project tool place document event`.
- `entities` SHOULD list at most 12 items. A note that names more things than that is usually answering more than one question (R1); a checker reports the excess as a warning. MOCs and the meta note are exempt: listing is their job.
- The canonical key order is `title · updated · [domain keys] · summary · keywords · entities · relations · links · rev`. Tools SHOULD preserve it.
- **The body is never touched by metadata operations.** Any process that rewrites frontmatter MUST leave the body byte-identical.

### 3.2 Frontmatter — reliability axes (recommended)

Two independent questions, answered by two independent markers. They MAY be expressed as frontmatter keys, as tags, or as inline symbols in the body; a vault MUST choose one convention and document it in its meta note (§5.4). The recommended convention is a `status` key.

**Axis A — is it true?**

| Marker | `status` value | Meaning |
|---|---|---|
| ✅ sourced | `sourced` | comes from a document, a system, or a working conversation; the source is named |
| ⚠️ to confirm | `to-confirm` | hypothesis, draft, placeholder; not yet validated |
| — superseded | `superseded` | no longer valid, kept in place (R7) |

**Axis B — does it exist?** (used where the vault describes something being built)

| Marker | Meaning |
|---|---|
| 🟢 implemented | exists and works as described |
| 🟡 decided | decided, not built |
| ⚠️ open | undecided |
| ❌ excluded | decided against |

A statement may be ✅ sourced and 🟡 not implemented: a verified fact about something that does not yet exist. Keeping the axes separate is what lets a reader, months later, tell an intention from a fact. Default aliases for `status` values: `ok` → `sourced`, `confermare` → `to-confirm`, `superato` → `superseded`; `stato` → `status`.

### 3.3 Frontmatter — domain keys (per vault)

A vault MAY add any keys it needs (`campaign`, `client`, `country`, `reliability`, `stage`…). Domain keys MUST be declared in the vault's meta note (§5.4) with their allowed values. Undeclared keys are a conformance warning, not an error.

### 3.4 Note types

The `type` key (or a `#type/...` tag) MAY classify notes. Three types have format-level meaning:

| `type` | Role |
|---|---|
| `moc` | *Map of Content*: an entry point that narrates an area and lists its notes. A vault MUST have at least one, usually `Home` or `00-Index`. |
| `synthesis` | a synthesis written to be read alone as context for a task; lives in `_synthesis/` (§5.2) |
| `document` | a **composed document**: a note whose frontmatter lists the notes it is assembled from (§6) |

Default aliases: `tipo` → `type`; `sintesi` → `synthesis`; `documento` → `document`.

### 3.5 Example

```markdown
---
title: Portwest — player card
updated: 2026-08-12
tags: [player, ppe, competitor]
status: sourced
summary: "Irish PPE manufacturer present in 130+ countries with an own-brand line that undercuts distributors on price; the reference competitor for price."
keywords: [portwest, price competitor, own brand, irish ppe manufacturer, 130 countries, private label]
entities:
  - {name: Portwest, type: company}
relations:
  - {from: Portwest, type: competes with, to: Ateş}
links: [PPE consolidation 2025, Strategic scenarios]
rev: a81c0d33ef21
---

# Portwest — player card

Sells in 130+ countries. Own-brand line undercuts distributors. ✅ sourced (company site, 2026-07).
See [[PPE consolidation 2025]] and [[Strategic scenarios]].
```

## 4. Links and the graph

- A note MUST have at least one incoming wikilink from another note, or from a MOC. A note with no incoming link is an **orphan** and is a conformance error.
- Every wikilink MUST resolve. An unresolved wikilink is a conformance error.
- `links` is the machine-readable mirror of the note's outbound wikilinks. It MAY be a subset of the wikilinks in the body; it MUST NOT contain targets that do not exist.
- The notes, their `entities`, `relations` and wikilinks together form the vault graph. The graph is derived from files; it is never the source of truth.

## 5. Vault structure

### 5.1 Free layout, reserved names

Folders are free. Numbered prefixes (`00-Index`, `01-Company`, …) are a common convention and are read as a **reading order**, not a build order. Three folder names are reserved:

| Folder | Content |
|---|---|
| `_meta/` | the vault's own governance: meta note, taxonomy, open questions (§5.4) |
| `_synthesis/` | synthesis notes written to be consumed alone as context |
| `_inbox/` | material that has entered the vault but has not yet been turned into notes; nothing in `_inbox/` counts toward conformance |

`_sintesi/` is recognised as an alias of `_synthesis/`. A vault MAY additionally keep a `_private/` folder excluded from version control for personal working material. Nothing in `_private/` is part of the vault. Folders holding content exports that are not notes MAY be declared as **payload** in the meta note and are then excluded from the frontmatter check.

### 5.2 Synthesis notes

A `_synthesis/` note condenses an area of the vault into a text that can be read alone. It MUST link to the notes it summarises. It is the recommended unit to hand to a machine or a newcomer before any task in that area. It is *not* a substitute for the notes: when it disagrees with a note, the note wins and the synthesis is stale.

### 5.3 Open questions ledger

The vault MUST have one note that lists what is not yet known or is contradictory. Its canonical location is `_meta/Open questions.md`. Each entry records: the question, the competing versions with their dates and sources, the practical consequence of choosing one over the other, and who is expected to resolve it. `Assunzioni da confermare.md` and `Domande aperte.md` are recognised as aliases.

### 5.4 Meta note

The vault MUST have a note (`_meta/Conventions.md`, or a `README.md` / `CLAUDE.md` at the root) that states: the folder contract (which question each folder answers), the reliability convention chosen (§3.2), the domain keys and their values (§3.3), the tag taxonomy with every tag in use, any aliases for CORE keys, any additional entity types, an optional closed relation vocabulary, any payload folders, and the people responsible for areas. The taxonomy MAY live in its own note inside `_meta/`. **A tag used in a note and absent from the taxonomy is a conformance warning.** The taxonomy is updated in the same change that introduces the tag.

The meta note declares these in its frontmatter so that tools can read them. This block is part of 1.0: the reference checker reads it (`aliases`, `entity_types`, `relation_types`, `payload`, and `tags` as the taxonomy).


```yaml
mosaix: "1.0"
folders: {01-Company: who they are, 02-Market: where they sell}
reliability: {key: status, values: [sourced, to-confirm, superseded]}
tags: [moc, meta, ledger, player, market]
domain_keys: {client: string, country: ISO-3166 alpha-2}
aliases: {aggiornato: updated}
entity_types: [department, regulation]
relation_types: [owns, supplies, competes with, depends on]
payload: [exports/]
maintainers: [{name: A. Fiorino, area: market}]
```

All are optional except `mosaix`.

## 6. Composed documents

Atomic notes are for machines. Humans read documents. The format therefore defines a note type that is a **view over other notes** without duplicating them.

A note with `type: document` MUST carry:

| Key | Type | Meaning |
|---|---|---|
| `fragments` | ordered list of note titles | the notes that make up the document, in reading order |
| `pool` | list of note titles (optional) | candidate notes considered but not included |
| `layout` | map (optional) | presentation hints (cover, sections, page format); free-form |

Default aliases: `mcp_frammenti` → `fragments`, `mcp_pool` → `pool`, `mcp_layout` → `layout`.

Example of a composed document's frontmatter, with a `layout` map. The map is free-form; the keys shown are the ones the reference implementations use, and a tool MUST ignore keys it does not understand:

```yaml
type: document
fragments: [PPE consolidation 2025, Portwest — player card, Strategic scenarios]
pool: [PPE trade fairs Europe 2026]
layout:
  cover: {title: Market entry brief — PPE, Europe, subtitle: Board reading, date: 2026-09-03}
  page: A4
  sections:
    - {title: Market, fragments: [PPE consolidation 2025, Portwest — player card]}
    - {title: Recommendation, fragments: [Strategic scenarios]}
  show: [summary, status]      # what of each fragment's frontmatter is printed
```

Its body MAY contain narrative connecting the fragments and MAY embed them with `![[Note]]`. The rule is: **the fragments stay atomic and separate; the document is only the view that joins them.** An edit made while reading the composed document belongs to the fragment's note, not to the document.

Because the composed document is itself a note, it inherits versioning, review, search and linking for free. No second storage channel is needed.

## 7. Rules of the vault

A conforming vault obeys the following. R1–R5 are verifiable from files; R6–R8 are process rules the meta note commits to.

- **R1 — Atomicity.** One note answers one question.
- **R2 — Self-description.** Every note carries the CORE frontmatter (§3.1).
- **R3 — Connectedness.** No orphans, no broken links (§4).
- **R4 — Declared taxonomy.** Every tag and every domain key is declared in the meta note (§5.4).
- **R5 — Composition over duplication.** Content that must be read together is joined with a composed document (§6) or a synthesis (§5.2), never copied.
- **R6 — Record, don't resolve.** A contradiction between notes is entered in the open-questions ledger with both versions. Nobody picks a winner silently. Numbers, prices, dates and commitments to third parties are never chosen on behalf of the owner.
- **R7 — Supersede, don't delete.** A note that is no longer valid is marked superseded (`status: superseded`, `#status/archived`, or a banner) and left in place, because other notes link to it. Deletion is reserved for notes that were created in error.
- **R8 — Propose, don't apply.** Any automated process that writes to the vault writes to a branch, a pull request, or a staging area that a human reviews. Automated processes never write to the vault's main line. `rev` is the mechanism that lets a reviewer see whether a proposal was made against the current body.

## 8. Out of scope

The following are **not** defined by this specification. They are implementations, and different implementations may compete on them while producing and consuming conformant vaults:

- how `summary`, `keywords`, `entities`, `relations`, `links` are generated (enrichment);
- how documents are turned into notes (ingest, splitting, deduplication);
- how notes are retrieved for a task (search, ranking, embeddings, context budgets);
- how composed documents are edited, paginated or printed (editors);
- how the vault is exposed to agents (MCP tools, APIs) or synchronised (git, mirrors);
- how the graph is visualised.

A vault produced by hand, with no tooling, can be fully conformant.

## 9. Host application profile: Obsidian

Obsidian is the reference host: its wikilink and embed resolution, tag syntax and frontmatter handling match §2 exactly. A vault MAY additionally use Obsidian features; they are **outside the format** and MUST NOT be required by any rule:

- Dataview queries, Bases (`.base`), Canvas, map plugins: views, not content. They SHOULD live inside notes so they are versioned with the vault.
- Callouts (`> [!tip]`): a vault MAY assign meaning to callout kinds; if so, the meaning is documented in the meta note.
- The `.obsidian/` folder is host state, not vault content; `workspace.json` SHOULD be excluded from version control.

Other hosts known to read the substrate (§2): Logseq, Foam, Dendron, Zettlr, and Markdown editors with wikilink extensions.

## 10. Conformance

A vault is **Mosaix 1.0 conformant** when a check over its files reports zero errors for:

| Check | Rule |
|---|---|
| Frontmatter present on every note outside `_inbox/`, `_private/` and declared payload folders | R2 |
| `title`, `updated`, `tags`, `summary`, `keywords`, `rev` present (canonical or aliased) | R2 |
| `summary` length 120–240 characters | R2 |
| `keywords` count 6–8 | R2 |
| `entities` present on ≥ 80 % of notes; each `type` in the allowed set | R2 |
| every wikilink and every `links` entry resolves | R3 |
| no orphan notes | R3 |
| at least one `type: moc` note | §3.4 |
| open-questions ledger and meta note exist | §5.3, §5.4 |
| every `type: document` note lists ≥ 2 `fragments`, all resolving | §6 |

and zero or more **warnings** for: tags not declared in the taxonomy, domain keys not declared, `rev` older than the body (stale metadata), notes without any reliability marker, more than 12 `entities` on a note that is not a MOC.

A reference checker, `audit_reference.py`, accompanies this specification. It uses only the Python standard library and produces the table above. Its output is the conformance report.

## 11. Versioning of this specification

Versions follow `MAJOR.MINOR.PATCH`. A MINOR version may add optional keys, note types or warnings; it never turns a conformant vault into a non-conformant one. A MAJOR version may. Vaults SHOULD state the version they target in their meta note (`mosaix: "1.0"`).

Under discussion for 1.1, not part of 1.0: a stable `id` key so links survive renames; a `question` key recording the single question a note answers; a mandatory closed relation vocabulary; an entity registry with aliases; `origin` (human · distilled · observed) and `as_of`, the date a fact was true.

## 12. Acknowledgements and provenance

The format was extracted from three vaults in production use (code documentation, industrial market intelligence, education marketing), by measuring which conventions each had invented and keeping the intersection that a machine could rely on. Those vaults used Italian key names; they are kept as default aliases so that they remain conformant unchanged. The two-axis reliability model, the open-questions ledger and the supersede-don't-delete rule come from the practice of working with several sources of different dates. The composed-document type comes from the observation that a vault of good atomic notes is unreadable by the people who need it most.

---

**Citing this specification.** Fiorino, A. (2026). *Mosaix Format — Specification v1.0.0*. Boom Digital. https://mosaixformat.org — source tag `mosaix-format/spec@v1.0.0`.

*Mosaix Format v1.0 — a format by SLIM — © 2026 Andrea Fiorino — CC BY-SA 4.0.*
