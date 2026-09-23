# MCP Tool Surface — Formal Definitions

**Mosaix Format v1.2.0 — Non-normative**

This document defines the formal input/output schema for the six tools exposed by a Mosaix MCP server. It complements the reference implementation in `mosaix_mcp/` and the architectural guide in `MULTIAGENT-INTEGRATION.md`.

---

## Transport

The reference server uses **stdio** (JSON-RPC 2.0 over standard input/output). This is the required transport for local, single-process deployments.

Implementations MAY additionally support **HTTP with Server-Sent Events (SSE)** for remote or multi-client deployments. When HTTP/SSE is used, the server MUST expose the same six tools with identical input/output schemas. Authentication and authorisation over HTTP are implementation-specific and outside the scope of this document.

---

## Error codes

How the **reference server** reports failures:

- **Tool-level errors** are returned as a normal tool result with `isError: true` and a
  human-readable message. When a client has to distinguish a case programmatically, the
  message starts with a stable token: e.g. `PERMISSION_DENIED:` for deleting a note with
  incoming links without `force: true`.
- **Unexpected exceptions** are returned as a JSON-RPC error with code `-32000`.
- **Malformed requests** use the standard JSON-RPC codes (`-32600`–`-32603`).

The names below are the error vocabulary implementations SHOULD use as the message token.
The numeric `-320xx` codes are **reserved for HTTP/SSE deployments**, where an application
error can be carried in the JSON-RPC error object itself; the stdio reference server does not
emit them.

| Name | Meaning |
|------|---------|
| `NOT_FOUND` | The requested note does not exist at the given path. |
| `VALIDATION_ERROR` | The note fails one or more conformance checks (§10). |
| `CONFLICT` | The note has been modified since the caller last read it. |
| `PERMISSION_DENIED` | The operation is not permitted — e.g. writing to a read-only vault, or deleting a note with incoming links without `force: true`. |

---

## Tool definitions

### `read_note`

Read a single note. The returned frontmatter is **stripped** of `id`, `rev`, `status`, `updated`, and `mosaix` keys before delivery. These keys are housekeeping metadata that wastes tokens and invites hallucination when injected into an LLM context. If the caller needs these keys (for orchestration or staleness checks), it should use `list_notes`.

**Input:**

