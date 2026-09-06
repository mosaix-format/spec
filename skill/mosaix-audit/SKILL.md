# Mosaix Audit — Skill for Claude

You are auditing a **Mosaix vault** — a folder of Markdown notes that follow the Mosaix Format v1.0. This skill teaches you how to verify conformance, interpret results, and fix common issues.

**Prerequisite.** You should already know the format: if `mosaix-format` is installed, its rules apply here. If not, read the spec at `_meta/` or at https://mosaixformat.org.

---

## 1. The reference checker

The checker is `audit_reference.py` — a single-file Python script, standard library only, read-only, offline.

```bash
# Basic check
python audit_reference.py /path/to/vault

# Verbose — shows every issue per note
python audit_reference.py /path/to/vault --verbose

# Check rev hashes (slower, computes body hashes)
python audit_reference.py /path/to/vault --check-rev

# Machine-readable output
python audit_reference.py /path/to/vault --json > report.json
```

Exit code 0 = conformant. Non-zero = errors found.

The checker looks for the script in these locations, in order:
1. The vault itself (root or `_meta/`)
2. A sibling `spec/` folder
3. The current working directory

If the checker is not available, you can still audit manually using the rules below.

## 2. What the checker verifies

### Errors (must fix for conformance)

| Check | Rule |
|---|---|
| Frontmatter present on every note outside `_inbox/`, `_private/`, and declared payload folders | R2 |
| `title`, `updated`, `tags`, `summary`, `keywords`, `rev` present (canonical or aliased) | R2 |
| `summary` length 120–240 characters | R2 |
| `keywords` count 6–8 | R2 |
| `entities` present on ≥80% of notes; each `type` in the allowed set | R2 |
| Every wikilink and every `links` entry resolves | R3 |
| No orphan notes (every note has at least one incoming link) | R3 |
| At least one `type: moc` note exists | §3.4 |
| Open-questions ledger and meta note exist | §5.3, §5.4 |
| Every `type: document` note lists ≥2 `fragments`, all resolving | §6 |

### Warnings (should fix, not blocking)

| Check | Meaning |
|---|---|
| Tags not declared in the taxonomy | R4 — add the tag to the meta note |
| Domain keys not declared | R4 — add the key to the meta note |
| `rev` older than the body (stale metadata) | Enrichment is out of date |
| Notes without any reliability marker (`status`) | No one knows if this is sourced or a guess |
| More than 12 `entities` on a non-MOC note | The note may answer more than one question (R1) |

## 3. Manual audit checklist

When the checker is not available, verify in this order:

1. **Meta note exists?** Look for `_meta/Conventions.md`, or `README.md` / `CLAUDE.md` at root. Must have `mosaix: "1.0"`.
2. **Open-questions ledger exists?** `_meta/Open questions.md` (or aliases: `Assunzioni da confermare.md`, `Domande aperte.md`).
3. **At least one MOC?** Search for `type: moc` in frontmatter.
4. **Sample 5–10 notes** outside `_inbox/` and `_private/`:
   - Frontmatter present with `---` delimiters?
   - All CORE keys present (canonical or aliased)?
   - `summary` between 120–240 chars?
   - `keywords` has 6–8 items?
   - `entities` present with valid types?
   - `links` entries resolve to real notes?
5. **Spot-check wikilinks** — follow 3–5 `[[links]]` and confirm the target exists.
6. **Check for orphans** — find notes that no other note links to. Every note needs at least one incoming link.

## 4. Common issues and fixes

### Missing CORE keys

**Symptom:** `ERROR: missing required key 'summary'`

**Fix:** Add the missing key. Don't invent content — if you can write a good summary from the body, do it. If not, add a placeholder and mark the note `status: to-confirm`.

```yaml
summary: "TO DO — summary needed."
```

This will fail the 120–240 char check, which is intentional: it stays visible as an error until someone writes a real summary.

### Summary too short or too long

**Symptom:** `ERROR: summary length 85 (expected 120–240)`

**Fix:** Rewrite. A good summary:
- Is one declarative sentence
- Does NOT repeat the title
- Does NOT start with "This note…"
- Tells a reader what they'll find without opening the note
- Is 120–240 characters

### Broken wikilinks

**Symptom:** `ERROR: broken link [[Note That Was Renamed]]`

**Fix:** Find the correct target note and update the link. If the target was deleted, that violates R7 (supersede, don't delete) — restore the note with `status: superseded` or update all incoming links to point to the replacement.

### Orphan notes

**Symptom:** `ERROR: orphan note — no incoming links: MyNote.md`

**Fix:** Find the MOC or parent note where this note belongs and add a `[[MyNote]]` link to it. Every note must be reachable from the graph.

### Undeclared tags

**Symptom:** `WARNING: tag 'newconcept' not declared in taxonomy`

**Fix:** Either:
- Add `newconcept` to the `tags` list in the meta note (if it's a real category), or
- Remove or rename the tag in the note (if it was a typo)

### Stale rev

**Symptom:** `WARNING: rev mismatch on MyNote.md (frontmatter: abc123, body: def456)`

**Fix:** The note's body changed after the last enrichment. Re-run enrichment on this note, or update `rev` to `000000000000` to acknowledge the metadata is stale.

### Entity type not in allowed set

**Symptom:** `ERROR: entity type 'department' not in allowed set`

**Fix:** Either:
- Add `department` to `entity_types` in the meta note (if it's a real type for this vault), or
- Change the entity's type to one of the 8 defaults: `person`, `company`, `product`, `project`, `tool`, `place`, `document`, `event`

## 5. Audit workflow

When asked to audit a vault:

1. **Run the checker** if available (always try `--verbose`)
2. **Read the report** — errors first, then warnings
3. **Group issues by type** — "12 notes missing summary" is one fix pattern, not 12 separate issues
4. **Propose fixes** as a batch — write to a branch or staging area (R8)
5. **Re-run the checker** after fixes to verify exit code 0
6. **Report** the before/after: how many errors, how many fixed, what remains

Never fix silently. Always show what you changed and why.

## 6. What this skill does NOT cover

- How to write conformant notes from scratch → use `mosaix-format`
- How to enrich notes with summary/keywords/entities → use `mosaix-enrich`
- How to set up a vault from zero → use `mosaix-onboard`

---

*Mosaix Format v1.0 — specification at https://mosaixformat.org — CC BY-SA 4.0*
