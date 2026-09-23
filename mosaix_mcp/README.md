# Mosaix Reference MCP Server

Minimal, stdlib-only Python MCP server for [Mosaix Format](../Mosaix-Format-v1.0.en.md) vaults.

**No dependencies** — Python 3.10+ standard library only.  
**Read-only by default** — writes require `--writable`.  
**~430 lines** across four files.

## Install

```bash
git clone <repo> && cd <repo>
# No pip install needed — run directly as a package
```

## Usage

```bash
# Start without a vault — choose which vault to load via switch_vault tool
python -m mosaix_mcp --writable

# Start with a default vault (still switchable at runtime)
python -m mosaix_mcp /path/to/vault --writable

# Read-only (safe default, no --writable)
python -m mosaix_mcp /path/to/vault

# Verbose error output on stderr
python -m mosaix_mcp /path/to/vault --verbose
```

## Tools

| Tool | Description |
|---|---|
| `switch_vault` | Load or switch to a different vault at runtime — re-indexes the new path |
| `reindex` | Rebuild the in-memory index from disk — needed after writes made outside the server |
| `read_note` | Read a note — returns parsed frontmatter (JSON) and body |
| `history` | Version chain of a note, following the R7 supersession arcs — metadata only |
| `write_note` | Write a validated note; applies R7 supersede if file exists (requires `--writable`) |
| `move_note` | Move or rename a note, rewriting every incoming wikilink and `links` entry |
| `delete_note` | Delete a note; refuses if other notes link to it unless `force: true` |
| `search` | Case-insensitive substring search across summary, keywords, title (or any field) |
| `compose` | Assemble a `type: document` note from its fragments |
| `check` | Run §10 conformance check on one note or the whole vault |
| `list_notes` | List notes with optional `tag` / `type` filter, sorted by `updated` |

### `read_note`

```json
{"path": "spec/§3 The note.md"}
```

Returns `{frontmatter: {...}, body: "...", path: "..."}`.  
Accepts relative paths from vault root or bare stem names (`§3 The note`).

### `history`

```json
{"path": "notes/my-topic.md"}
```

Returns the version chain of a note: follows `superseded_by` forwards and backwards (every
note that points to this one), resolving each arc by stem or by ULID `id`. Metadata only —
`id`, `updated`, `status`, `title`, `superseded_by`, `current` — sorted oldest first, capped
at 50 entries, with `chain_length`. The bodies are not included: read them with `read_note`
when you need one.

```json
{"path": "notes/my-topic.md", "chain_length": 2,
 "chain": [{"stem": "my-topic_001", "status": "superseded", "superseded_by": "my-topic", …},
           {"stem": "my-topic", "status": "", "current": true, …}]}
```

### `write_note`

```json
{
  "path": "notes/my-topic.md",
  "frontmatter": {
    "title": "My topic",
    "updated": "2026-01-01",
    "tags": ["research"],
    "summary": "...",
    "keywords": ["a", "b", "c", "d", "e", "f"],
    "rev": "abc123def456"
  },
  "body": "# My topic\n\n..."
}
```

Validates §10 rules before writing. Returns `{path, created, superseded, overwritten}`.  
If the target already exists, the old file is renamed `<stem>_superseded.md` with
`status: superseded` and `superseded_by: <id of the new version>` added to its frontmatter —
unless `supersede` is `false`, in which case the file is overwritten **in place**, with no
copy: use it for corrections that do not deserve a version (typos, formatting).

**A new version is a new note, and carries a new `id`.** R7 copies the previous frontmatter
verbatim, so if the caller reuses the old ULID the two versions share it and `superseded_by`
becomes ambiguous. Generate a fresh ULID for the new version; `history` resolves the chain
either way (it prefers the live note over a retired copy), but the distinct id is what makes
the arc unambiguous and rename-proof.

```json
{"path": "notes/my-topic.md", "frontmatter": {…}, "body": "…", "supersede": false}
```

### `move_note`

```json
{"from": "Product/Hydraulic hoses.md", "to": "Product/Hoses/Hydraulic hoses.md"}
```

Moves or renames a note and rewrites every incoming reference: wikilinks in bodies
(`[[stem]]`, with alias, anchor or folder prefix) and entries in `links:`. The destination
must not already exist. Returns `{from, to, updated_refs}`. It does **not** version the note:
use `write_note` for that.

```json
{"from": "Product/Hydraulic hoses.md", "to": "Product/Hoses/Hydraulic hoses.md", "updated_refs": 3}
```

### `delete_note`

```json
{"path": "Product/Obsolete widget.md", "force": false}
```

Deletes the note file. If other notes link to it, the server refuses with
`PERMISSION_DENIED` unless `force` is `true`. Forcing leaves dangling references, which the
checker reports as `E009`. Per R7, prefer marking a note `status: superseded` over deleting
it: deletion is not recoverable.

