# obsidian-mosaix — Functional Specification

**Version:** 1.0-draft  
**Updated:** 2026-09-08  
**Author:** Andrea Fiorino  
**License:** MIT (plugin code) · CC BY-SA 4.0 (documentation, aligned with Mosaix Format spec)  
**Target spec:** Mosaix Format v1.0.0  
**Minimum Obsidian:** v1.4 (requires `app.metadataCache` APIs introduced in that release)

---

## 0. Purpose

`obsidian-mosaix` is an Obsidian community plugin that integrates the Mosaix Format (v1.0) directly into the editor. It gives a vault author:

1. **live conformance feedback** without leaving the editor (F1);
2. **scaffolding commands** to create well-formed notes from the start (F2);
3. **visual cues in the graph view** for supersession, contradictions, and orphans (F3);
4. **a status bar badge** summarising the health of the current note (F4);
5. **a sidebar panel** with per-note diagnostics and vault-level health (F5);
6. **configurable settings** (F6).

The plugin is read-only with respect to the vault's *body*: it never modifies the Markdown content of a note. It modifies frontmatter only on explicit user action (F2 commands).

---

## 1. Authoritative references

| Document | Role |
|---|---|
| `Mosaix-Format-v1.0.en.md` (spec root) | Normative. Defines keys, rules, conformance. |
| `spec.yaml` | Machine-readable rule table. The plugin reads error codes, messages, and constraints from here when the file is present in the vault or adjacent directory. |
| Obsidian Plugin API v1.x | All plugin APIs must be in the stable, documented surface. No internal or undocumented APIs. |

---

## 2. Architecture constraints

- **Language:** TypeScript, compiled to a single `main.js` (standard Obsidian plugin layout).
- **No external dependencies** beyond the Obsidian API and the TypeScript standard library. All utilities (ULID generation, YAML parsing fallback) are implemented inline.
- **YAML parsing strategy:** use `app.metadataCache.getFileCache(file).frontmatter` as the primary source for all CORE keys Obsidian exposes. Fall back to direct string parsing only for fields Obsidian does not expose (e.g., structured values inside `entities`, `relations`).
- **ULID generation:** inline implementation (~20 lines TypeScript). Generates a random ULID using `crypto.getRandomValues` (available in both Obsidian desktop and mobile). Does not use any npm package.
- **Platforms:** must work on Obsidian desktop (Windows, macOS, Linux) and mobile (iOS, Android). No Node.js–only APIs in the validation hot path.
- **Testability:** the validation engine (`src/validator/`) must be a pure TypeScript module with no Obsidian imports, so it can be unit-tested with a standard test runner (Vitest or Jest) using the conformance test corpus.

---

## 3. Feature F1 — Lint inline (live validation)

### 3.1 Scope

F1 validates a single note against §10 of the Mosaix Format spec. The check is *local*: it does not require scanning the whole vault. Checks that need vault-wide data (E006 broken wikilinks, E007 orphans, E008/E009 broken `links`, E012–E015) are vault-level checks and are handled separately (§3.4).

### 3.2 Checks performed per note (note-level)

| Error / Warning | id | Trigger condition |
|---|---|---|
| No frontmatter | E001 | YAML block absent |
| Missing required key | E002 | any of `updated`, `tags`, `summary`, `keywords`, `rev` absent (canonical or aliased) |
| Summary length | E003 | `summary` outside 120–240 chars |
| Keywords count | E004 | `keywords` list has < 6 or > 8 items |
| Entity type not allowed | E005 | `entities[n].type` not in built-in set and not declared in meta note |
| Too many entities | W001 | non-MOC note has > 12 entities |
| Relation type undeclared | W002 | relation type not in `relation_types` vocabulary (only when vocabulary is declared) |
| Missing id | W003 | `id` key absent |
| Invalid id | W004 | `id` present but not a valid ULID (`^[0-7][0-9A-HJKMNP-TV-Z]{25}$`) |
| Tag undeclared | W005 | any `tags` value absent from meta note taxonomy |
| No reliability marker | W007 | note has no `status` key, `#status/...` tag, or inline axis symbol |
| Stale rev | W008 | `rev` is present but does not equal `sha256(body)[:12]` |
| Summary repeats title | — | `summary` equals or begins with the `title` value |
| Summary bad start | — | `summary` starts with "This note" or "Questa nota" |
| keywords overlap tags | — | any keyword also appears in `tags` |

