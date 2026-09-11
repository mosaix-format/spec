"""MCP server over stdio — JSON-RPC 2.0 newline-delimited transport."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "mosaix-mcp", "version": "1.2.0"}

# Instructions sent to the AI on initialize — teaches the Mosaix Format rules
# so the AI can write conformant notes without reading the spec externally.
SERVER_INSTRUCTIONS = """\
Mosaix Format vault server. ALWAYS load the "mosaix" skill before writing notes — it has the full rules.

Quick ref (the skill has details):
- Frontmatter REQUIRED: title, updated (YYYY-MM-DD), tags (list), summary (120-240 chars, declarative), keywords (6-8 terms), entities ({name,type} list), links (wikilink targets), rev (12 hex).
- Optional: id (ULID), question (ends with ?), origin, as_of, type, status, relations, fragments.
- Types: atomic (default), moc, synthesis, document, meta, ledger, log.
- Vault needs: _meta/Conventions.md (type:meta, mosaix:"1.2"), _meta/Open questions.md (type:ledger), at least one MOC.
- Rules: one idea per note (R1), no orphans (R3), supersede don't delete (R7).
- Italian aliases accepted: titolo, riassunto, parole_chiave, aggiornato, domanda, entita, tipo, stato.
- Always run check after writing. Call switch_vault first if no vault is loaded.
"""

TOOLS = [
    {
        "name": "switch_vault",
        "description": (
            "Load or switch to a different Mosaix vault. "
            "Re-indexes the vault at the given path. All subsequent tool calls operate on this vault."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "vault_path": {
                    "type": "string",
                    "description": "Absolute path to the vault directory.",
                }
            },
            "required": ["vault_path"],
        },
    },
    {
        "name": "read_note",
        "description": "Read a Mosaix note. Returns parsed frontmatter, body, and path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from vault root (e.g. 'spec/§3 The note.md') or just stem name.",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_note",
        "description": (
            "Write a validated Mosaix note. Requires server started with --writable. "
            "Validates §10 rules before writing. If the file already exists, applies R7: "
            "renames the old file with _superseded suffix and marks it superseded."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path from vault root"},
                "frontmatter": {"type": "object", "description": "Note frontmatter as a JSON object"},
                "body": {"type": "string", "description": "Note body (Markdown, without frontmatter block)"},
            },
            "required": ["path", "frontmatter", "body"],
        },
    },
    {
        "name": "search",
        "description": (
            "Case-insensitive substring search across vault notes. "
            "Default searches summary + keywords + title. Returns up to 20 results sorted by score."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "field": {
                    "type": "string",
                    "description": "Restrict to one field: summary, keywords, entities, title, body",
                    "enum": ["summary", "keywords", "entities", "title", "body"],
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "compose",
        "description": (
            "Assemble a composed document (type: document) from its fragments. "
            "Returns the concatenated body text and the list of fragment paths."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path or stem of the document note"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "check",
        "description": (
            "Run the Mosaix §10 conformance check. "
            "If path is given, checks one note; otherwise checks the entire vault."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional: relative path for a single-note check. Omit for full vault.",
                }
            },
        },
    },
    {
        "name": "list_notes",
        "description": "List vault notes with optional tag and/or type filter, sorted by updated descending.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "description": "Filter by tag value"},
                "type": {"type": "string", "description": "Filter by note type (moc, synthesis, document, …)"},
            },
        },
    },
]


class _ToolError(Exception):
    """Errors returned to the client as isError:true tool results."""


class _ServerState:
    """Mutable server state holding the current vault index."""

    def __init__(self, vault_path: Path | None, writable: bool) -> None:
        self.writable = writable
        self.index = None
        self.vault_path: Path | None = None
        if vault_path is not None:
            self.load_vault(vault_path)

    def load_vault(self, vault_path: Path) -> int:
        from .vault import VaultIndex
        vault_path = vault_path.resolve()
        if not vault_path.is_dir():
            raise _ToolError(f"Directory not found: {vault_path}")
        print(f"mosaix-mcp: indexing {vault_path} …", file=sys.stderr)
        self.index = VaultIndex(vault_path)
        self.vault_path = vault_path
        count = len(self.index)
        mode = "writable" if self.writable else "read-only"
        print(f"mosaix-mcp: ready — {count} notes indexed ({mode})", file=sys.stderr)
        return count

    def require_index(self):
        if self.index is None:
            raise _ToolError("No vault loaded. Call switch_vault first with the path to your vault.")
        return self.index


def run(vault_path: Path | None = None, writable: bool = False, verbose: bool = False) -> None:
    """Optionally index a vault, then serve MCP requests on stdin/stdout until EOF."""
    state = _ServerState(vault_path, writable)

    if vault_path is None:
        print("mosaix-mcp: started without vault — use switch_vault to load one", file=sys.stderr)

    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"mosaix-mcp: JSON parse error: {exc}", file=sys.stderr)
            continue

        req_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params") or {}

        if method.startswith("notifications/"):
            continue  # notifications need no response

        try:
            result = _dispatch(method, params, state)
            if req_id is not None:
                _send({"jsonrpc": "2.0", "id": req_id, "result": result})
        except _ToolError as exc:
            if req_id is not None:
                _send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True},
                })
        except Exception as exc:
            if verbose:
                traceback.print_exc(file=sys.stderr)
            if req_id is not None:
                _send({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}})


def _send(obj: Any) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")
    sys.stdout.flush()


def _dispatch(method: str, params: dict, state: _ServerState) -> Any:
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER_INFO,
            "instructions": SERVER_INSTRUCTIONS,
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments") or {}
        return _call_tool(name, args, state)
    raise Exception(f"Method not found: {method}")


def _call_tool(name: str, args: dict, state: _ServerState) -> dict:
    try:
        if name == "switch_vault":
            vault_path = Path(args["vault_path"])
            count = state.load_vault(vault_path)
            result = {
                "vault": str(state.vault_path),
                "notes_indexed": count,
                "writable": state.writable,
            }
        elif name == "read_note":
            index = state.require_index()
            result = index.read_note(args["path"])
        elif name == "write_note":
            if not state.writable:
                raise _ToolError("Server is read-only. Restart with --writable to enable writes.")
            index = state.require_index()
            result = index.write_note(args["path"], args["frontmatter"], args["body"])
        elif name == "search":
            index = state.require_index()
            result = index.search(args["query"], field=args.get("field"))
        elif name == "compose":
            index = state.require_index()
            result = index.compose(args["path"])
        elif name == "check":
            index = state.require_index()
            result = index.check(args.get("path"))
        elif name == "list_notes":
            index = state.require_index()
            result = index.list_notes(tag=args.get("tag"), note_type=args.get("type"))
        else:
            raise _ToolError(f"Unknown tool: {name}")
    except _ToolError:
        raise
    except (KeyError, ValueError) as exc:
        raise _ToolError(str(exc)) from exc

    return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, default=str)}]}
