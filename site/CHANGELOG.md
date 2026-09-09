# Changelog — Mosaix Format

## 1.2.0 — 2026-09-09

- **`question` — optional CORE key.** A string field that records the single question this note answers (R1: atomicity). MUST end with `?`. Alias: `domanda`. Positioned before `summary` in canonical order; if present, `summary` SHOULD answer it. Documentation-only in v1.2: the checker does not validate it.

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
