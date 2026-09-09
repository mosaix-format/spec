"""Minimal YAML subset for Mosaix frontmatter — stdlib only.

Extracted from audit_reference.py. Handles the flat scalar + list structures
that appear in Mosaix CORE keys; does not support full YAML.
"""
from __future__ import annotations

ITEM_ALIASES = {"nome": "name", "tipo": "type", "da": "from", "a": "to"}
VALUE_ALIASES = {
    "persona": "person", "azienda": "company", "prodotto": "product", "progetto": "project",
    "strumento": "tool", "luogo": "place", "documento": "document", "evento": "event",
    "sintesi": "synthesis",
    "ok": "sourced", "confermare": "to-confirm", "superato": "superseded",
}
KEY_ALIASES = {
    "titolo": "title", "aggiornato": "updated", "riassunto": "summary", "parole_chiave": "keywords",
    "mcp_entita": "entities", "mcp_relazioni": "relations", "mcp_collegamenti": "links", "mcp_rev": "rev",
    "mcp_frammenti": "fragments", "mcp_pool": "pool", "mcp_layout": "layout",
    "tipo": "type", "stato": "status",
}


def _scalar(s: str):
    s = s.strip()
    if not s:
        return ""
    if (s[0] == s[-1]) and s[0] in "\"'":
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        items, depth, cur, quote = [], 0, "", ""
        for ch in inner:
            if quote:
                if ch == quote:
                    quote = ""
            elif ch in "\"'" and not cur.strip():
                quote = ch
            elif ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
            if ch == "," and depth == 0 and not quote:
                items.append(_scalar(cur))
                cur = ""
            else:
                cur += ch
        items.append(_scalar(cur))
        return items
    if s.startswith("{") and s.endswith("}"):
        d = {}
        for part in s[1:-1].split(","):
            if ":" in part:
                k, v = part.split(":", 1)
                d[k.strip()] = _scalar(v)
        return d
    return s


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter_dict | None, body_str)."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    block = text[3:end].strip("\n")
    body = text[end + 4:]
    fm: dict = {}
    key = None
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "" or val in ("|", ">"):
                fm[key] = [] if val == "" else ""
            else:
                fm[key] = _scalar(val)
        elif key is not None and line.lstrip().startswith("- "):
            item = line.lstrip()[2:].strip()
            if not isinstance(fm.get(key), list):
                fm[key] = []
            if item.startswith("{"):
                fm[key].append(_scalar(item))
            elif ":" in item and not item.startswith(("\"", "'", "[")):
                d: dict = {}
                k, _, v = item.partition(":")
                d[k.strip()] = _scalar(v)
                j = i + 1
                while j < len(lines) and lines[j].startswith((" ", "\t")) and not lines[j].lstrip().startswith("- ") and ":" in lines[j]:
                    k2, _, v2 = lines[j].strip().partition(":")
                    d[k2.strip()] = _scalar(v2)
                    j += 1
                fm[key].append(d)
                i = j
                continue
            else:
                fm[key].append(_scalar(item))
        elif key is not None and isinstance(fm.get(key), str):
            fm[key] = (fm[key] + " " + line.strip()).strip()
        i += 1
    return fm, body


def _canon_items(items: list) -> list:
    out = []
    for it in items or []:
        if isinstance(it, dict):
            d = {ITEM_ALIASES.get(k, k): v for k, v in it.items()}
            if "type" in d:
                t = str(d["type"]).lower()
                d["type"] = VALUE_ALIASES.get(t, t)
            out.append(d)
        else:
            out.append(it)
    return out


def normalise(fm: dict, extra_key_aliases: dict | None = None) -> dict:
    """Map aliased keys/values to canonical Mosaix vocabulary."""
    aliases = dict(KEY_ALIASES)
    if extra_key_aliases:
        aliases.update(extra_key_aliases)
    out: dict = {}
    for k, v in fm.items():
        canon = aliases.get(k, k)
        if canon in out and canon != k:
            continue
        out[canon] = v
    for k in ("entities", "relations"):
        if isinstance(out.get(k), list):
            out[k] = _canon_items(out[k])
    for k in ("type", "status"):
        if k in out and isinstance(out[k], str):
            v2 = out[k].lower()
            out[k] = VALUE_ALIASES.get(v2, v2)
    return out
