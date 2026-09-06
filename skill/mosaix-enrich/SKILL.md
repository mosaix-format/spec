# Mosaix Enrich — Skill for Claude

You are enriching the frontmatter of notes in a **Mosaix vault** — filling in the CORE keys that make each note self-describing and machine-retrievable. This skill teaches you what good enrichment looks like and how to validate the result. It does not prescribe a specific model, prompt, or pipeline — those are implementations (§8 of the spec).

**Prerequisite.** You should already know the format: if `mosaix-format` is installed, its rules apply here.

---

## 1. What enrichment is

A note starts with a body written by a human. Enrichment fills in the CORE frontmatter keys that a human would write poorly or not at all:

- **`summary`** — a declarative sentence for readers who haven't opened the note
- **`keywords`** — search terms for people who don't know this note exists
- **`entities`** — named things cited in the body
- **`relations`** — typed links between those entities
- **`links`** — wikilink targets, mirroring the `[[links]]` in the body
- **`rev`** — hash of the body at the time of enrichment

`title`, `updated`, and `tags` are typically human-written and not part of automated enrichment, though they may be suggested.

## 2. Quality criteria for each key

### `summary`

A good summary:

- Is **one declarative sentence** (not two, not a fragment)
- Is **120–240 characters** long
- Does **not** repeat the title
- Does **not** start with "This note…", "This document…", or similar meta-references
- Tells a reader **what they'll find** without opening the note
- Is written for someone who has **not** seen the body

**Bad:** "This note describes TerraCore 300." (repeats title, meta-reference, too short)
**Bad:** "TerraCore 300." (fragment, too short, repeats title)
**Good:** "A compact soil sensor rated to IP68, designed for precision agriculture, greenhouse automation, and vineyard monitoring."

Test: cover the title and read only the summary. Does it make sense? Does it tell you what's inside?

### `keywords`

Good keywords:

- Are **6 to 8 items** (not fewer, not more)
- Are **lowercase strings**
- Include **synonyms**, **spoken phrasings**, and **questions** — how someone would search
- Do **not** duplicate tags
- Do **not** repeat the title verbatim

**Bad:** `[terracore, sensor, soil]` (too few, includes title word)
**Good:** `[compact soil sensor, ip68 soil probe, precision agriculture sensor, greenhouse soil monitor, vineyard moisture sensor, soil sensor for automation, what sensor for field moisture, wireless soil monitoring]`

Test: would someone type these into a search box when looking for this note?

### `entities`

Good entities:

- Are **named things** cited in the body (people, companies, products, etc.)
- Have a valid `type`: one of the 8 defaults (`person`, `company`, `product`, `project`, `tool`, `place`, `document`, `event`) or a custom type declared in the meta note
- Have **at most 12 items** per note (more suggests the note isn't atomic)
- Use the entity's **proper name**, not a description

**Bad:** `{name: "the main competitor", type: company}` (description, not a name)
**Good:** `{name: "Grünfeld AG", type: company}`

### `relations`

Good relations:

- Connect entities **named in `entities`**
- Use a **present-tense verb phrase** as the type (`owns`, `supplies`, `depends on`, `competes with`)
- Represent a relationship **stated or clearly implied** in the body — not inferred from general knowledge

**Bad:** `{from: Grünfeld AG, type: is, to: competitor}` (vague type, "competitor" isn't an entity)
**Good:** `{from: Grünfeld AG, type: competes with, to: Nakamura Corp}` (both are named entities, verb is specific)

If the vault's meta note declares a closed `relation_types` vocabulary, use only those types.

### `links`

- Must include every `[[wikilink]]` target from the body
- Every entry must resolve to an existing note in the vault
- If a wikilink target doesn't exist, either create the target note or remove the link

### `rev`

- A 12-character hex string that is the hash of the body at the time enrichment ran
- Write `000000000000` as a placeholder when enriching by hand
- A mismatch between `rev` and the current body hash means the enrichment is stale

## 3. Enrichment workflow

### Step 1 — Read the meta note

Before enriching any note, read the vault's meta note to learn:
- Custom entity types
- Custom relation types (if closed vocabulary)
- Domain keys
- Aliases
- Tag taxonomy

### Step 2 — Read the note's body

Read the full body. Enrichment is based on what the body says, not on external knowledge.

### Step 3 — Write each key

Fill in `summary`, `keywords`, `entities`, `relations`, `links` following the quality criteria above.

### Step 4 — Validate

For each enriched note:

- [ ] `summary` is 120–240 chars
- [ ] `summary` does not repeat the title
- [ ] `summary` does not start with "This note…"
- [ ] `summary` is one sentence
- [ ] `keywords` has 6–8 items, lowercase
- [ ] `keywords` does not duplicate any tag
- [ ] `entities` has ≤12 items
- [ ] Each entity `type` is in the allowed set (defaults + meta note customs)
- [ ] Each entity `name` is a proper name from the body
- [ ] Each relation uses entities from the `entities` list
- [ ] Each relation `type` is a present-tense verb phrase
- [ ] `links` includes all `[[wikilink]]` targets
- [ ] All `links` entries resolve
- [ ] `rev` is set (placeholder or computed)

### Step 5 — Propose, don't apply

Write enriched notes to a branch or staging area (R8). Never write directly to the vault's main line.

## 4. Batch enrichment

When enriching multiple notes:

1. Read the meta note **once** at the start
2. Process notes in any order — enrichment of each note is independent
3. After the batch, run the checker to catch cross-note issues (broken links, orphans)
4. Notes with `rev: 000000000000` or stale `rev` are candidates for (re-)enrichment

## 5. What NOT to do

**Don't invent entities.** Only extract entities named in the body. If the body mentions "a large German manufacturer" without naming it, don't guess who it is.

**Don't add relations from general knowledge.** If the body says "Grünfeld AG operates in Bavaria", you can add that relation. If you happen to know they also operate in Saxony but the body doesn't say so, don't add it.

**Don't write summaries that require the title to make sense.** "It is rated to IP68" fails without the title. "A compact soil sensor rated to IP68 for precision agriculture" stands alone.

**Don't optimise keywords for SEO.** Keywords are for vault-internal search — how a colleague would look for this note. Not for Google.

**Don't change the body.** Enrichment fills frontmatter. The body stays untouched. If the body has errors, that's a separate edit.

## 6. What this skill does NOT cover

- The format rules → use `mosaix-format`
- How to validate the result systematically → use `mosaix-audit`
- How to turn documents into notes before enriching → use `mosaix-ingest`
- Which model, prompts, or pipeline to use for automated enrichment → that is an implementation (§8 of the spec), and different implementations compete on quality
- The cost structure of enrichment → implementation-specific

---

*Mosaix Format v1.0 — specification at https://mosaixformat.org — CC BY-SA 4.0*
