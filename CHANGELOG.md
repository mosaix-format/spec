# Changelog — Mosaix Format

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
- Rules R1–R8 (atomicity, self-description, connectedness, declared taxonomy, composition over duplication, record-don't-resolve, supersede-don't-delete, propose-don't-apply).
- Meta note frontmatter (`mosaix`, `folders`, `reliability`, `tags`, `domain_keys`, `aliases`, `entity_types`, `relation_types`, `payload`, `maintainers`) read by the checker.
- Conformance checks (§10) and reference checker `audit_reference.py`.
- Obsidian host profile (§9): host features are outside the format.
- Explicit out-of-scope list (§8): enrichment, ingest, retrieval, editors, agent exposure, visualisation.

Available in English (normative) and Italian.