Alias resolution (§3.1 of spec, `aliases` section of `spec.yaml`) is applied before all checks: Italian keys and legacy key names are normalised to their canonical forms.

### 3.3 Trigger

- **On save** (default): debounced 500 ms after the last keystroke that triggers a save, or immediately on explicit `Cmd/Ctrl+S`. The 500 ms delay prevents re-running on every character while auto-save is active.
- **On demand**: via the command `Mosaix: Validate this note` (registered in the Obsidian command palette).
- **Manual only**: if `Auto-validate` is set to `manual only` in settings (F6), the save trigger is disabled; the command still works.

### 3.4 Vault-level checks (E012–E015 + E006/E007/E008/E009)

These checks require iterating over vault files and are expensive.

- **Periodic**: run every 5 minutes in the background when Obsidian is open, unless `Auto-validate` is set to `manual only`.
- **On demand**: via the command `Mosaix: Validate vault`.
- **Async**: vault-level checks run on a background microtask (`Promise`-based); they must not block the editor event loop.
- Results are stored in plugin memory and used by F4 and F5 until the next run.

### 3.5 Gutter markers

- **Error marker** (red): displayed in the Obsidian editor gutter beside the frontmatter line that contains the offending key (or beside the opening `---` for E001).
- **Warning marker** (yellow/amber): same position, lower severity.
- Markers are rendered using the Obsidian `EditorSuggest` / `MarkdownPostProcessor` or the CodeMirror 6 gutter extension exposed through the Obsidian CM6 API, whichever is stable at the target API version.
- One marker per line; if multiple issues map to the same line, show the highest-severity marker and aggregate the messages in the hover tooltip.

### 3.6 Hover tooltip

Hovering over a gutter marker shows a tooltip containing:

- The error/warning id (e.g. `E003`)
- The full message, interpolated (e.g. `summary length 87 (120–240)`)
- A brief one-line explanation of the rule (drawn from `spec.yaml` `description` field if loaded; hardcoded fallback)

### 3.7 Performance budget

- Note-level validation must complete in < 50 ms on a note with ≤ 500 frontmatter lines.
- Vault-level scan must not block the editor. It runs asynchronously; progress is visible in the sidebar (F5).

---

## 4. Feature F2 — Scaffolding

### 4.1 Command: "Mosaix: New note"

Creates a new Obsidian note pre-populated with all CORE keys.

**Flow:**

1. Opens a modal dialog with a single text input: **Title**.
2. On confirmation, creates a new `.md` file in the currently active folder (or vault root if no folder is selected) with the filename `<title>.md`.
3. The file is created with the following frontmatter, in canonical key order:

```yaml
---
title: <title from modal>
id: <ULID generated at creation time>
updated: <today YYYY-MM-DD>
tags: []
summary: ""
keywords: []
entities: []
relations: []
links: []
rev: ""
---
```

4. The file is opened in the active pane.
5. The cursor is placed on the `tags: []` line (first empty field requiring user input).
6. `rev` is left empty at creation; it is computed and filled in after the first save that contains body content (see §4.3).

**Constraints:**

- If a note with the same filename already exists in the target folder, the modal shows an inline error and does not create the file.
- Title validation: must be non-empty; Obsidian-illegal characters (`\ / : * ? " < > |`) are rejected with an inline error.

### 4.2 Command: "Mosaix: Mosaix-ify this note"

Adds missing CORE keys to an already-existing note, without touching keys that are already present or modifying the body.

**Flow:**

