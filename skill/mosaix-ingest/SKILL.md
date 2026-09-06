# Mosaix Ingest — Skill for Claude

You are turning an external document into **atomic Mosaix notes**. This skill teaches you the principles of splitting and what a good result looks like. It does not prescribe a specific algorithm — different implementations may split differently and still produce conformant notes.

**Prerequisite.** You should already know the format: if `mosaix-format` is installed, its rules apply here.

---

## 1. The goal

A source document (PDF, Word, web page, transcript, email, spreadsheet) becomes a set of atomic notes where:

- Each note answers **one question** (R1)
- Each note is **self-describing** with full CORE frontmatter (R2)
- Each note is **connected** to at least one other note (R3)
- No content is **duplicated** — if two sources say the same thing, one note suffices (R5)

The output is a set of `.md` files ready to drop into a Mosaix vault.

## 2. Principles of splitting

### One concept per note

The atomic unit is **one question answered**. Not one paragraph, not one page, not one section. A 3-paragraph section that answers one question is one note. A 1-paragraph section that answers two questions is two notes.

Ask yourself: "If someone searched for this concept, would they want the rest of the section too?" If yes, keep together. If no, split.

### Preserve attribution

Every note produced from a source document should record where it came from:

```yaml
tags: [sourced]
status: sourced
```

The source itself should be identifiable — through the note's body, a frontmatter field, or a link to a document note.

### Don't interpret, transcribe

When splitting, your job is to **faithfully represent what the source says**, not to improve it. If the source contradicts another note in the vault, record both versions in the open-questions ledger (R6). If the source is ambiguous, mark the note `status: to-confirm`.

### Maintain context

An atomic note must make sense on its own. When you split a section, each resulting note needs enough context that a reader (human or machine) can understand it without reading the source. This usually means:

- A summary that stands alone (not "Continued from above")
- Entities that are named, not pronoun-referenced
- Links to related notes for background

### Handle tables and lists

A table of 50 rows about 50 different products is 50 notes (one per product), not one note with a big table. A table of 5 metrics about one product is one note.

The rule: does each row answer a different question? If yes, split by row. If no, keep the table.

### Handle hierarchical documents

A document with chapters, sections, and subsections maps naturally:

- **Chapter** → MOC note (type: `moc`) listing its sections
- **Section answering one question** → one atomic note
- **Section answering multiple questions** → multiple atomic notes, linked

The chapter MOC provides the reading order. A composed document (type: `document`) can reconstruct the original structure for reading.

## 3. The splitting workflow

### Step 1 — Read the source

Read the entire document first. Understand its structure, identify the key concepts, and note any contradictions or ambiguities.

### Step 2 — Identify the questions

List the distinct questions the document answers. Each becomes a candidate note. Typical patterns:

- "What is X?" → one note
- "How does X relate to Y?" → one note (with a relation in frontmatter)
- "What are the specifications of product Z?" → one note per product, or one note if they're tightly coupled
- "What happened at event E?" → one note
- "What did person P decide?" → one note

### Step 3 — Draft the notes

For each question, write a note with full CORE frontmatter. The body faithfully represents the source content relevant to that question.

### Step 4 — Connect the notes

- Link related notes with `[[wikilinks]]` in the body
- Ensure every note has at least one incoming link (R3)
- Create a MOC if the source document had clear structure
- Consider creating a composed document to preserve the original reading order

### Step 5 — Validate

For each note:

- [ ] Answers exactly one question (R1)
- [ ] Has full CORE frontmatter (R2)
- [ ] `summary` is 120–240 chars, standalone, does not start with "This note…"
- [ ] `keywords` has 6–8 items
- [ ] `entities` have valid types
- [ ] All `links` entries resolve
- [ ] Has at least one incoming link (R3)
- [ ] Content is not duplicated from an existing vault note (R5)

For the batch:

- [ ] At least one MOC or composed document ties the notes together
- [ ] No orphans
- [ ] Source is traceable (attribution)
- [ ] Contradictions with existing vault notes are logged in the open-questions ledger (R6)

## 4. What NOT to do

**Don't split mechanically by page or paragraph.** Pages are layout, not meaning. A concept that spans pages is one note.

**Don't create notes without context.** "Q3 results improved by 12%" is useless without knowing Q3 of what, when, and for whom. Add context.

**Don't resolve contradictions.** If the source says the price is €500 and the vault says €450, log both in the open-questions ledger. Don't pick one.

**Don't duplicate existing vault content.** If the vault already has a note about this concept, either link to it or update it (on a branch, R8). Don't create a second note saying the same thing.

**Don't discard information.** Every substantive claim in the source should land in a note. If something doesn't fit anywhere, create a note and tag it `to-confirm`.

**Don't write directly to main.** Ingested notes go to a branch or staging area for review (R8).

## 5. Example

Source: a 2-page product datasheet for "TerraCore 300"

Produces:

1. **TerraCore 300** — product note (what it is, key specs, applications)
2. **TerraCore 300 — technical specifications** — detailed specs table (if the table is large enough to warrant its own note)
3. **TerraCore 300 — certifications** — which standards it meets (if there are several with meaningful detail)

Or, if the datasheet is compact:

1. **TerraCore 300** — one note covering everything

The split point is whether each chunk answers a question someone would search for independently.

## 6. What this skill does NOT cover

- The format rules for writing notes → use `mosaix-format`
- How to validate the result → use `mosaix-audit`
- How to enrich notes with computed metadata → use `mosaix-enrich`
- The specific algorithm, model, or prompts used for automated splitting → that is an implementation (§8 of the spec)

---

*Mosaix Format v1.0 — specification at https://mosaixformat.org — CC BY-SA 4.0*
