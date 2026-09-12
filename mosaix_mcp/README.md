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
| `read_note` | Read a note — returns parsed frontmatter (JSON) and body |
| `write_note` | Write a validated note; applies R7 supersede if file exists (requires `--writable`) |
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

Validates §10 rules before writing. Returns `{path, created, superseded}`.  
If the target already exists, the old file is renamed `<stem>_superseded.md` with
`status: superseded` and `superseded_by: <new_path>` added to its frontmatter.

### `search`

```json
{"query": "atomic notes", "field": "summary"}
```

`field` is optional. Without it, searches `summary + keywords + title`.  
Allowed values: `summary`, `keywords`, `entities`, `title`, `body`.  
Returns up to 20 results: `[{path, title, summary, score}]`.

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

### `list_notes`

```json
{"tag": "synthesis"}
{"type": "document"}
{}
```

Returns `[{path, title, type, tags, updated}]` sorted by `updated` descending.

### `switch_vault`

```json
{"vault_path": "/absolute/path/to/your/vault"}
```

Re-indexes the vault at the given path. All subsequent tool calls operate on
this vault until you call `switch_vault` again. Returns `{vault, notes_indexed, writable}`.

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
- **Scope**: read, write, search, compose, check, list. No enrichment, no vector
  store, no embedding, no retrieval ranking — those are implementation concerns (§8).

## Limitations

- ULID id-first link resolution (E008) is not checked — only filename-based links.
- Tag taxonomy warnings (W005–W006) and rev staleness (W008) are not checked.
- No streaming; the entire vault is indexed in memory at startup.