1. Reads the current note's frontmatter via `app.metadataCache.getFileCache`.
2. For each CORE key that is absent (canonical or aliased):
   - `id`: generate a new ULID and add it.
   - `updated`: add today's date.
   - `title`: add the note's basename without extension.
   - `tags`, `keywords`, `entities`, `relations`, `links`: add as empty list `[]`.
   - `summary`: add as empty string `""`.
   - `rev`: add as empty string `""` (will be computed on next save).
3. Keys already present (under any recognised alias) are left untouched.
4. If the Italian-alias option is enabled in settings (F6) and the note has Italian key names (`aggiornato`, `riassunto`, etc.), the command offers a confirmation dialog: *"Convert Italian key names to canonical English names? This does not change their values."* The conversion is applied only if the user confirms.
5. The frontmatter is written back following canonical key order (§3.1 of spec). Keys not recognised by the spec are preserved in their original position after the CORE block.
6. **The body is never modified.** The operation is byte-identical on the body content.

**Constraints:**

- Only available when a note is open in the active editor pane.
- The command is a no-op (with a notice: "This note already has all CORE keys") if all CORE keys are present.

### 4.3 rev computation

`rev` = `sha256(body)[:12]` where `body` is the note content below the closing `---` of the frontmatter, with leading/trailing whitespace stripped.

- Computed and written into frontmatter on save, if `entities`, `relations`, or `links` are non-empty and `rev` is empty or stale.
- Computation is triggered only when the user saves explicitly (not on auto-save intervals shorter than 30 s), to avoid excessive writes.
- If the body is empty, `rev` is set to the 12-char hex of `sha256("")`.

---

## 5. Feature F3 — Graph enhancements

Graph enhancements use the Obsidian graph view extension APIs where available. Where the stable API does not permit a specific visual, the feature degrades gracefully (the enhancement is silently skipped, and the setting remains visible but shows a note: *"Requires Obsidian graph API"*).

### 5.1 Supersession arcs (R7)

- Notes with `status: superseded` (or alias `superato`) are visually connected to their replacement note with a directed arc coloured **orange**.
- Replacement detection: the plugin looks for a wikilink from the superseded note's body to another note (heuristic: the most recently `updated` note that the superseded note links to is treated as its replacement). If no such link is found, no arc is drawn.
- Direction: **superseded note → replacement note**.
- The arc is drawn in addition to the normal graph edge, not instead of it.

### 5.2 Contradiction badge (R6)

- Notes that have a wikilink to `_meta/Open questions.md` (or accepted aliases: `Assunzioni da confermare.md`, `Domande aperte.md`) are marked with a **⚠️ badge** on their graph node.
- Alternative detection: if the note's body contains the word "contradiction" or "contraddizione" (case-insensitive), the badge is shown.
- Both conditions are OR: either one triggers the badge.

### 5.3 Orphan highlight

- Notes with no incoming wikilinks (E007) are rendered with a **dashed red border** on their graph node.
- This is the graph-view counterpart of the E007 gutter marker.

### 5.4 Filter by type

- A filter control in the graph panel allows showing only notes with a specific `type` value.
- Supported filter values: `moc`, `synthesis`, `document`, and a catch-all *"untyped"* for notes with no `type` key.
- The filter is additive: selecting multiple values shows the union.
- Implemented via the Obsidian graph filter API if available; otherwise via the node CSS class injection approach (applies colour only, not hiding).

---

## 6. Feature F4 — Status bar

A permanent badge in the Obsidian status bar (right side).

### 6.1 States

| Display | Condition |
|---|---|
| `Mosaix ✓` (green text) | Current note: 0 errors, 0 warnings |
| `Mosaix ⚠ N` (amber text) | Current note: 0 errors, N warnings (N ≥ 1) |
| `Mosaix ✗ N` (red text) | Current note: N errors (N ≥ 1) |
| `Mosaix —` (grey text) | Current pane has no note (canvas, settings, etc.) |

- The badge updates each time the active leaf changes and each time validation completes for the active note.
- Error count takes precedence over warning count: if there are both errors and warnings, show the error state.

### 6.2 Interaction

