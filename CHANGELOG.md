# Changelog — Mosaix Format

## 1.3.0 — 2026-11-04

- **Dossiers (§6.1).** A dossier is a composed document whose fragments are chosen by a saved **criterion**: it gathers the notes around a topic, a customer, a project, an application or a source document. It lives in the new reserved folder `_dossier/` (recommended `_dossier/<kind>/<title>.md`) and carries a `dossier` map — `kind` (free word), `criterion.description` (+ optional `filters`: `folders`, `types`, `entities`, `documents`), `origin` (`document` · `model` · `owner`) — plus `members`, `added`, `excluded`, `external_links`, `members_rev`. `fragments` = `links` = members ∪ added − excluded, restricted to existing notes. An exclusion is a decision: no automated step undoes it. Italian aliases (`tipo`, `criterio`, `descrizione`, `filtri`, `origine`, `membri`, `aggiunte`, `esclusioni`, `link_esterni`, …) are defaults, so dossiers written by vault-mcp are conformant unchanged.
- **Checker:** E016 (dossier without `kind` or criterion), E017 (excluded note listed in `fragments`/`links`), W010 (stale dossier), W011 (unknown `origin`). The frontmatter parser now reads nested maps, both flow (`{a: {b: "x, y"}}`) and block style; W009 is now listed in `spec.yaml`. Fixed a YAML error in `spec.yaml` (line 74).
- **MCP server:** `list_dossiers` and `read_dossier`; `compose` accepts a dossier and uses its resolved notes; `check` reports the dossier codes. Server version 1.3.0.
- **Conformance corpus:** `edge-cases/dossier_valid/` and `edge-cases/dossier_broken/`.
- **Site:** new "Dossiers" section on the landing page and §6.1 in `spec.html`. Fixed the mobile layout: the four numbers of "Why it matters" were an inline 4-column grid that the media queries could not reach, and the page scrolled sideways on phones; the hero mosaic now sizes its tiles to the column.
- Labelled MINOR per GOVERNANCE §1: a new optional note shape and reserved folder; no 1.2 vault loses conformance.

## 1.2.1 — 2026-09-12

- **MCP server enhancements:**
  - `compose` tool now supports three modes: `text` (default, returns full text), `structure` (returns metadata only: bytes, words per fragment), and `file` (writes to `_composed/<stem>.txt` with SHA256 hash).
  - Added `fragments` parameter to `compose` for selective fragment inclusion.
  - UTF-8 encoding fix for Windows stdio (`_configure_stdio()`) — resolves `UnicodeEncodeError` on characters outside cp1252.
- **Zenodo archival metadata** (`zenodo.json`, `ZENODO-UPLOAD-INSTRUCTIONS.md`) for persistent DOI assignment.
- **Multiagent integration guides** (`MULTIAGENT-INTEGRATION.md`) — best practices for using Mosaix vaults in multi-agent systems with MCP.
- **MCP tool surface documentation** (`MCP-TOOL-SURFACE.md`) — complete tool schemas, examples, and error handling for the six MCP tools.

## 1.2.0 — 2026-09-09

- **`question` — optional CORE key.** A string field that records the single question this note answers (R1: atomicity). MUST end with `?`. Alias: `domanda`. Positioned before `summary` in canonical order; if present, `summary` SHOULD answer it. Documentation-only in v1.2: the checker does not validate it.
- **`origin` — optional, recommended CORE key.** Enum string: `human` (written by a person), `distilled` (synthesised or generated from other notes/sources), `observed` (captured from an external system or event). Records who wrote the note. Default alias: `origine`. Not validated by the checker in v1.2.
- **`as_of` — optional, recommended CORE key.** Date `YYYY-MM-DD`. When the described fact was true, distinct from `updated` which records when the note was last edited. Useful for market data, prices, decisions, and anything that changes over time. Default alias: `data_fatto`. Not validated by the checker in v1.2.
- Both `origin` and `as_of` sit after `rev` in the canonical key order: `title · id · updated · [domain keys] · question · summary · keywords · entities · relations · links · rev · origin · as_of`.

## 1.1.0 — 2026-09-08

