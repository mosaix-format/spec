# MCP Tool Surface — Formal Definitions

**Mosaix Format v1.2.0 — Non-normative**

This document defines the formal input/output schema for the six tools exposed by a Mosaix MCP server. It complements the reference implementation in `mosaix_mcp/` and the architectural guide in `MULTIAGENT-INTEGRATION.md`.

---

## Transport

The reference server uses **stdio** (JSON-RPC 2.0 over standard input/output). This is the required transport for local, single-process deployments.

Implementations MAY additionally support **HTTP with Server-Sent Events (SSE)** for remote or multi-client deployments. When HTTP/SSE is used, the server MUST expose the same six tools with identical input/output schemas. Authentication and authorisation over HTTP are implementation-specific and outside the scope of this document.

---

## Error codes

All tools return JSON-RPC 2.0 error responses with the following application-specific codes:

| Code | Name | Meaning |
|------|------|---------|
| `-32001` | `NOT_FOUND` | The requested note does not exist at the given path. |
| `-32002` | `VALIDATION_ERROR` | The note fails one or more conformance checks (§10). The `data` field contains the list of errors. |
| `-32003` | `CONFLICT` | The note has been modified since the caller last read it. The `data` field contains the current `rev`. |
| `-32004` | `PERMISSION_DENIED` | The operation is not permitted — e.g. writing to a read-only vault or deleting a note with incoming links without `force: true`. |

Standard JSON-RPC 2.0 errors (`-32600` to `-32603`) apply for malformed requests, unknown methods, and invalid parameters.

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
