# Mosaix Onboard — Skill for Claude

You are setting up a new **Mosaix vault** from scratch. This skill walks you through bootstrapping the structure so the vault is conformant from the first note.

**Prerequisite.** You should already know the format: if `mosaix-format` is installed, its rules apply here.

---

## 1. What you need before starting

Three pieces of information from the vault owner:

1. **Domain** — what is this vault about? (a client, a product, a market, a course)
2. **Folder structure** — how do they want to organise notes? (by topic, by phase, by entity)
3. **Custom types and tags** — any domain-specific entity types, relation types, or tags beyond the defaults?

If the owner doesn't know yet, start with a minimal structure and expand later. The format is designed for that.

## 2. Create the folder structure

Every Mosaix vault has three reserved folders:

```
vault/
├── _meta/              # governance: meta note, taxonomy, open questions
├── _synthesis/          # synthesis notes (condensed views of areas)
├── _inbox/              # unprocessed material, not checked for conformance
└── [domain folders]/    # whatever the owner needs
```

Optional:
- `_private/` — personal notes, excluded from version control (add to `.gitignore`)

Domain folders are free. Examples:

```
# For a client vault
01-Company/
02-Market/
03-Competitors/
04-Strategy/

# For a product vault
architecture/
features/
decisions/
integrations/

# For a course
modules/
students/
materials/
```

## 3. Create the meta note

This is the most important file in the vault. It declares the conventions everything else follows.

Create `_meta/Conventions.md`:

```yaml
---
title: Conventions
updated: YYYY-MM-DD
mosaix: "1.0"
type: meta
tags: [meta]
summary: "Declares the conventions, taxonomy, and structure of this vault."
keywords: [vault conventions, taxonomy, meta note, vault structure, domain keys, entity types]
entities: []
relations: []
links: []
rev: 000000000000
folders:
  01-Company: "who they are, history, structure"
  02-Market: "where they sell, segments, trends"
  03-Competitors: "player cards, positioning"
reliability:
  key: status
  values: [sourced, to-confirm, superseded]
tags: [meta, moc, player, market, strategy, product]
domain_keys: {}
aliases: {}
entity_types: []
relation_types: []
payload: []
maintainers:
  - {name: Owner Name, area: all}
---

# Conventions

This vault follows **Mosaix Format v1.0**. Every note is atomic (one question, one note), self-describing (CORE frontmatter), and connected (no orphans, no broken links).

## Reliability

- `sourced` — from a document, system, or working conversation; source named
- `to-confirm` — hypothesis, draft, or placeholder; not yet validated
- `superseded` — no longer valid; kept in place, other notes link to it

## Folders

| Folder | Contents |
|---|---|
| `_meta/` | This note, the open questions ledger, taxonomy |
| `_synthesis/` | Condensed views of areas |
| `_inbox/` | Unprocessed material |
| `01-Company/` | Who they are |
| ... | ... |

## Tags

All tags used in this vault are declared here: `meta`, `moc`, `player`, `market`, `strategy`, `product`.

To add a new tag, add it to this list first (R4).

## Entity types

The 8 default types apply: `person`, `company`, `product`, `project`, `tool`, `place`, `document`, `event`.

Custom types for this vault: *(none yet — add here when needed)*.

## Domain keys

*(none yet — add here when needed)*
```

### Customising the meta note

- **`folders`** — describe each folder in the vault. Add or remove as needed.
- **`tags`** — declare every tag that notes may use. Start small, expand as the vault grows.
- **`domain_keys`** — vault-specific frontmatter keys (e.g., `client: string`, `country: ISO-3166 alpha-2`). Leave empty if none.
- **`entity_types`** — custom types beyond the 8 defaults (e.g., `department`, `regulation`). Leave empty if the defaults suffice.
- **`relation_types`** — optional closed vocabulary for relation types (e.g., `owns`, `supplies`, `depends on`). Leave empty for open vocabulary.
- **`aliases`** — custom key aliases beyond the Italian defaults. Leave empty if none.
- **`payload`** — folders excluded from conformance checks (e.g., `exports/`, `assets/`).
- **`maintainers`** — who is responsible for what area.

## 4. Create the open-questions ledger

Create `_meta/Open questions.md`:

```yaml
---
title: Open questions
updated: YYYY-MM-DD
type: meta
tags: [meta]
summary: "Registry of unresolved questions, contradictions, and assumptions that need confirmation."
keywords: [open questions, contradictions, assumptions, unresolved, to confirm, pending decisions, knowledge gaps]
entities: []
relations: []
links: [Conventions]
rev: 000000000000
---

# Open questions

This ledger records what is unknown, contradictory, or assumed. Each entry states the question, the competing versions (with dates and sources), the practical consequence, and who resolves it.

When you find a contradiction between notes, add it here — don't pick a winner silently (R6).

## Template

### [Question title]

- **Version A:** [claim] — source: [where], date: [when]
- **Version B:** [claim] — source: [where], date: [when]
- **Consequence:** [what changes depending on which is true]
- **Resolves:** [who decides]
- **Status:** open / resolved ([date], chose [version], because [reason])

---

*(No open questions yet.)*
```

## 5. Create the first MOC

Every vault must have at least one `type: moc` note (§3.4). Create a Home MOC:

```yaml
---
title: Home
updated: YYYY-MM-DD
type: moc
tags: [moc]
summary: "Entry point to the vault — links to every area and its key notes."
keywords: [home, index, entry point, vault map, navigation, table of contents, starting point]
entities: []
relations: []
links: [Conventions, Open questions]
rev: 000000000000
---

# Home

Welcome to the **[Domain Name]** vault.

## Structure

- [[Conventions]] — how this vault works
- [[Open questions]] — what we don't know yet

## Areas

*(Add links to area MOCs or key notes as the vault grows.)*
```

## 6. First real note

Now write the vault's first content note. Use the full CORE frontmatter:

```yaml
---
title: [Note title]
updated: YYYY-MM-DD
tags: [topic-tag]
summary: "[One sentence, 120–240 chars, about what this note contains.]"
keywords: [6 to 8 lowercase search terms]
entities:
  - {name: Something, type: company}
relations:
  - {from: Something, type: operates in, to: Some Market}
links: [Home]
rev: 000000000000
---

# [Note title]

[Body — answers one question.]
```

Then update the Home MOC to link to this note.

## 7. Bootstrap checklist

- [ ] `_meta/` folder exists
- [ ] `_meta/Conventions.md` exists with `mosaix: "1.0"`, folders, tags, entity types
- [ ] `_meta/Open questions.md` exists
- [ ] `_synthesis/` folder exists (can be empty)
- [ ] `_inbox/` folder exists (can be empty)
- [ ] At least one `type: moc` note exists (Home)
- [ ] Home links to Conventions and Open questions
- [ ] Domain folders created per the owner's structure
- [ ] `.gitignore` excludes `_private/` and `.obsidian/` if using git
- [ ] First content note written and linked from Home
- [ ] Run the checker: `python audit_reference.py /path/to/vault`

## 8. What this skill does NOT cover

- How to write conformant notes → use `mosaix-format`
- How to verify the vault is healthy → use `mosaix-audit`
- How to import existing documents into the vault → use `mosaix-ingest`

---

*Mosaix Format v1.0 — specification at https://mosaixformat.org — CC BY-SA 4.0*