- **Click**: opens the sidebar panel (F5) focused on the *Errors & warnings* section for the current note.
- **Tooltip** (hover): shows a one-line summary, e.g. `"3 errors, 1 warning — click to open Mosaix panel"`.

---

## 7. Feature F5 — Sidebar panel

A dedicated Obsidian `ItemView` registered as a leaf (right sidebar by default). Activated via the status bar badge click (F4) or the command `Mosaix: Open panel`.

### 7.1 Sections

The panel is divided into collapsible sections. All data reflects the current active note except the *Vault health* section.

#### 7.1.1 Errors and warnings

- List of all issues found by F1 for the current note.
- Each row: `[id] message` — clicking a row scrolls the editor to the relevant frontmatter line.
- Empty state: *"No issues found."*

#### 7.1.2 Supersession chain

- Predecessors: notes that link to this note with `status: superseded` (notes this note replaces).
- Successors: notes that this note links to which have `status: superseded` (notes this note was superseded by).
- Each entry is a clickable link that opens the target note.
- Empty state if the note is not part of any supersession chain.

#### 7.1.3 Contradictions

- List of wikilinks from the open-questions ledger that reference this note (by title or `id`).
- Each entry shows the ledger entry title or excerpt and links to the ledger note.
- Empty state: *"No recorded contradictions."*

#### 7.1.4 Composed documents

- List of notes with `type: document` that include this note in their `fragments` list.
- Each entry links to the document note.
- Empty state: *"Not included in any composed document."*

#### 7.1.5 Vault health

Updated on each vault-level scan (§3.4). Shows:

| Metric | Description |
|---|---|
| Total notes | Count of `.md` files outside `_inbox/`, `_private/`, payload folders |
| Errors | Count of vault-level errors (all E-codes) |
| Warnings | Count of vault-level warnings (all W-codes) |
| Orphans | Count of notes with no incoming link (E007) |
| Entities coverage | `N/Total = X%` (E015 threshold is 80%) |
| Last scan | Timestamp of last vault scan |
| Status | `Scanning…` while a scan is in progress; idle otherwise |

---

## 8. Feature F6 — Settings

Registered as a standard Obsidian plugin settings tab.

| Setting | Type | Default | Description |
|---|---|---|---|
| **Auto-validate** | radio | `on save` | `on save` triggers F1 on every save (debounced 500 ms). `manual only` disables auto-trigger; validation runs only via command. |
| **Severity filter** | checkbox group | errors + warnings | Controls which severity levels show gutter markers and count toward the status bar. Options: `errors`, `warnings`. Both selected = show all. |
| **Italian aliases** | toggle | off | When on, "Mosaix-ify" automatically renames Italian key names to canonical English names (with confirmation dialog). When off, Italian keys are recognised but not renamed. |
| **spec.yaml path** | text | *(auto-detect)* | Path to `spec.yaml` relative to vault root. Leave empty to auto-detect (looks for `spec.yaml` in vault root, then in the directory containing the meta note). When found, error messages are loaded from this file; when absent, messages are hardcoded from the v1.0.0 spec. |
| **Graph enhancements** | toggle | on | Enable/disable all F3 graph enhancements. |
| **Vault scan interval** | number (minutes) | 5 | How often the background vault-level scan runs. Minimum: 1. Set to 0 to disable periodic scans. |

---

## 9. Commands registered

All commands appear in the Obsidian command palette under the prefix `Mosaix:`.

| Command id | Name | Context |
|---|---|---|
| `mosaix:new-note` | New note | Global |
| `mosaix:mosaix-ify` | Mosaix-ify this note | Requires active Markdown note |
| `mosaix:validate-note` | Validate this note | Requires active Markdown note |
| `mosaix:validate-vault` | Validate vault | Global |
| `mosaix:open-panel` | Open panel | Global |

---

## 10. Validation engine (standalone module)

The validation logic lives in `src/validator/` and has **no imports from the Obsidian API**. Its public interface:

