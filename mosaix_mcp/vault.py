"""Vault operations for Mosaix Format: read, write, search, compose, check, list."""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

# ── Mosaix constants (§3, §5, §10) ──────────────────────────────────────────

CORE_KEYS = ("title", "updated", "tags", "summary", "keywords", "rev")
ENTITY_TYPES = {"person", "company", "product", "project", "tool", "place", "document", "event"}
ULID_RE = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")

KEY_ALIASES: dict[str, str] = {
    "titolo": "title", "aggiornato": "updated", "riassunto": "summary",
    "parole_chiave": "keywords", "mcp_entita": "entities", "mcp_relazioni": "relations",
    "mcp_collegamenti": "links", "mcp_rev": "rev", "mcp_frammenti": "fragments",
    "mcp_pool": "pool", "mcp_layout": "layout", "tipo": "type", "stato": "status",
}
ITEM_ALIASES: dict[str, str] = {"nome": "name", "tipo": "type", "da": "from", "a": "to"}
VALUE_ALIASES: dict[str, str] = {
    "persona": "person", "azienda": "company", "prodotto": "product", "progetto": "project",
    "strumento": "tool", "luogo": "place", "documento": "document", "evento": "event",
    "sintesi": "synthesis",
    "ok": "sourced", "confermare": "to-confirm", "superato": "superseded",
}

EXCLUDED_DIRS = {"_inbox", "_private", ".obsidian", ".git", "node_modules", ".trash", "__pycache__", ".vault-ingest"}
META_NAMES = {"conventions", "metodo e convenzioni", "claude", "readme", "taxonomy", "tag index", "tassonomia", "indice tag"}
META_DIRS = {"_meta", "99-meta", "meta"}
LEDGER_NAMES = {"open questions", "assunzioni da confermare", "domande aperte"}
MOC_NAMES = {"home", "00-index", "index", "00-indice", "indice"}
RELIABILITY_MARKERS = ("✅", "⚠️", "🟢", "🟡", "❌", "status:", "sourced", "to-confirm")

# ── Minimal YAML subset parser ───────────────────────────────────────────────

def _scalar(s: str):
    """Parse a YAML scalar: quoted string, inline list, inline dict, or plain string."""
    s = s.strip()
    if not s:
        return ""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
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
        d: dict = {}
        for part in s[1:-1].split(","):
            if ":" in part:
                k, v = part.split(":", 1)
                d[k.strip()] = _scalar(v)
        return d
    return s


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Extract and parse YAML frontmatter block. Returns (fm_dict or None, body_str)."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    block = text[3:end].strip("\n")
    body = text[end + 4:]
    fm: dict = {}
    key: str | None = None
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
            fm[key] = [] if val == "" else ("" if val in ("|", ">") else _scalar(val))
        elif key is not None and line.lstrip().startswith("- "):
            item = line.lstrip()[2:].strip()
            if not isinstance(fm.get(key), list):
                fm[key] = []
            if ":" in item and not item.startswith(("\"", "'", "[", "{")):
                d: dict = {}
                k, _, v = item.partition(":")
                d[k.strip()] = _scalar(v)
                j = i + 1
                while (j < len(lines) and lines[j].startswith((" ", "\t"))
                       and not lines[j].lstrip().startswith("- ") and ":" in lines[j]):
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


def normalise(fm: dict) -> dict:
    """Map aliased keys/values to the canonical Mosaix vocabulary."""
    out: dict = {}
    for k, v in fm.items():
        canon = KEY_ALIASES.get(k, k)
        if canon in out and canon != k:
            continue
        out[canon] = v
    for key in ("entities", "relations"):
        if isinstance(out.get(key), list):
            items = []
            for it in out[key]:
                if isinstance(it, dict):
                    d = {ITEM_ALIASES.get(ik, ik): iv for ik, iv in it.items()}
                    if "type" in d:
                        t = str(d["type"]).lower()
                        d["type"] = VALUE_ALIASES.get(t, t)
                    items.append(d)
                else:
                    items.append(it)
            out[key] = items
    for key in ("type", "status"):
        if key in out and isinstance(out[key], str):
            v = out[key].lower()
            out[key] = VALUE_ALIASES.get(v, v)
    return out