- **`id` — tenth CORE key.** ULID (26 chars, Crockford Base32). Missing or invalid `id` is a warning (W003) in 1.x and becomes an error in 2.0 (GOVERNANCE §4). Links resolve id-first, filename as fallback.
- Labelled MINOR per GOVERNANCE §1: new optional key, new tooling, R8 relaxed from rule to recommendation. No 1.0 vault loses conformance.
- **R8 moved from normative rule to agent workflow recommendation (§7.1).** R8 ("Propose, don't apply") is now a non-normative SHOULD recommendation rather than a conformance rule. Rationale: a file cannot prove it was proposed rather than applied directly, so the checker cannot verify it; making it non-normative strengthens the claim that every remaining rule is machine-verifiable. The content and identifier are unchanged. Skills carry it as SHOULD. The checker is unaffected.
- **Cluster model clarified as observed average, not prescribed limit.** The ~600 token figure in §7 (site §07) is an observed average on production vaults, not a ceiling. Wording updated to prevent misinterpretation.
- **`spec.yaml` — machine-readable single source of truth.** Every CORE key, rule (R1–R7), recommendation (R8), conformance error (E001–E015) and warning (W001–W008) encoded in one parseable YAML file. The checker loads conformance messages from it (with hardcoded fallback).
- **Conformance test corpus** (`tests/conformance/`). 39 test cases across `valid/`, `invalid/`, `warnings/` and `edge-cases/`, with `expected.json` and a runner (`run_conformance.py`). All 39 pass.
- **Reference MCP server** (`mosaix_mcp/`). Stdlib-only Python package (~430 lines), JSON-RPC 2.0 over stdio, six tools: `read_note`, `write_note`, `search`, `compose`, `check`, `list_notes`. Writes validate against §10.
- **`mosaix_init.py`** — scaffold a new vault with the standard structure, a meta note, an open-questions ledger and a pre-configured GitHub Actions workflow. Optional `--with-examples`.
- **`mosaix_migrate.py`** — bring an existing directory of `.md` files toward Mosaix conformance with best-effort inference (title, summary, keywords, tags, links, rev). Body is never modified; every migrated note gets `reliability: to-confirm`. Supports `--dry-run` and `--git-dates`.
- **`GOVERNANCE.md`** — versioning policy (SemVer), RFC process with GitHub Issue template, backward compatibility guarantee, deprecation policy, version declaration, BDFL model.
- **`OBSIDIAN-PLUGIN-SPEC.md`** — functional specification for `obsidian-mosaix`: inline lint, scaffolding commands, graph enhancements (supersession chains, contradiction badges, orphan highlighting), status bar, sidebar panel, settings.

## 1.0.0 — 2026-09-04

First public version. Extracted from three production vaults. Working title "SLIM Vault Format" renamed to "Mosaix Format" on 2026-09-03; the format's frontmatter key is `mosaix`. Canonical vocabulary switched to English on 2026-09-04, before publication; the Italian names used by the source vaults are default aliases.

- GitHub Action (`mosaix-format/spec@v1.0.0`) wrapping the reference checker.
- Two example vaults, both conformant: the specification itself (with Obsidian templates and a minimal `.obsidian/`) and a fictional bakery.
- Site: `llms.txt`, `llms-full.txt`, `robots.txt`, `sitemap.xml`; "Compared with" reference section.
- CORE frontmatter: `title`, `updated`, `tags`, `summary` (120–240), `keywords` (6–8), `entities`, `relations`, `links`, `rev`.
- Default aliases: `mcp_entita → entities`, `mcp_relazioni → relations`, `mcp_collegamenti → links`, `mcp_rev → rev`, `mcp_frammenti → fragments`, `mcp_pool → pool`, `mcp_layout → layout`, `tipo → type`, `stato → status`, `aggiornato → updated`, `titolo → title`, `riassunto → summary`, `parole_chiave → keywords`; item keys `nome/tipo/da/a → name/type/from/to`; Italian entity types, note types and status values map to the English ones. A vault may declare further aliases in its meta note.
- `entities` SHOULD hold at most 12 items (warning above); `layout` example for composed documents.
- Two independent reliability axes (true? / exists?); recommended `status` key with `sourced · to-confirm · superseded`.
- Reserved folders `_meta/`, `_synthesis/` (alias `_sintesi/`), `_inbox/`; optional unversioned `_private/`; declared payload folders.
- Note types with format meaning: `moc`, `synthesis`, `document`.
- Composed documents (`type: document`, `fragments`, `pool`, `layout`).
- Rules R1–R7 (atomicity, self-description, connectedness, declared taxonomy, composition over duplication, record-don't-resolve, supersede-don't-delete); agent workflow recommendation R8 (propose-don't-apply, non-normative, §7.1).
- Meta note frontmatter (`mosaix`, `folders`, `reliability`, `tags`, `domain_keys`, `aliases`, `entity_types`, `relation_types`, `payload`, `maintainers`) read by the checker.
- Conformance checks (§10) and reference checker `audit_reference.py`.
- Obsidian host profile (§9): host features are outside the format.
- Explicit out-of-scope list (§8): enrichment, ingest, retrieval, editors, agent exposure, visualisation.

Available in English (normative) and Italian.
