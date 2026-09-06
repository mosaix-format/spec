# Mosaix Compose — Skill for Claude

You are assembling a **composed document** from atomic notes in a Mosaix vault. This skill teaches you how to build a document that joins notes without duplicating them.

**Prerequisite.** You should already know the format: if `mosaix-format` is installed, its rules apply here.

---

## 1. What a composed document is

A composed document is a note with `type: document`. It is a **view over other notes** — it does not contain the content itself. The atomic notes stay separate; the document defines the reading order and presentation.

This is rule R5: **composition over duplication**. Content that must be read together is joined with a composed document, never copied.

## 2. Required frontmatter

```yaml
---
title: Market Entry Brief — Organic Tea, Southeast Asia
updated: 2026-09-03
type: document
tags: [document, market, tea]
summary: "Board reading that assembles the organic tea market landscape, key competitor profiles, and strategic scenarios into one document."
keywords: [organic tea market entry, southeast asia tea report, competitor analysis tea, board reading market brief, tea sourcing strategy, market entry document]
entities:
  - {name: Organic Tea SE Asia, type: project}
fragments: [Tea market consolidation 2025, Liang Brothers — player card, Strategic scenarios]
pool: [Tea trade fairs Asia 2026]
layout:
  cover: {title: Market entry brief — Organic Tea, SE Asia, subtitle: Board reading, date: 2026-09-03}
  page: A4
  sections:
    - {title: Market, fragments: [Tea market consolidation 2025, Liang Brothers — player card]}
    - {title: Recommendation, fragments: [Strategic scenarios]}
  show: [summary, status]
relations: []
links: [Tea market consolidation 2025, Liang Brothers — player card, Strategic scenarios, Tea trade fairs Asia 2026]
rev: 000000000000
---
```

### Key-by-key

- **`type: document`** — marks this as a composed document.
- **`fragments`** — ordered list of note titles that make up the document, in reading order. Must have ≥2 entries. Every entry must resolve to an existing note.
- **`pool`** — (optional) notes that were considered but not included. Useful for audit trails: why was this left out?
- **`layout`** — (optional) presentation hints. Free-form map; tools ignore keys they don't understand. Common keys:
  - `cover` — title, subtitle, date for a cover page
  - `page` — page format (A4, Letter, etc.)
  - `sections` — groups of fragments under section headings
  - `show` — which frontmatter keys from each fragment to display (e.g. `[summary, status]`)
- **`links`** — must include all fragment and pool note titles (they are outbound links).

## 3. The body

The body of a composed document MAY contain:

- **Narrative** connecting the fragments — transitions, context, editorial commentary
- **Embeds** using `![[Note title]]` to include fragment content inline
- **Section headers** organising the reading flow

Example body:

```markdown
## Market landscape

The Southeast Asian organic tea market is consolidating rapidly. The following analysis covers the last 18 months.

![[Tea market consolidation 2025]]

## Key competitor

![[Liang Brothers — player card]]

## Strategic recommendation

Given the consolidation trend and Liang Brothers' positioning:

![[Strategic scenarios]]
```

The rule: **an edit belongs to the fragment, not to the document.** If you need to change what a section says, change the underlying atomic note. The document only controls order and framing.

## 4. How to build a composed document

### Step 1 — Identify the question

What does the reader need to understand after reading this document? Write it down — it becomes your compass for selecting fragments.

### Step 2 — Select fragments

Search the vault for notes that answer parts of the question. Use:
- `entities` to find notes about specific things
- `tags` to find notes in a topic area
- `links` to trace dependencies
- `summary` to scan without opening

Each fragment must be an atomic note that stands on its own (R1). If a fragment is too large or answers multiple questions, it should be split first.

### Step 3 — Order them

Put fragments in the order a reader needs them. Typically:
- Context before detail
- Problem before solution
- Evidence before conclusion

### Step 4 — Decide what's in the pool

Notes you considered but excluded go in `pool`. This is documentation: it answers "why isn't X in this document?" without anyone having to ask.

### Step 5 — Write the layout

If the document will be rendered (PDF, slides, print), add `layout` hints. If it's just a reading order, `fragments` alone is enough.

### Step 6 — Write the body

Add narrative glue between embeds. Keep it short — the fragments carry the content. The body provides:
- Transitions ("Given the market data above, we now look at competitors")
- Framing ("This section focuses on the European market only")
- Editorial commentary ("The gap between Liang Brothers and the next player is notable")

### Step 7 — Validate

- [ ] `type: document` is set
- [ ] `fragments` has ≥2 entries
- [ ] Every fragment resolves to an existing note
- [ ] Every fragment and pool entry is in `links`
- [ ] No content is duplicated — the document embeds, it doesn't copy
- [ ] The document has all CORE frontmatter keys
- [ ] The body does not modify fragment content (edits go to the fragment)

## 5. Updating a composed document

When a fragment changes, the document automatically reflects the change (since it embeds, not copies). You only need to update the document when:

- The reading order changes → update `fragments`
- A fragment is added or removed → update `fragments`, `pool`, `links`
- The narrative needs adjustment → edit the body
- The layout changes → update `layout`

## 6. Common mistakes

**Copying content instead of embedding.** If you find yourself pasting text from a note into the document body, stop. Embed it with `![[Note]]` instead.

**Fragments that aren't atomic.** If a fragment answers three questions, the composed document inherits that mess. Split the fragment first.

**Missing pool.** If you evaluated 10 notes and included 5, the other 5 should be in `pool`. Six months from now someone will ask why they're missing.

**Editing the document instead of the fragment.** The document is the view. If the content is wrong, fix the source note.

## 7. What this skill does NOT cover

- How to write atomic notes → use `mosaix-format`
- How to render a composed document as PDF or slides → that is an implementation (§8 of the spec)
- How to split a large note into atomic fragments → use `mosaix-ingest`

---

*Mosaix Format v1.0 — specification at https://mosaixformat.org — CC BY-SA 4.0*
