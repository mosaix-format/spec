"""Vault operations for Mosaix Format: read, write, search, compose, check, list."""
from __future__ import annotations

import hashlib
import math
import os
import re
from collections import defaultdict
from pathlib import Path

# ── Search mode ────────────────────────────────────────────────────────────────
# SEARCH_MODE env var: "reference" (default) = original substring count,
# "fusion" = BM25-like scoring on body + metadata field weighting.
# Used by benchmark F3/F4 to measure search quality delta.
SEARCH_MODE = os.environ.get("SEARCH_MODE", "reference")

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

# Suffisso che write_note applica alla versione precedente (R7)
SUPERSEDED_SUFFIX = "_superseded"


def is_superseded(stem: str, fm: dict | None) -> bool:
    """Una nota ritirata non e' contenuto vivo.

    R7 prescrive di marcare `status: superseded` (e write_note aggiunge il suffisso
    `_superseded` al nome file). Un documento ritirato non puo' avere link entranti nel
    momento in cui nasce, quindi segnalarlo come orfano (E007) e' un falso positivo:
    il controllo va saltato per queste note.
    """
    if str((fm or {}).get("status", "")).strip().lower() == "superseded":
        return True
    return SUPERSEDED_SUFFIX in stem.lower()

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


def _incoming(notes: dict[str, dict], all_stems: dict[str, Path]) -> dict[str, int]:
    """Link entranti per stem: wikilink nel body piu' voci `links` che esistono davvero.

    Serve sia al controllo degli orfani (E007) sia a `delete_note` (guardia: non si
    cancella una nota che qualcuno linka) e a `move_note` (i link vanno riscritti).
    """
    incoming: dict[str, int] = defaultdict(int)
    for n in notes.values():
        for target in set(WIKILINK.findall(n["body"])):
            incoming[target.strip().split("/")[-1]] += 1
        if n["fm"]:
            for t_raw in (n["fm"].get("links", []) or []):
                t = str(t_raw).strip()
                if not ULID_RE.match(t) and t in all_stems:
                    incoming[t] += 1
    return incoming


def _rewrite_wikilinks(text: str, old_stem: str, new_stem: str) -> tuple[str, int]:
    """Riscrive `[[vecchio]]` in `[[nuovo]]`, anche con alias, ancora o prefisso cartella."""
    count = 0

    def _sub(m: re.Match) -> str:
        nonlocal count
        target = m.group(1)
        prefix, _, last = target.rpartition("/")
        if last != old_stem:
            return m.group(0)
        count += 1
        new_target = f"{prefix}/{new_stem}" if prefix else new_stem
        return m.group(0).replace(target, new_target, 1)

    return WIKILINK.sub(_sub, text), count