```json
{
  "path": "Product/Hydraulic hoses.md"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Vault-relative path to the note. |

**Output:**

```json
{
  "path": "Product/Hydraulic hoses.md",
  "frontmatter": {
    "title": "Hydraulic hoses",
    "tags": ["product", "hydraulics"],
    "question": "What types of hydraulic hoses does the company produce?",
    "summary": "The company manufactures three families of hydraulic hoses...",
    "keywords": ["hydraulic", "hose", "rubber", "coupling", "pressure", "SAE"],
    "entities": [
      {"name": "2SN hose", "type": "product"},
      {"name": "SAE 100R2", "type": "document"}
    ],
    "relations": [
      {"from": "2SN hose", "type": "complies with", "to": "SAE 100R2"}
    ],
    "links": ["Rubber compounds", "Pressure ratings"],
    "origin": "human",
    "as_of": "2026-08-15"
  },
  "body": "The company manufactures three families of hydraulic hoses..."
}
```

Note: `id`, `rev`, `status`, `updated`, and `mosaix` are **not present** in the output, even though they exist in the file on disk. This is the stratification rule — see MULTIAGENT-INTEGRATION.md §2.

---

### `search`

Full-text search across the vault. Returns results ranked by relevance.

**Input:**

```json
{
  "query": "hydraulic pressure rating",
  "limit": 10
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | yes | Search query (plain text). |
| `limit` | integer | no | Maximum results to return. Default: 10. |

**Output:**

```json
{
  "results": [
    {
      "path": "Product/Hydraulic hoses.md",
      "summary": "The company manufactures three families of hydraulic hoses...",
      "score": 0.92
    }
  ],
  "total": 1
}
```

---

### `list_notes`

Enumerate notes in the vault, optionally filtered by folder or tag.

**Input:**

```json
{
  "folder": "Product/",
  "tag": "hydraulics"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder` | string | no | Vault-relative folder path. Lists only notes under this folder. |
| `tag` | string | no | Filter to notes carrying this tag. |

**Output:**

```json
{
  "notes": [
    {
      "path": "Product/Hydraulic hoses.md",
      "title": "Hydraulic hoses",
      "updated": "2026-08-15",
      "tags": ["product", "hydraulics"],
      "id": "01J5M9KQXP3N7V8W2RTYH6FGDC",
      "rev": "a1b2c3d4e5f6",
      "status": "sourced"
    }
  ],
  "total": 1
}
```

Note: unlike `read_note`, `list_notes` **includes** `id`, `rev`, `status`, and `updated`. These fields are useful for orchestration (staleness checks, deduplication, cross-vault resolution) but should not be injected into LLM prompts.

---

### `write_note`

Create or update a note. The server validates the note against §10 conformance checks **before** persisting. If validation fails, the server returns a `VALIDATION_ERROR` with the list of errors and does not write the file.

On update, if the caller supplies a `rev` in the frontmatter, the server checks it against the current file's `rev`. A mismatch returns a `CONFLICT` error — the note has been modified since the caller last read it. If no `rev` is supplied, the server overwrites unconditionally.

**Input:**

```json
{
  "path": "Product/Hydraulic hoses.md",
  "frontmatter": {
    "title": "Hydraulic hoses",
    "tags": ["product", "hydraulics"],
    "summary": "The company manufactures three families of hydraulic hoses...",
    "keywords": ["hydraulic", "hose", "rubber", "coupling", "pressure", "SAE"],
    "entities": [
      {"name": "2SN hose", "type": "product"}
    ]
  },
  "body": "The company manufactures three families of hydraulic hoses..."
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Vault-relative path. Created if it does not exist. |
| `frontmatter` | object | yes | YAML frontmatter keys. The server adds `rev` (computed from body), `updated` (today), and `mosaix: true` automatically. |
| `body` | string | yes | Markdown body of the note. |

**Output:**

```json
{
  "path": "Product/Hydraulic hoses.md",
  "rev": "a1b2c3d4e5f6",
  "created": false
}
```

---

### `move_note`

Move or rename a note. The server updates all incoming wikilinks across the vault to point to the new path.

**Input:**

```json
{
  "from": "Product/Hydraulic hoses.md",
  "to": "Product/Hoses/Hydraulic hoses.md"
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from` | string | yes | Current vault-relative path. |
| `to` | string | yes | Target vault-relative path. Must not already exist. |

**Output:**

```json
{
  "from": "Product/Hydraulic hoses.md",
  "to": "Product/Hoses/Hydraulic hoses.md",
  "updated_refs": 3
}
```

---

### `delete_note`

Delete a note from the vault. If other notes link to this note (incoming wikilinks), the server returns a `PERMISSION_DENIED` error unless `force: true` is passed. Per R7 (Supersede, don't delete), prefer marking a note as `status: superseded` over deleting it.

**Input:**

```json
{
  "path": "Product/Obsolete widget.md",
  "force": false
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Vault-relative path to delete. |
| `force` | boolean | no | If `true`, delete even if incoming links exist. Default: `false`. |

**Output:**

```json
{
  "path": "Product/Obsolete widget.md",
  "deleted": true
}
```

---

## Implementation extensions

The six tools above are the **portable core**: a client that speaks them can work against any
conforming server. The reference implementation additionally exposes the tools below. They are
not part of the portable contract — treat them as extensions, and do not assume another
implementation has them.

| Tool | Purpose |
|------|---------|
| `switch_vault` | Load or switch the active vault at runtime, re-indexing it. Session management, not knowledge. |
| `reindex` | Rebuild the in-memory index from disk. Needed after writes made outside the server: the reference server indexes once at `switch_vault` and updates only the notes it writes itself. |
| `compose` | Assemble a `type: document` note from its `fragments`. Modes: `text` (default), `structure` (metadata only, no text), `file` (write the text to `_composed/<stem>.txt`), plus an optional `fragments` selection. |
| `check` | Run the §10 conformance check on one note or the whole vault. |
| `history` | Version chain of a note, following the R7 supersession arcs. Metadata only — cheap by design. |

Two consequences worth knowing when implementing a server:

- **Retired notes are history, not content.** `search` and `list_notes` exclude notes marked
  `status: superseded` by default; `include_superseded: true` includes them, and `history`
  walks them explicitly.
- **A new version is a new note.** R7 copies the previous frontmatter verbatim, so the caller
  must give the new version a fresh `id`; otherwise both versions share a ULID and the
  `superseded_by` arc becomes ambiguous. Arcs written as ULIDs survive renames by
  construction; stem and path arcs are accepted for compatibility and `move_note` rewrites
  them.

---

## Stratification summary

The stratification rule is the single most important design decision in the tool surface. It exists because LLMs treat everything in their context as content to reason about and reproduce. A ULID in the prompt becomes a ULID in the output — fabricated, mangled, or echoed without understanding. A revision hash becomes something the model "knows" and may assert as current when it is stale.

| Key | In `read_note` | In `list_notes` | In `write_note` (input) | In file on disk |
|-----|:-:|:-:|:-:|:-:|
| `id` | stripped | included | optional | present |
| `rev` | stripped | included | optional (conflict check) | present (computed) |
| `status` | stripped | included | optional | present |
| `updated` | stripped | included | auto-set | present (auto-set) |
| `mosaix` | stripped | — | auto-set | present (auto-set) |
| All other keys | included | — | required/optional per §3.1 | present |

---

## References

- Mosaix Format Specification v1.2.0: [Mosaix-Format-v1.2.en.md](Mosaix-Format-v1.2.en.md)
- Multi-Agent Integration Guide: [MULTIAGENT-INTEGRATION.md](MULTIAGENT-INTEGRATION.md)
- Reference MCP server: [mosaix_mcp/](mosaix_mcp/)
- Machine-readable spec: [spec.yaml](spec.yaml)
