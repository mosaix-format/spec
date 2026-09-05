#!/usr/bin/env python3
"""
audit_reference.py — reference conformance checker for Mosaix Format v1.0 (§10).

Standard library only. Read-only. Exit code 0 = conformant (no errors), 1 = errors found.

Usage:
    python audit_reference.py <vault_dir> [--json] [--check-rev] [--verbose] [--exclude=path1,path2]

--check-rev   also compare `rev` with sha256(body)[:12] (warning only; implementations
              may normalise the body differently, so a mismatch is a hint, not a verdict).
--exclude=    comma-separated relative path prefixes to skip (e.g. content exports that are
              payload for a platform, not notes). Excluded files still resolve links.

Canonical vocabulary is English (§3.1). Italian names used by pre-1.0 vaults are accepted
as default aliases (KEY_ALIASES, ITEM_ALIASES, VALUE_ALIASES) and reported by their
canonical name.

© 2026 Andrea Fiorino — CC BY-SA 4.0 (same licence as the specification).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CORE_KEYS = ("title", "updated", "tags", "summary", "keywords", "rev")
ENTITY_TYPES = {"person", "company", "product", "project", "tool", "place", "document", "event"}

# Default aliases (§3.1, §3.2, §3.4, §6). A vault may declare more in its meta note.
KEY_ALIASES = {
    "titolo": "title", "aggiornato": "updated", "riassunto": "summary", "parole_chiave": "keywords",
    "mcp_entita": "entities", "mcp_relazioni": "relations", "mcp_collegamenti": "links", "mcp_rev": "rev",
    "mcp_frammenti": "fragments", "mcp_pool": "pool", "mcp_layout": "layout",
    "tipo": "type", "stato": "status",
}
ITEM_ALIASES = {"nome": "name", "tipo": "type", "da": "from", "a": "to"}
VALUE_ALIASES = {
    # entity types
    "persona": "person", "azienda": "company", "prodotto": "product", "progetto": "project",
    "strumento": "tool", "luogo": "place", "documento": "document", "evento": "event",
    # note types
    "sintesi": "synthesis",
    # status
    "ok": "sourced", "confermare": "to-confirm", "superato": "superseded",
}

EXCLUDED_DIRS = {"_inbox", "_private", ".obsidian", ".git", "node_modules", ".trash", "__pycache__", ".vault-ingest"}
META_NAMES = {"conventions", "metodo e convenzioni", "claude", "readme", "taxonomy", "tag index", "tassonomia", "indice tag"}
META_DIRS = {"_meta", "99-meta", "meta"}
LEDGER_NAMES = {"open questions", "assunzioni da confermare", "domande aperte"}
MOC_NAMES = {"home", "00-index", "index", "00-indice", "indice"}
RELIABILITY_MARKERS = ("✅", "⚠️", "🟢", "🟡", "❌", "status:", "sourced", "to-confirm", "da fonte", "da confermare", "affidabilita", "affidabilità")

WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
EMBED = re.compile(r"!\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
BODY_TAG = re.compile(r"(?<![\w/&])#((?![0-9A-Fa-f]{3,8}\b)[A-Za-z][A-Za-z0-9_/\-]*)")


# ---------- minimal YAML subset (enough for the CORE keys) ----------

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


def parse_frontmatter(text: str):
    """Returns (frontmatter dict or None, body str)."""
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
                # block mapping item: "- name: X" followed by indented "  type: Y"
                d = {}
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


# ---------- normalisation (aliases → canonical) ----------

def _canon_items(items):
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
    """Map aliased keys and values to the canonical vocabulary. Canonical wins if both present."""
    aliases = dict(KEY_ALIASES)
    if extra_key_aliases:
        aliases.update(extra_key_aliases)
    out = {}
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
            v = out[k].lower()
            out[k] = VALUE_ALIASES.get(v, v)
    return out


# ---------- audit ----------

def audit(vault: Path, check_rev: bool = False, exclude: tuple[str, ...] = ()):
    errors: list[str] = []
    warnings: list[str] = []
    notes: dict[str, dict] = {}       # basename -> info
    all_md: dict[str, Path] = {}      # basename -> path (includes excluded dirs, for link resolution)

    files = []
    for p in vault.rglob("*.md"):
        rel_parts = p.relative_to(vault).parts
        rel = "/".join(rel_parts)
        all_md.setdefault(p.stem, p)
        if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
            continue
        if any(rel.startswith(x) for x in exclude):
            continue
        files.append((p, rel_parts, rel))

    # first pass: find the meta note and read its declarations (§5.4)
    meta_decl: dict = {}
    for p, rel_parts, rel in files:
        is_meta = p.stem.lower() in META_NAMES or any(part.lower() in META_DIRS for part in rel_parts[:-1])
        if not is_meta:
            continue
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if fm and "mosaix" in fm:
            meta_decl = fm
            break
    extra_aliases = meta_decl.get("aliases") if isinstance(meta_decl.get("aliases"), dict) else {}
    entity_types = set(ENTITY_TYPES) | {str(t).lower() for t in (meta_decl.get("entity_types") or [])}
    payload = tuple(str(x) for x in (meta_decl.get("payload") or []))
    relation_types = {str(t).lower() for t in (meta_decl.get("relation_types") or [])}

    for p, rel_parts, rel in files:
        if any(rel.startswith(x) for x in payload):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        if fm is not None:
            fm = normalise(fm, extra_aliases)
        is_meta = p.stem.lower() in META_NAMES or any(part.lower() in META_DIRS for part in rel_parts[:-1])
        notes[p.stem] = {"path": p, "fm": fm, "body": body, "rel": rel, "is_meta": is_meta}

    incoming: dict[str, int] = defaultdict(int)
    declared_tags: set[str] = {str(t) for t in (meta_decl.get("tags") or [])}
    declared_keys: set[str] = set(meta_decl.get("domain_keys") or {}) if isinstance(meta_decl.get("domain_keys"), dict) else set()
    has_moc = has_meta = has_ledger = False
    entity_count = 0
    reliability_missing: list[str] = []

    for name, n in notes.items():
        fm, body, rel = n["fm"], n["body"], n["rel"]
        low = name.lower()
        if n["is_meta"]:
            has_meta = True
            declared_tags |= set(BODY_TAG.findall(body))
            declared_tags |= set(re.findall(r"`#([A-Za-z0-9_/\-]+)`", body))
            declared_keys |= set(re.findall(r"`([a-z_]+)`", body))
        if low in LEDGER_NAMES:
            has_ledger = True

        # links
        for target in set(WIKILINK.findall(body)) | set(EMBED.findall(body)):
            t = target.strip().split("/")[-1]
            if t in all_md:
                incoming[t] += 1
            elif "." not in t:  # non-.md assets are not checked
                errors.append(f"{rel}: broken link [[{target}]]")

        if fm is None:
            errors.append(f"{rel}: no frontmatter")
            continue

        ntype = str(fm.get("type", "")).lower()
        if ntype == "moc" or "moc" in low or low in MOC_NAMES:
            has_moc = True

        for k in CORE_KEYS:
            if k not in fm or fm[k] in ("", [], None):
                if k == "title":
                    continue  # derivable from filename
                errors.append(f"{rel}: missing `{k}`")

        s = str(fm.get("summary", ""))
        if s and not (120 <= len(s) <= 240):
            errors.append(f"{rel}: summary length {len(s)} (120–240)")
        kw = fm.get("keywords", [])
        if isinstance(kw, list) and kw and not (6 <= len(kw) <= 8):
            errors.append(f"{rel}: keywords count {len(kw)} (6–8)")

        ents = fm.get("entities", [])
        if isinstance(ents, list) and ents:
            entity_count += 1
            if len(ents) > 12 and ntype != "moc" and not n["is_meta"]:
                warnings.append(f"{rel}: {len(ents)} entities (>12); is this one question? (R1)")
            for e in ents:
                if isinstance(e, dict) and str(e.get("type", "")).lower() not in entity_types:
                    errors.append(f"{rel}: entity type `{e.get('type')}` not allowed")

        if relation_types:
            for r in fm.get("relations", []) or []:
                if isinstance(r, dict) and str(r.get("type", "")).lower() not in relation_types:
                    warnings.append(f"{rel}: relation type `{r.get('type')}` not in relation_types")

        for target in fm.get("links", []) or []:
            t = str(target).strip()
            if t in all_md:
                incoming[t] += 1
            else:
                errors.append(f"{rel}: links target `{t}` does not exist")

        if ntype == "document":
            frags = fm.get("fragments", []) or []
            if len(frags) < 2:
                errors.append(f"{rel}: document with {len(frags)} fragments (≥2)")
            for f in frags:
                if str(f) not in all_md:
                    errors.append(f"{rel}: fragment `{f}` does not exist")

        if n["is_meta"]:
            declared_tags |= {str(t) for t in (fm.get("tags", []) or [])}
        n["tags"] = set(BODY_TAG.findall(body)) | {str(t) for t in (fm.get("tags", []) or [])}

        if not any(m in text_for_markers(fm, body) for m in RELIABILITY_MARKERS):
            reliability_missing.append(rel)

        if check_rev and fm.get("rev"):
            digest = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:12]
            if digest != str(fm["rev"]):
                warnings.append(f"{rel}: rev may be stale (hint only)")

    # orphans (a MOC / meta / ledger may legitimately have no incoming link)
    for name, n in notes.items():
        low = name.lower()
        if incoming.get(name, 0) == 0 and not n["is_meta"] and low not in LEDGER_NAMES and "moc" not in low and low not in MOC_NAMES:
            errors.append(f"{n['rel']}: orphan (no incoming link)")

    # taxonomy warnings
    if declared_tags:
        for name, n in notes.items():
            for t in n.get("tags", set()):
                if t not in declared_tags and not t.startswith(("type/", "status/", "tipo/", "stato/")):
                    warnings.append(f"{n['rel']}: tag #{t} not declared in meta note")
    else:
        warnings.append("meta note declares no tags: taxonomy check skipped")

    if not has_moc:
        errors.append("vault: no MOC note (type: moc, or Home/00-Index)")
    if not has_meta:
        errors.append("vault: no meta note (§5.4)")
    if not has_ledger:
        errors.append("vault: no open-questions ledger (§5.3)")
    if notes and entity_count / len(notes) < 0.80:
        errors.append(f"vault: entities coverage {entity_count}/{len(notes)} = {entity_count/len(notes):.0%} (<80%)")
    for rel in reliability_missing:
        warnings.append(f"{rel}: no reliability marker")

    return {
        "vault": str(vault),
        "mosaix": str(meta_decl.get("mosaix", "")) or None,
        "notes": len(notes),
        "errors": errors,
        "warnings": warnings,
        "conformant": not errors,
    }


def text_for_markers(fm: dict, body: str) -> str:
    return body + " " + " ".join(f"{k}:{v}" for k, v in fm.items())


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    vault = Path(argv[1]).resolve()
    as_json = "--json" in argv
    check_rev = "--check-rev" in argv
    verbose = "--verbose" in argv
    exclude: tuple[str, ...] = ()
    for a in argv:
        if a.startswith("--exclude="):
            exclude = tuple(x.strip() for x in a[len("--exclude="):].split(",") if x.strip())
    r = audit(vault, check_rev=check_rev, exclude=exclude)
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"Mosaix 1.0 audit — {r['vault']}")
        print(f"notes: {r['notes']}  errors: {len(r['errors'])}  warnings: {len(r['warnings'])}")
        print("CONFORMANT" if r["conformant"] else "NOT CONFORMANT")
        shown = r["errors"] if not verbose else r["errors"] + r["warnings"]
        for line in shown[:200]:
            print("  " + line)
        if len(shown) > 200:
            print(f"  … {len(shown) - 200} more")
    return 0 if r["conformant"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