# ── Conformance checker (§10 core rules) ────────────────────────────────────
def _check(
    notes: dict[str, dict],
    all_stems: dict[str, Path],
    target_rel: str | None,
) -> dict:
    """Minimal §10 conformance check. Returns errors/warnings dicts."""
    errors: list[dict] = []
    warnings: list[dict] = []

    # Phase 1: incoming link counts across ALL notes (needed for the orphan check)
    incoming = _incoming(notes, all_stems)

    # Phase 2: per-note checks
    checked: dict[str, dict] = {}
    has_moc = has_meta = has_ledger = False
    entity_count = 0

    for rel_key, n in notes.items():
        rel = n["rel"]
        if target_rel and rel != target_rel:
            continue
        checked[rel_key] = n
        fm, body = n["fm"], n["body"]
        stem = n["stem"]
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
        for _rel_key, n in checked.items():
            stem = n["stem"]
            low = stem.lower()
            if (incoming.get(stem, 0) == 0 and not n["is_meta"]
                    and not is_superseded(stem, n["fm"])
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
        # Chiave = path relativo, NON stem: `README` vive in decine di cartelle, e
        # indicizzare per stem teneva solo l'ultimo file letto — le altre note
        # sparivano da search/list_notes e un path completo ne restituiva un'altra.
        self._notes: dict[str, dict] = {}         # rel → {path, rel, stem, fm, body, is_meta}
        self._by_rel: dict[str, str] = {}         # normalised rel → rel
        self._by_stem: dict[str, list[str]] = {}  # stem → [rel, …]; >1 = ambiguo
        self._all_stems: dict[str, Path] = {}     # all .md stems (incl. excluded dirs)
        self._scan()

    def __len__(self) -> int:
        return len(self._notes)

    def _index_rel(self, rel: str) -> None:
        """Registra un path negli indici: per path (con e senza .md) e per stem."""
        low = rel.lower()
        self._by_rel[low] = rel
        self._by_rel[low.removesuffix(".md")] = rel
        stem = Path(rel).stem
        rels = self._by_stem.setdefault(stem, [])
        if rel not in rels:
            rels.append(rel)

    def _unindex_rel(self, rel: str) -> None:
        """Rimuove un path dagli indici.

        Non tocca `_all_stems`: copre anche le directory escluse e, per lo stesso
        stem, puo' puntare a un file diverso da questo.
        """
        for key in [k for k, v in self._by_rel.items() if v == rel]:
            self._by_rel.pop(key, None)
        stem = Path(rel).stem
        rels = self._by_stem.get(stem)
        if rels and rel in rels:
            rels.remove(rel)
            if not rels:
                self._by_stem.pop(stem, None)

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
            self._notes[rel] = {"path": p, "rel": rel, "stem": p.stem,
                                "fm": fm, "body": body, "is_meta": is_meta}
            self._index_rel(rel)

    def _resolve_ref(self, path: str) -> str | None:
        """Risolve path o stem a un rel. None se non esiste; ValueError se ambiguo."""
        key = str(path).strip().lower().rstrip("/").replace("\\", "/")
        if key in self._by_rel:
            return self._by_rel[key]
        rels = self._by_stem.get(str(path).strip(), [])
        if len(rels) == 1:
            return rels[0]
        if len(rels) > 1:
            raise ValueError(
                f"Ambiguous note name {str(path)!r}: {len(rels)} notes share it "
                f"({', '.join(sorted(rels)[:6])}{' …' if len(rels) > 6 else ''}). "
                f"Use the relative path."
            )
        return None

    def _resolve(self, path: str) -> tuple[str, dict]:
        """Resolve a user path to (rel, note_info). Raises KeyError if not found."""
        try:
            rel = self._resolve_ref(path)
        except ValueError as exc:
            raise KeyError(str(exc)) from exc
        if rel is None:
            raise KeyError(f"Note not found: {path!r}")
        return rel, self._notes[rel]

    # ── public tools ────────────────────────────────────────────────────────

    def read_note(self, path: str) -> dict:
        """Read a note. Returns {frontmatter, body, path}."""
        _rel, n = self._resolve(path)
        return {"frontmatter": n["fm"] or {}, "body": n["body"], "path": n["rel"]}

    def _search_fusion(self, query: str,
                       include_superseded: bool = False) -> list[dict]:
        """BM25-like fusion search: body + metadata field weighting.

        Three-branch scoring (approximation of production weights):
          - body:     BM25(body_text)        weight 0.55
          - meta:     BM25(summary+keywords) weight 0.25
          - title:    exact/partial match    weight 0.20

        BM25 params: k1=1.5, b=0.75 (standard).
        """
        k1, b = 1.5, 0.75
        q_terms = query.lower().split()
        if not q_terms:
            return []

        # Pre-compute average doc lengths
        body_lengths: list[int] = []
        meta_lengths: list[int] = []
        active_notes: list[tuple[str, dict]] = []

        for _rel, n in self._notes.items():
            if not include_superseded and is_superseded(n["stem"], n["fm"]):
                continue
            active_notes.append((_rel, n))
            body_lengths.append(len(n["body"].split()))
            fm = n["fm"] or {}
            meta_text = " ".join([
                str(fm.get("summary", "")),
                " ".join(str(k) for k in fm.get("keywords", []) if isinstance(fm.get("keywords"), list)),
                " ".join(str(e.get("name", "")) for e in fm.get("entities", [])
                         if isinstance(e, dict) and isinstance(fm.get("entities"), list)),
            ])
            meta_lengths.append(len(meta_text.split()))

        if not active_notes:
            return []

        N = len(active_notes)
        avgdl_body = sum(body_lengths) / N if N else 1
        avgdl_meta = sum(meta_lengths) / N if N else 1

        def bm25_score(text: str, dl: int, avgdl: float) -> float:
            """BM25 score for all query terms against a text."""
            words = text.lower().split()
            if not words:
                return 0.0
            score = 0.0
            for term in q_terms:
                tf = words.count(term) if len(term) >= 3 else text.lower().count(term)
                if tf == 0:
                    continue
                # IDF approximation: log(N / (df + 0.5)) — estimate df from tf presence
                # Since we compute per-document, use a simplified IDF
                idf = math.log(N + 1)  # constant boost, varies by corpus size
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * dl / avgdl)
                score += idf * numerator / denominator
            return score

        results: list[dict] = []
        for idx, (_rel, n) in enumerate(active_notes):
            fm = n["fm"] or {}

            # Branch 1: body (weight 0.55)
            body_score = bm25_score(n["body"], body_lengths[idx], avgdl_body)

            # Branch 2: metadata (weight 0.25)
            meta_text = " ".join([
                str(fm.get("summary", "")),
                " ".join(str(k) for k in fm.get("keywords", []) if isinstance(fm.get("keywords"), list)),
                " ".join(str(e.get("name", "")) for e in fm.get("entities", [])
                         if isinstance(e, dict) and isinstance(fm.get("entities"), list)),
            ])
            meta_score = bm25_score(meta_text, meta_lengths[idx], avgdl_meta)

            # Branch 3: title (weight 0.20)
            title = str(fm.get("title", n["stem"])).lower()
            title_score = 0.0
            for term in q_terms:
                if term in title:
                    title_score += 2.0  # exact substring bonus
                    if title.startswith(term) or f" {term}" in title:
                        title_score += 1.0  # prefix/word-boundary bonus

            # Fusion
            total = body_score * 0.55 + meta_score * 0.25 + title_score * 0.20

            if total > 0:
                results.append({
                    "path": n["rel"],
                    "title": fm.get("title", n["stem"]),
                    "summary": fm.get("summary", ""),
                    "score": round(total, 4),
                })

        results.sort(key=lambda x: -x["score"])
        return results[:20]

    def search(self, query: str, field: str | None = None,
               include_superseded: bool = False) -> list[dict]:
        """Search notes. Mode depends on SEARCH_MODE env var:
          - "reference": substring count across frontmatter fields (original)
          - "fusion": BM25 body + metadata field weighting (Mnemora approximation)

        Returns ≤20 results by score.
        """
        if SEARCH_MODE == "fusion" and field is None:
            return self._search_fusion(query, include_superseded)

        # Original reference search (substring count)
        q = query.lower()
        fields = [field] if field else ["summary", "keywords", "title"]
        results: list[dict] = []

        for _rel, n in self._notes.items():
            if not include_superseded and is_superseded(n["stem"], n["fm"]):
                continue
            fm = n["fm"] or {}
            score = 0
            for f in fields:
                if f == "title":
                    score += str(fm.get("title", n["stem"])).lower().count(q)
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
                    "title": fm.get("title", n["stem"]),
                    "summary": fm.get("summary", ""),
                    "score": score,
                })

        results.sort(key=lambda x: -x["score"])
        return results[:20]

    def list_notes(self, tag: str | None = None, note_type: str | None = None,
                   include_superseded: bool = False) -> list[dict]:
        """List notes with optional tag/type filter, sorted by updated descending.

        Le note ritirate (R7) restano fuori dal catalogo di default: sono storia. Si
        includono con `include_superseded=True`.
        """
        out: list[dict] = []
        for _rel, n in self._notes.items():
            if not include_superseded and is_superseded(n["stem"], n["fm"]):
                continue
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
                "title": fm.get("title", n["stem"]),
                "type": fm.get("type", ""),
                "tags": tags or [],
                "updated": str(fm.get("updated", "")),
            })
        out.sort(key=lambda x: x["updated"] or "", reverse=True)
        return out

    def compose(self, path: str, mode: str = "text", fragments: list[str] | None = None) -> dict:
        _rel, n = self._resolve(path)
        stem = n["stem"]
        fm = n["fm"] or {}
        if str(fm.get("type", "")).lower() != "document":
            raise ValueError(f"{n['rel']!r} is not type: document")
        frags = fm.get("fragments", []) or []
        if not frags:
            raise ValueError(f"{n['rel']}: no fragments declared")
        if fragments is not None:
            for f in fragments:
                if f not in frags:
                    raise ValueError(f"Fragment not requested by document: {f!r}")
        target_frags = fragments if fragments is not None else frags
        parts: list[str] = []
        frag_paths: list[str] = []
        frag_meta: list[dict] = []
        total_bytes = 0
        total_words = 0
        for frag_name in target_frags:
            frag_stem = str(frag_name).strip()
            frag_rel = self._resolve_ref(frag_stem)   # ValueError se lo stem e' ambiguo
            if frag_rel is not None:
                frag_n = self._notes[frag_rel]
                frag_paths.append(frag_n["rel"])
                body = frag_n["body"].strip()
                parts.append(body)
                b = len(body.encode("utf-8"))
                w = len(body.split())
                total_bytes += b
                total_words += w
                frag_meta.append({
                    "stem": frag_n["stem"],
                    "rel": frag_n["rel"],
                    "title": (frag_n["fm"] or {}).get("title", frag_n["stem"]),
                    "bytes": b,
                    "words": w,
                })
            elif frag_stem in self._all_stems:
                raise ValueError(f"Fragment {frag_name!r} exists but is in an excluded directory")
            else:
                raise ValueError(f"Fragment not found: {frag_name!r}")
        composed_text = "\n\n---\n\n".join(parts)
        if mode == "text":
            return {"path": n["rel"], "title": fm.get("title", n["stem"]),
                    "fragments": frag_paths, "composed_text": composed_text}
        if mode == "structure":
            return {"path": n["rel"], "title": fm.get("title", n["stem"]),
                    "fragments": frag_meta, "total_bytes": total_bytes,
                    "total_words": total_words}
        if mode == "file":
            out_dir = self.root / "_composed"
            out_dir.mkdir(parents=True, exist_ok=True)
            file_path = out_dir / f"{n['stem']}.txt"
            file_path.write_text(composed_text, encoding="utf-8", newline="")
            return {"path": n["rel"], "title": fm.get("title", n["stem"]),
                    "fragments": frag_paths, "composed_path": str(file_path),
                    "bytes": len(composed_text.encode("utf-8")),
                    "sha256": hashlib.sha256(composed_text.encode("utf-8")).hexdigest()}
        raise ValueError(f"unknown mode: {mode!r}")

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

    def delete_note(self, path: str, force: bool = False) -> dict:
        """Rimuovi una nota dal vault, con guardia sui link entranti (MCP-TOOL-SURFACE).

        Se altre note la linkano il server rifiuta, a meno di `force: true`. La via
        preferibile resta comunque R7: marcare `status: superseded` invece di cancellare.
        Il file viene rimosso dal disco, quindi non e' recuperabile.
        """
        rel, n = self._resolve(path)
        target = n["path"]
        if not target.exists():
            raise ValueError(f"Note not found on disk: {n['rel']!r}")

        incoming = _incoming(self._notes, self._all_stems).get(n["stem"], 0)
        if incoming and not force:
            raise ValueError(
                f"PERMISSION_DENIED: {n['rel']!r} has {incoming} incoming link(s). "
                f"Pass force: true to delete anyway, or prefer R7: mark it "
                f"`status: superseded` and keep the history."
            )

        target.unlink()
        self._notes.pop(rel, None)
        if self._all_stems.get(n["stem"]) == target:
            self._all_stems.pop(n["stem"], None)
        self._unindex_rel(rel)
        return {"path": rel, "deleted": True, "incoming_refs": incoming}

    def move_note(self, src: str, dst: str) -> dict:
        """Sposta o rinomina una nota riscrivendo i wikilink entranti (MCP-TOOL-SURFACE).

        La destinazione non deve esistere. I riferimenti `[[stem]]` nel body e le voci
        `links:` vengono aggiornati in tutte le note che puntavano al vecchio nome.
        """
        old_rel, n = self._resolve(src)
        old_stem = n["stem"]
        rel_dst = dst.lstrip("/").replace("\\", "/")
        if not rel_dst.endswith(".md"):
            rel_dst += ".md"
        new_stem = Path(rel_dst).stem
        target = self.root / rel_dst
        if target.exists():
            raise ValueError(f"{rel_dst!r} already exists")
        if rel_dst.lower() in self._by_rel:
            raise ValueError(f"PERMISSION_DENIED: {rel_dst!r} is already indexed")

        old_path = n["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(target)
        # il file e' gia' nella destinazione: aggiorno subito il path, perche' il loop
        # qui sotto riscrive i body passando da other["path"] e ricreerebbe il vecchio
        n["path"] = target

        updated = 0
        for _other_rel, other in self._notes.items():
            body, k = _rewrite_wikilinks(other["body"], old_stem, new_stem)
            fm = other["fm"] or {}
            links = fm.get("links")
            if isinstance(links, list):
                new_links = [new_stem if str(t).strip() == old_stem else t for t in links]
                if new_links != links:
                    fm["links"] = new_links
                    k += 1
            if k:
                updated += k
                other["body"] = body
                other["path"].write_text(
                    (serialize_frontmatter(fm) if other["fm"] else "") + body, encoding="utf-8")

        # gli archi di supersessione possono stare in file che l'indice non ha mai visto
        # (le copie R7 precedenti a un reindex): li cerco anche sul disco
        for p in self.root.rglob("*.md"):
            try:
                testo = p.read_text(encoding="utf-8")
            except OSError:
                continue
            fm_disk, body_disk = parse_frontmatter(testo)
            if not fm_disk:
                continue
            sb = fm_disk.get("superseded_by")
            if not isinstance(sb, str):
                continue
            if ULID_RE.match(sb.strip()):
                continue      # arco ancorato all'id: rename-proof per costruzione, non si tocca
            if self._key_of(sb) != old_rel:
                continue
            fm_disk["superseded_by"] = (rel_dst if ("/" in sb or sb.endswith(".md")) else new_stem)
            p.write_text(serialize_frontmatter(fm_disk) + body_disk, encoding="utf-8")
            updated += 1
            try:
                other_rel = p.relative_to(self.root).as_posix()
            except ValueError:
                continue
            if other_rel in self._notes:
                self._notes[other_rel]["fm"] = normalise(dict(fm_disk))

        self._notes.pop(old_rel, None)
        self._unindex_rel(old_rel)
        if self._all_stems.get(old_stem) == old_path:
            self._all_stems.pop(old_stem, None)

        n["rel"], n["stem"] = rel_dst, new_stem
        self._notes[rel_dst] = n
        self._index_rel(rel_dst)
        self._all_stems[new_stem] = target
        return {"from": old_rel, "to": rel_dst, "updated_refs": updated}

    def _key_of(self, target: str) -> str:
        """Risolve un riferimento a nota nella chiave d'indice (il rel): `id` ULID,
        stem, path o path senza .md.

        Gli archi R7 in circolazione usano entrambe le forme (`write_note` scrive il path
        relativo, i fixture della spec usano lo stem), quindi la risoluzione le accetta
        tutte. Se il riferimento non e' risolvibile torna la stringa grezza: l'arco resta
        nel grafo ma non entra nella catena, invece di puntare a una nota a caso.
        """
        t = target.strip()
        if ULID_RE.match(t):
            candidati = [rel for rel, x in self._notes.items()
                         if str((x["fm"] or {}).get("id", "")) == t]
            # una versione nuova e' una nota nuova e porta un id nuovo, ma se due note
            # condividono l'id (R7 copia il frontmatter verbatim) l'arco deve puntare
            # alla versione viva, non alla copia ritirata
            for rel in candidati:
                if not is_superseded(self._notes[rel].get("stem", ""), self._notes[rel]["fm"]):
                    return rel
            return candidati[0] if candidati else t
        try:
            rel = self._resolve_ref(t)
        except ValueError:
            return t          # stem ambiguo: non si sceglie a caso
        return rel if rel is not None else t

    def history(self, path: str) -> dict:
        """Catena delle versioni di una nota, percorrendo gli archi R7.

        Segue `superseded_by` in avanti e all'indietro (chi punta a questa nota), risolvendo
        ogni arco per stem o per `id`. Restituisce SOLO i metadati: id, updated, status,
        titolo. I corpi si leggono a parte, con `read_note`, se servono. E' il grafo di
        supersessione reso leggibile a costo di poche centinaia di byte.
        """
        start_rel, n = self._resolve(path)
        preds: dict[str, list[str]] = defaultdict(list)
        for s, x in self._notes.items():
            t = str((x["fm"] or {}).get("superseded_by", "")).strip()
            if t:
                preds[self._key_of(t)].append(s)

        seen = {start_rel}
        stack = [start_rel]
        while stack and len(seen) < 50:
            cur = stack.pop()
            nxt = list(preds.get(cur, []))
            t = str((self._notes[cur]["fm"] or {}).get("superseded_by", "")).strip()
            if t:
                k = self._key_of(t)
                if k in self._notes:
                    nxt.append(k)
            for x in nxt:
                if x not in seen:
                    seen.add(x)
                    stack.append(x)

        chain = []
        for s in seen:
            fm = self._notes[s]["fm"] or {}
            status = str(fm.get("status", "")).strip().lower()
            chain.append({"stem": self._notes[s]["stem"], "rel": self._notes[s]["rel"],
                          "id": str(fm.get("id", "")),
                          "title": str(fm.get("title", self._notes[s]["stem"])),
                          "updated": str(fm.get("updated", "")),
                          "status": status,
                          "superseded_by": str(fm.get("superseded_by", "")),
                          "current": status != "superseded"})
        chain.sort(key=lambda c: (c["updated"], c["stem"]))
        return {"path": self._notes[start_rel]["rel"], "chain_length": len(chain), "chain": chain}

    def write_note(self, path: str, frontmatter: dict, body: str,
                   supersede: bool = True) -> dict:
        """Validate and write a note.

        Con `supersede=True` (default) la versione precedente viene conservata secondo R7;
        con `supersede=False` il file viene sovrascritto in place, senza copie: serve per le
        correzioni che non meritano una versione (refusi, formattazione).
        """
        violations = _validate_note(frontmatter)
        if violations:
            raise ValueError("Validation failed:\n" + "\n".join(f"  - {v}" for v in violations))

        rel = path.lstrip("/").replace("\\", "/")
        target = self.root / rel
        superseded_path: str | None = None
        existed = target.exists()

        if existed and supersede:
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
            # Forma canonica dell'arco: l'id ULID del successore, che sopravvive ai rename
            # per costruzione. Fallback allo stem se il successore non porta id.
            new_id = str(normalise(dict(frontmatter)).get("id", "")).strip()
            old_fm["superseded_by"] = new_id if ULID_RE.match(new_id) else target.stem
            candidate.write_text(serialize_frontmatter(old_fm) + old_body, encoding="utf-8")
            superseded_path = "/".join(candidate.relative_to(self.root).parts)
            # il server ha appena creato questo file: l'indice deve saperlo, altrimenti
            # `history` non vede la versione precedente finche' non si chiama reindex
            self._notes[superseded_path] = {
                "path": candidate, "rel": superseded_path, "stem": candidate.stem,
                "fm": normalise(dict(old_fm)), "body": old_body,
                "is_meta": (candidate.stem.lower() in META_NAMES
                            or any(p.lower() in META_DIRS for p in Path(superseded_path).parts[:-1])),
            }
            self._index_rel(superseded_path)
            self._all_stems[candidate.stem] = candidate

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(serialize_frontmatter(frontmatter) + body, encoding="utf-8")

        # Update in-memory index
        fm_norm = normalise(dict(frontmatter))
        is_meta = (target.stem.lower() in META_NAMES
                   or any(p.lower() in META_DIRS for p in Path(rel).parts[:-1]))
        self._notes[rel] = {"path": target, "rel": rel, "stem": target.stem,
                            "fm": fm_norm, "body": body, "is_meta": is_meta}
        self._index_rel(rel)
        self._all_stems[target.stem] = target

        return {"path": rel, "created": not existed, "superseded": superseded_path,
                "overwritten": existed and superseded_path is None}