def serialize_frontmatter(fm: dict) -> str:
    """Serialize a dict to YAML frontmatter (Mosaix subset). Returns '---\\n...\\n---\\n'."""
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            elif isinstance(v[0], dict):
                lines.append(f"{k}:")
                for item in v:
                    parts = ", ".join(f"{ik}: {iv}" for ik, iv in item.items())
                    lines.append(f"  - {{{parts}}}")
            else:
                serialized: list[str] = []
                for x in v:
                    sx = str(x)
                    if any(c in sx for c in ', []{}"\' '):
                        sx = f'"{sx}"'
                    serialized.append(sx)
                lines.append(f"{k}: [{', '.join(serialized)}]")
        else:
            sv = str(v) if v is not None else "~"
            if v is not None and any(c in sv for c in ':#{}[]|>"\'') or (sv and sv[0] in " \t"):
                sv = f'"{sv}"'
            lines.append(f"{k}: {sv}")
    lines.append("---")
    return "\n".join(lines) + "\n"


# ── Note validation ──────────────────────────────────────────────────────────

def _validate_note(fm: dict) -> list[str]:
    """Return a list of §10 violation strings for a single note's frontmatter."""
    nfm = normalise(dict(fm))
    violations: list[str] = []
    for k in CORE_KEYS:
        if k == "title":
            continue
        if k not in nfm or nfm[k] in ("", [], None):
            violations.append(f"missing required key: `{k}`")
    s = str(nfm.get("summary", ""))
    if s and not (120 <= len(s) <= 240):
        violations.append(f"summary length {len(s)} must be 120–240 characters")
    kw = nfm.get("keywords", [])
    if isinstance(kw, list) and kw and not (6 <= len(kw) <= 8):
        violations.append(f"keywords count {len(kw)} must be 6–8")
    for e in nfm.get("entities", []) or []:
        if isinstance(e, dict) and str(e.get("type", "")).lower() not in ENTITY_TYPES:
            violations.append(f"entity type `{e.get('type')}` not in allowed types")
    return violations


# ── Conformance checker (§10 core rules) ────────────────────────────────────

def _check(
    notes: dict[str, dict],
    all_stems: dict[str, Path],
    target_rel: str | None,
) -> dict:
    """Minimal §10 conformance check. Returns errors/warnings dicts."""
    errors: list[dict] = []
    warnings: list[dict] = []
    incoming: dict[str, int] = defaultdict(int)

    # Phase 1: collect incoming link counts across ALL notes (needed for orphan check)
    for stem, n in notes.items():
        for target in set(WIKILINK.findall(n["body"])):
            t = target.strip().split("/")[-1]
            incoming[t] += 1
        if n["fm"]:
            for t_raw in (n["fm"].get("links", []) or []):
                t = str(t_raw).strip()
                if not ULID_RE.match(t) and t in all_stems:
                    incoming[t] += 1

    # Phase 2: per-note checks
    checked: dict[str, dict] = {}
    has_moc = has_meta = has_ledger = False
    entity_count = 0

    for stem, n in notes.items():
        rel = n["rel"]
        if target_rel and rel != target_rel:
            continue
        checked[stem] = n
        fm, body = n["fm"], n["body"]
        low = stem.lower()

        if n["is_meta"]:
            has_meta = True
        if low in LEDGER_NAMES:
            has_ledger = True

        if fm is None:
            errors.append({"id": "E001", "message": f"{rel}: no frontmatter"})
            continue

        ntype = str(fm.get("type", "")).lower()
        if ntype == "moc" or "moc" in low or low in MOC_NAMES:
            has_moc = True

        for k in CORE_KEYS:
            if k == "title":
                continue
            if k not in fm or fm[k] in ("", [], None):
                errors.append({"id": "E002", "message": f"{rel}: missing `{k}`"})

        s = str(fm.get("summary", ""))
        if s and not (120 <= len(s) <= 240):
            errors.append({"id": "E003", "message": f"{rel}: summary length {len(s)} (120–240)"})

        kw = fm.get("keywords", [])
        if isinstance(kw, list) and kw and not (6 <= len(kw) <= 8):
            errors.append({"id": "E004", "message": f"{rel}: keywords count {len(kw)} (6–8)"})

        ents = fm.get("entities", [])
        if isinstance(ents, list):
            if ents:
                entity_count += 1
            for e in ents:
                if isinstance(e, dict) and str(e.get("type", "")).lower() not in ENTITY_TYPES:
                    errors.append({"id": "E005", "message": f"{rel}: entity type `{e.get('type')}` not allowed"})

        note_id = fm.get("id")
        if not note_id:
            warnings.append({"id": "W003", "message": f"{rel}: missing `id` (required from v2.0; generate a ULID)"})
        elif not ULID_RE.match(str(note_id)):
            warnings.append({"id": "W004", "message": f"{rel}: `id` is not a valid ULID: `{note_id}`"})

        for t_raw in fm.get("links", []) or []:
            t = str(t_raw).strip()
            if ULID_RE.match(t):
                pass  # id-first resolution: accepted, full resolution skipped in minimal check
            elif t not in all_stems:
                errors.append({"id": "E009", "message": f"{rel}: links target `{t}` does not exist"})

        if ntype == "document":
            frags = fm.get("fragments", []) or []
            if len(frags) < 2:
                errors.append({"id": "E010", "message": f"{rel}: document with {len(frags)} fragments (≥2)"})
            for f in frags:
                if str(f) not in all_stems:
                    errors.append({"id": "E011", "message": f"{rel}: fragment `{f}` does not exist"})

    # Phase 3: vault-level checks (only when not checking a single note)
    if not target_rel:
        for stem, n in checked.items():
            low = stem.lower()
            if (incoming.get(stem, 0) == 0 and not n["is_meta"]
                    and low not in LEDGER_NAMES and "moc" not in low and low not in MOC_NAMES):
                errors.append({"id": "E007", "message": f"{n['rel']}: orphan (no incoming link)"})
        if not has_moc:
            errors.append({"id": "E012", "message": "vault: no MOC note (type: moc, or Home/00-Index)"})
        if not has_meta:
            errors.append({"id": "E013", "message": "vault: no meta note (§5.4)"})
        if not has_ledger:
            errors.append({"id": "E014", "message": "vault: no open-questions ledger (§5.3)"})
        if checked and entity_count / len(checked) < 0.80:
            pct = f"{entity_count / len(checked):.0%}"
            errors.append({
                "id": "E015",
                "message": f"vault: entities coverage {entity_count}/{len(checked)} = {pct} (<80%)",
            })

    return {
        "errors": errors,
        "warnings": warnings,
        "notes_checked": len(checked),
        "conformant": len(errors) == 0,
    }