```json
{"path": "Product/Obsolete widget.md", "deleted": true, "incoming_refs": 0}
```

### `search`

```json
{"query": "atomic notes", "field": "summary"}
```

`field` is optional. Without it, searches `summary + keywords + title`.  
Allowed values: `summary`, `keywords`, `entities`, `title`, `body`.  
Returns up to 20 results: `[{path, title, summary, score}]`.  
Retired notes (`status: superseded`) are **excluded by default** — they are history, not
current content. Pass `include_superseded: true` to search them too, or use `history` to see
a note's version chain.

### `compose`

Assembles a `type: document` note by concatenating its `fragments` bodies, separated by a blank line with three dashes.

**Modes:**
- **`text`** (default): Unchanged behavior. Returns `{path, title, fragments: [...], composed_text: "..."}`.
- **`structure`**: Returns `{path, title, fragments: [{stem, rel, title, bytes, words}], total_bytes, total_words}` without the text content.
- **`file`**: Writes the composed document to `<vault>/_composed/<stem>.txt` and returns `{path, title, fragments: [...], composed_path, bytes, sha256}`.

**Parameters:**
- `fragments`: A list of fragment stems to include (e.g., `["stem1", "stem2"]`). If omitted, all fragments are used.
- `mode`: Must be one of "text", "structure", or "file". Unknown modes raise a `ValueError`.

**Examples:**

### `check`

```json
{}                            // full vault
{"path": "spec/§3 The note.md"}  // single note
```

Returns `{errors: [{id, message}], warnings: [{id, message}], notes_checked, conformant}`.  
Covers E001–E015 and W003–W004 from §10. The `id` field matches the spec code
(e.g. `"E002"`, `"W003"`).

Notes marked `status: superseded`, or whose filename carries the `_superseded` suffix, are
exempt from **E007**: R7 creates them without incoming links by construction, so flagging
them as orphans would be a false positive.

### `list_notes`

```json
{"tag": "synthesis"}
{"type": "document"}
{}
```

Returns `[{path, title, type, tags, updated}]` sorted by `updated` descending.  
Retired notes are **excluded by default**; pass `include_superseded: true` to list them.

### `switch_vault`

```json
{"vault_path": "/absolute/path/to/your/vault"}
```

Re-indexes the vault at the given path. All subsequent tool calls operate on
this vault until you call `switch_vault` again. Returns `{vault, notes_indexed, writable}`.

### `reindex`

```json
{}
```

Rebuilds the in-memory index from disk. The server indexes once at `switch_vault` and updates
the index only for notes it writes itself, so after any write made outside the server — or
after R7 renames a previous version to `*_superseded.md` — `check`, `search` and `list_notes`
describe a stale vault. Call `reindex` before trusting them again. Returns
`{vault, notes_indexed, reindexed}`.

## Claude Desktop config

Start **without** a hardcoded vault — choose which vault to load at the beginning
of each conversation via `switch_vault`:

```json
{
  "mcpServers": {
    "mosaix": {
      "command": "python",
      "args": ["-m", "mosaix_mcp", "--writable"],
      "cwd": "/path/to/repo/spec"
    }
  }
}
```

Or start with a default vault (still switchable at runtime):

```json
{
  "mcpServers": {
    "mosaix": {
      "command": "python",
      "args": ["-m", "mosaix_mcp", "/absolute/path/to/your/vault", "--writable"],
      "cwd": "/path/to/repo/spec"
    }
  }
}
```

The `cwd` must point to the directory where `mosaix_mcp/` lives, or add it
to `PYTHONPATH`.

## Design notes

- **Transport**: JSON-RPC 2.0 over stdio, newline-delimited (one JSON object per line).
  No HTTP, no SSE, no external MCP SDK.
- **Parser**: minimal YAML subset — flat scalars, inline lists, block list-of-dicts.
  Sufficient for all Mosaix frontmatter structures; no general YAML needed.
- **Aliases**: Italian key aliases (`titolo`, `riassunto`, …) are accepted transparently,
  same as the reference checker.
- **Check**: inline implementation of §10 core rules (E001–E015, W003–W004).
  Does not require `audit_reference.py` at runtime.
- **Scope**: read, write, search, compose, check, list, reindex. No enrichment, no vector
  store, no embedding, no retrieval ranking — those are implementation concerns (§8).

## Limitations

- ULID id-first link resolution (E008) is not checked — only filename-based links.
- Tag taxonomy warnings (W005–W006) and rev staleness (W008) are not checked.
- No streaming; the entire vault is indexed in memory at `switch_vault`. Writes made outside
  the server are not seen until `reindex` is called.
