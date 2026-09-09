"""validate_note(note) and validate_vault(path) → Report."""
from __future__ import annotations

import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from ._yaml import parse_frontmatter, normalise

CORE_KEYS = ("title", "updated", "tags", "summary", "keywords", "rev")
ENTITY_TYPES = {"person", "company", "product", "project", "tool", "place", "document", "event"}
ULID_RE = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
EMBED = re.compile(r"!\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
BODY_TAG = re.compile(r"(?<![\w/&])#((?![0-9A-Fa-f]{3,8}\b)[A-Za-z][A-Za-z0-9_/\-]*)")
RELIABILITY_MARKERS = ("✅", "⚠️", "🟢", "🟡", "❌", "status:", "sourced", "to-confirm",
                       "da fonte", "da confermare", "affidabilita", "affidabilità")
EXCLUDED_DIRS = {"_inbox", "_private", ".obsidian", ".git", "node_modules", ".trash", "__pycache__", ".vault-ingest"}
META_NAMES = {"conventions", "metodo e convenzioni", "claude", "readme", "taxonomy", "tag index", "tassonomia", "indice tag"}
META_DIRS = {"_meta", "99-meta", "meta"}
LEDGER_NAMES = {"open questions", "assunzioni da confermare", "domande aperte"}
MOC_NAMES = {"home", "00-index", "index", "00-indice", "indice"}


@dataclass
class Issue:
    code: str
    message: str
    path: str | None = None


@dataclass
class Report:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def conformant(self) -> bool:
        return not self.errors

    @property
    def is_conformant(self) -> bool:
        return not self.errors

    def _e(self, code: str, path: str | None, **kw: object) -> None:
        msg = _MESSAGES_E.get(code, code)
        try:
            msg = msg.format(**kw)
        except (KeyError, IndexError):
            pass
        self.errors.append(Issue(code=code, message=msg, path=path))

    def _w(self, code: str, path: str | None, **kw: object) -> None:
        msg = _MESSAGES_W.get(code, code)
        try:
            msg = msg.format(**kw)
        except (KeyError, IndexError):
            pass
        self.warnings.append(Issue(code=code, message=msg, path=path))


_MESSAGES_E: dict[str, str] = {
    "E001": "{rel}: no frontmatter",
    "E002": "{rel}: missing `{key}`",
    "E003": "{rel}: summary length {len} (120–240)",
    "E004": "{rel}: keywords count {count} (6–8)",
    "E005": "{rel}: entity type `{type}` not allowed",
    "E006": "{rel}: broken link [[{target}]]",
    "E007": "{rel}: orphan (no incoming link)",
    "E008": "{rel}: links id `{ulid}` does not resolve to any note",
    "E009": "{rel}: links target `{target}` does not exist",
    "E010": "{rel}: document with {count} fragments (≥2)",
    "E011": "{rel}: fragment `{fragment}` does not exist",
    "E012": "vault: no MOC note (type: moc, or Home/00-Index)",
    "E013": "vault: no meta note (§5.4)",
    "E014": "vault: no open-questions ledger (§5.3)",
    "E015": "vault: entities coverage {n}/{total} = {pct} (<80%)",
}
_MESSAGES_W: dict[str, str] = {
    "W001": "{rel}: {count} entities (>12); is this one question? (R1)",
    "W002": "{rel}: relation type `{type}` not in relation_types",
    "W003": "{rel}: missing `id` (required from v2.0; generate a ULID)",
    "W004": "{rel}: `id` is not a valid ULID: `{value}`",
    "W005": "{rel}: tag #{tag} not declared in meta note",
    "W006": "meta note declares no tags: taxonomy check skipped",
    "W007": "{rel}: no reliability marker",
    "W008": "{rel}: rev may be stale (hint only)",
}


def validate_note(note, *, entity_types: set[str] | None = None) -> Report:
    """Validate a single Note against Mosaix rules. Returns a Report."""
    from .parser import Note  # local to avoid circular at module level
    report = Report()
    rel = str(note.path)
    et = entity_types or ENTITY_TYPES

    if note.frontmatter_raw is None:
        report._e("E001", rel, rel=rel)
        return report

    fm = normalise(note.frontmatter_raw)

    for k in CORE_KEYS:
        if k == "title":
            continue
        if not fm.get(k) and fm.get(k) != 0:
            report._e("E002", rel, rel=rel, key=k)

    s = str(fm.get("summary", ""))
    if s and not (120 <= len(s) <= 240):
        report._e("E003", rel, rel=rel, len=len(s))

    kw = fm.get("keywords", [])
    if isinstance(kw, list) and kw and not (6 <= len(kw) <= 8):
        report._e("E004", rel, rel=rel, count=len(kw))

    ents = fm.get("entities", [])
    if isinstance(ents, list):
        for e in ents:
            if isinstance(e, dict) and str(e.get("type", "")).lower() not in et:
                report._e("E005", rel, rel=rel, type=e.get("type"))

    note_id = fm.get("id")
    if not note_id:
        report._w("W003", rel, rel=rel)
    elif not ULID_RE.match(str(note_id)):
        report._w("W004", rel, rel=rel, value=note_id)

    text = (note.frontmatter_raw or {})
    body_and_fm = note.body + " " + " ".join(f"{k}:{v}" for k, v in fm.items())
    if not any(m in body_and_fm for m in RELIABILITY_MARKERS):
        report._w("W007", rel, rel=rel)

    return report


def validate_vault(path: Path | str, *, check_rev: bool = False, exclude: tuple[str, ...] = ()) -> Report:
    """Validate an entire vault directory. Wraps audit() logic."""
    from collections import defaultdict
    vault = Path(path)
    report = Report()
    notes: dict[str, dict] = {}
    all_md: dict[str, Path] = {}

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

    id_to_stem: dict[str, str] = {}
    for name, n in notes.items():
        if n["fm"] and isinstance(n["fm"].get("id"), str):
            id_to_stem[n["fm"]["id"]] = name

    incoming: dict[str, int] = defaultdict(int)
    declared_tags: set[str] = {str(t) for t in (meta_decl.get("tags") or [])}
    has_moc = has_meta = has_ledger = False
    entity_count = 0

    for name, n in notes.items():
        fm, body, rel = n["fm"], n["body"], n["rel"]
        low = name.lower()
        if n["is_meta"]:
            has_meta = True
            declared_tags |= set(BODY_TAG.findall(body))
            declared_tags |= set(re.findall(r"`#([A-Za-z0-9_/\-]+)`", body))
        if low in LEDGER_NAMES:
            has_ledger = True

        for target in set(WIKILINK.findall(body)) | set(EMBED.findall(body)):
            t = target.strip().split("/")[-1]
            if t in all_md:
                incoming[t] += 1
            elif "." not in t:
                report._e("E006", rel, rel=rel, target=target)

        if fm is None:
            report._e("E001", rel, rel=rel)
            continue

        ntype = str(fm.get("type", "")).lower()
        if ntype == "moc" or "moc" in low or low in MOC_NAMES:
            has_moc = True

        for k in CORE_KEYS:
            if k == "title":
                continue
            if not fm.get(k) and fm.get(k) != 0:
                report._e("E002", rel, rel=rel, key=k)

        s = str(fm.get("summary", ""))
        if s and not (120 <= len(s) <= 240):
            report._e("E003", rel, rel=rel, len=len(s))
        kw = fm.get("keywords", [])
        if isinstance(kw, list) and kw and not (6 <= len(kw) <= 8):
            report._e("E004", rel, rel=rel, count=len(kw))

        ents = fm.get("entities", [])
        if isinstance(ents, list) and ents:
            entity_count += 1
            if len(ents) > 12 and ntype != "moc" and not n["is_meta"]:
                report._w("W001", rel, rel=rel, count=len(ents))
            for e in ents:
                if isinstance(e, dict) and str(e.get("type", "")).lower() not in entity_types:
                    report._e("E005", rel, rel=rel, type=e.get("type"))

        if relation_types:
            for r in fm.get("relations", []) or []:
                if isinstance(r, dict) and str(r.get("type", "")).lower() not in relation_types:
                    report._w("W002", rel, rel=rel, type=r.get("type"))

        note_id = fm.get("id")
        if not note_id:
            report._w("W003", rel, rel=rel)
        elif not ULID_RE.match(str(note_id)):
            report._w("W004", rel, rel=rel, value=note_id)

        for target in fm.get("links", []) or []:
            t = str(target).strip()
            if ULID_RE.match(t):
                if t in id_to_stem:
                    incoming[id_to_stem[t]] += 1
                else:
                    report._e("E008", rel, rel=rel, ulid=t)
            elif t in all_md:
                incoming[t] += 1
            else:
                report._e("E009", rel, rel=rel, target=t)

        if ntype == "document":
            frags = fm.get("fragments", []) or []
            if len(frags) < 2:
                report._e("E010", rel, rel=rel, count=len(frags))
            for f in frags:
                if str(f) not in all_md:
                    report._e("E011", rel, rel=rel, fragment=f)

        if n["is_meta"]:
            declared_tags |= {str(t) for t in (fm.get("tags", []) or [])}
        n["tags"] = set(BODY_TAG.findall(body)) | {str(t) for t in (fm.get("tags", []) or [])}

        body_and_fm = body + " " + " ".join(f"{k}:{v}" for k, v in fm.items())
        if not any(m in body_and_fm for m in RELIABILITY_MARKERS):
            report._w("W007", rel, rel=rel)

        if check_rev and fm.get("rev"):
            digest = hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:12]
            if digest != str(fm["rev"]):
                report._w("W008", rel, rel=rel)

    for name, n in notes.items():
        low = name.lower()
        if incoming.get(name, 0) == 0 and not n["is_meta"] and low not in LEDGER_NAMES and "moc" not in low and low not in MOC_NAMES:
            report._e("E007", n["rel"], rel=n["rel"])

    if declared_tags:
        for name, n in notes.items():
            for t in n.get("tags", set()):
                if t not in declared_tags and not t.startswith(("type/", "status/", "tipo/", "stato/")):
                    report._w("W005", n["rel"], rel=n["rel"], tag=t)
    else:
        report._w("W006", None)

    if not has_moc:
        report._e("E012", None)
    if not has_meta:
        report._e("E013", None)
    if not has_ledger:
        report._e("E014", None)
    if notes and entity_count / len(notes) < 0.80:
        report._e("E015", None, n=entity_count, total=len(notes), pct=f"{entity_count/len(notes):.0%}")

    return report