# ── VaultIndex ───────────────────────────────────────────────────────────────

class VaultIndex:
    """In-memory index of all Mosaix notes in a vault directory."""

    def __init__(self, vault_path: Path) -> None:
        self.root = vault_path
        self._notes: dict[str, dict] = {}       # stem → {path, rel, fm, body, is_meta}
        self._by_rel: dict[str, str] = {}       # normalised rel → stem
        self._all_stems: dict[str, Path] = {}   # all .md stems (incl. excluded dirs)
        self._scan()

    def __len__(self) -> int:
        return len(self._notes)

    def _scan(self) -> None:
        """Walk vault and build in-memory index."""
        for p in self.root.rglob("*.md"):
            rel_parts = p.relative_to(self.root).parts
            self._all_stems.setdefault(p.stem, p)
            if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
                continue
            rel = "/".join(rel_parts)
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            fm, body = parse_frontmatter(text)
            if fm is not None:
                fm = normalise(fm)
            is_meta = (p.stem.lower() in META_NAMES
                       or any(part.lower() in META_DIRS for part in rel_parts[:-1]))
            self._notes[p.stem] = {"path": p, "rel": rel, "fm": fm, "body": body, "is_meta": is_meta}
            self._by_rel[rel.lower()] = p.stem
            self._by_rel[rel.lower().removesuffix(".md")] = p.stem

    def _resolve(self, path: str) -> tuple[str, dict]:
        """Resolve a user path to (stem, note_info). Raises KeyError if not found."""
        key = path.lower().rstrip("/").replace("\\", "/")
        if key in self._by_rel:
            stem = self._by_rel[key]
            return stem, self._notes[stem]
        stem = Path(path).stem
        if stem in self._notes:
            return stem, self._notes[stem]
        raise KeyError(f"Note not found: {path!r}")

    # ── public tools ────────────────────────────────────────────────────────

    def read_note(self, path: str) -> dict:
        """Read a note. Returns {frontmatter, body, path}."""
        stem, n = self._resolve(path)
        return {"frontmatter": n["fm"] or {}, "body": n["body"], "path": n["rel"]}

    def search(self, query: str, field: str | None = None) -> list[dict]:
        """Substring search across frontmatter fields. Returns ≤20 results by score."""
        q = query.lower()
        fields = [field] if field else ["summary", "keywords", "title"]
        results: list[dict] = []

        for stem, n in self._notes.items():
            fm = n["fm"] or {}
            score = 0
            for f in fields:
                if f == "title":
                    score += str(fm.get("title", stem)).lower().count(q)
                elif f == "summary":
                    score += str(fm.get("summary", "")).lower().count(q)
                elif f == "keywords":
                    kw = fm.get("keywords", [])
                    if isinstance(kw, list):
                        score += sum(q in str(k).lower() for k in kw)
                elif f == "entities":
                    ents = fm.get("entities", [])
                    if isinstance(ents, list):
                        score += sum(q in str(e.get("name", "")).lower()
                                     for e in ents if isinstance(e, dict))
                elif f == "body":
                    score += n["body"].lower().count(q)
            if score > 0:
                results.append({
                    "path": n["rel"],
                    "title": fm.get("title", stem),
                    "summary": fm.get("summary", ""),
                    "score": score,
                })

        results.sort(key=lambda x: -x["score"])
        return results[:20]

    def list_notes(self, tag: str | None = None, note_type: str | None = None) -> list[dict]:
        """List notes with optional tag/type filter, sorted by updated descending."""
        out: list[dict] = []
        for stem, n in self._notes.items():
            fm = n["fm"] or {}
            if note_type and str(fm.get("type", "")).lower() != note_type.lower():
                continue
            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            if tag and tag not in [str(t) for t in (tags or [])]:
                continue
            out.append({
                "path": n["rel"],
                "title": fm.get("title", stem),
                "type": fm.get("type", ""),
                "tags": tags or [],
                "updated": str(fm.get("updated", "")),
            })
        out.sort(key=lambda x: x["updated"] or "", reverse=True)
        return out

    def compose(self, path: str) -> dict:
        """Assemble a composed document from its fragment notes."""
        stem, n = self._resolve(path)
        fm = n["fm"] or {}
        if str(fm.get("type", "")).lower() != "document":
            raise ValueError(f"{n['rel']!r} is not type: document")
        frags = fm.get("fragments", []) or []
        if not frags:
            raise ValueError(f"{n['rel']}: no fragments declared")

        parts: list[str] = []
        frag_paths: list[str] = []
        for frag_name in frags:
            frag_stem = str(frag_name).strip()
            if frag_stem in self._notes:
                frag_n = self._notes[frag_stem]
                frag_paths.append(frag_n["rel"])
                parts.append(frag_n["body"].strip())
            elif frag_stem in self._all_stems:
                raise ValueError(f"Fragment {frag_name!r} exists but is in an excluded directory")
            else:
                raise ValueError(f"Fragment not found: {frag_name!r}")

        return {
            "path": n["rel"],
            "title": fm.get("title", stem),
            "fragments": frag_paths,
            "composed_text": "\n\n---\n\n".join(parts),
        }

    def check(self, path: str | None = None) -> dict:
        """Run §10 conformance check on one note or the entire vault."""
        target_rel: str | None = None
        if path:
            try:
                _, n = self._resolve(path)
                target_rel = n["rel"]
            except KeyError:
                raise ValueError(f"Note not found: {path!r}")
        return _check(self._notes, self._all_stems, target_rel)

    def write_note(self, path: str, frontmatter: dict, body: str) -> dict:
        """Validate and write a note. Applies R7 supersede if file already exists."""
        violations = _validate_note(frontmatter)
        if violations:
            raise ValueError("Validation failed:\n" + "\n".join(f"  - {v}" for v in violations))

        rel = path.lstrip("/").replace("\\", "/")
        target = self.root / rel
        superseded_path: str | None = None

        if target.exists():
            # R7: rename old with _superseded suffix
            old_stem = target.stem
            candidate = target.with_name(f"{old_stem}_superseded.md")
            counter = 1
            while candidate.exists():
                candidate = target.with_name(f"{old_stem}_superseded_{counter}.md")
                counter += 1
            old_text = target.read_text(encoding="utf-8")
            old_fm, old_body = parse_frontmatter(old_text)
            old_fm = old_fm or {}
            old_fm["status"] = "superseded"
            old_fm["superseded_by"] = rel
            candidate.write_text(serialize_frontmatter(old_fm) + old_body, encoding="utf-8")
            superseded_path = "/".join(candidate.relative_to(self.root).parts)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialize_frontmatter(frontmatter) + body, encoding="utf-8")

        # Update in-memory index
        fm_norm = normalise(dict(frontmatter))
        is_meta = (target.stem.lower() in META_NAMES
                   or any(p.lower() in META_DIRS for p in Path(rel).parts[:-1]))
        self._notes[target.stem] = {"path": target, "rel": rel, "fm": fm_norm, "body": body, "is_meta": is_meta}
        self._by_rel[rel.lower()] = target.stem
        self._by_rel[rel.lower().removesuffix(".md")] = target.stem
        self._all_stems[target.stem] = target

        return {"path": rel, "created": superseded_path is None, "superseded": superseded_path}