```typescript
// src/validator/types.ts
export interface NoteData {
  relativePath: string;
  frontmatter: Record<string, unknown>;
  body: string;           // content below the closing --- delimiter
  rev: string | undefined;
}

export interface Finding {
  code: string;           // e.g. "E003"
  severity: "error" | "warning";
  message: string;        // interpolated message
  key?: string;           // frontmatter key that triggered it, if applicable
}

// src/validator/noteValidator.ts
export function validateNote(
  note: NoteData,
  options: ValidatorOptions,
): Finding[];

// src/validator/vaultValidator.ts
export function validateVault(
  notes: NoteData[],
  options: ValidatorOptions,
): Map<string, Finding[]>;   // keyed by relativePath
```

`ValidatorOptions` carries the alias table, entity types, relation types vocabulary, and meta note data — all read from the vault's meta note and/or `spec.yaml` at startup.

The module must be importable by the conformance test suite (in `tests/`) without mocking any Obsidian globals.

---

## 11. ULID generation

Inline implementation with no dependencies. Contract:

- Uses `crypto.getRandomValues(new Uint8Array(10))` for the random component.
- Uses `Date.now()` for the 48-bit timestamp component.
- Encodes using the Crockford Base32 alphabet: `0123456789ABCDEFGHJKMNPQRSTVWXYZ`.
- First character is always in `0–7` (timestamp MSB constraint).
- Each call returns a distinct value; never re-uses or derives from file content.
- Total length: exactly 26 characters.

---

## 12. Out of scope (v1)

The following are **explicitly deferred** and must not be implemented in v1, even partially:

- **Enrichment**: automatic generation of `summary`, `keywords`, `entities`, `relations` (requires an LLM integration).
- **MCP integration**: connecting to the Mosaix reference MCP server.
- **Git sync**: automatic commits or branch creation.
- **Composed document rendering**: inline preview of assembled fragments.
- **Vault export/import**: bulk operations.
- **Multi-vault**: managing more than one vault simultaneously.

---

## 13. Development milestones

| Milestone | Features | Deliverable |
|---|---|---|
| **M1 — MVP** | F2 (scaffolding) + F6 (settings) | Plugin installable; notes can be created and Mosaix-ified; settings panel works. |
| **M2 — Validation** | F1 (lint) + F4 (status bar) | Gutter markers and status badge active; note-level and vault-level checks running. |
| **M3 — Sidebar** | F5 (panel) | Full per-note diagnostics and vault health dashboard. |
| **M4 — Graph** | F3 (graph enhancements) | Supersession arcs, contradiction badges, orphan highlights, type filter. |

M1 should be testable without a running Obsidian instance for the validator module. M4 is the most Obsidian-API-dependent milestone and should be developed last, when the stable graph extension API surface is confirmed.

---

## 14. Repository and publication

- **Repository:** separate repo from the Mosaix Format spec (`obsidian-mosaix`, not `mosaix-format`). The spec repo is a dependency, not a submodule.
- **Plugin manifest:** standard Obsidian `manifest.json` with `minAppVersion: "1.4.0"`.
- **Target:** Obsidian Community Plugins directory submission after M2 is complete.
- **Tests:** `tests/` directory, runnable with `npm test` (no Obsidian instance required). The conformance corpus from the spec repo (`tests/conformance/`) is the primary test fixture for the validator module.

---

## 15. Safety constraints (normative for the implementation)

These constraints are not negotiable in any milestone:

1. **The body of a note is never modified by the plugin.** Any frontmatter write operation must leave the content below the closing `---` delimiter byte-identical to what it was before.
2. **No Obsidian-internal or undocumented APIs.** The plugin may only call APIs present in the official Plugin API documentation at the time of the target Obsidian version.
3. **No network calls.** The plugin must function entirely offline. No telemetry, no remote spec fetches, no LLM calls.
4. **No writes without explicit user action.** Automated background processes (F1 validation, F3 graph, F4 badge, F5 panel, periodic vault scan) are read-only. The only operations that write to disk are the two F2 commands, and only when the user triggers them.

---

*obsidian-mosaix spec v1.0-draft — © 2026 Andrea Fiorino — MIT (plugin) · CC BY-SA 4.0 (this document)*
