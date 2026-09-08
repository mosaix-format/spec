#!/usr/bin/env python3
"""
mosaix_migrate.py — bring existing vaults to Mosaix Format v1.0 conformance.

Standard library only. Reads .md files, infers missing CORE keys from content,
and writes updated frontmatter. Does NOT modify note bodies.

Usage:
    python mosaix_migrate.py <vault_dir> [--dry-run] [--git-dates]

--dry-run     Show what would change without writing any files.
--git-dates   Use `git log --format=%aI -1 -- <file>` for the `updated` date.
              Falls back to filesystem mtime if git is unavailable or the file
              is not tracked.

© 2026 Andrea Fiorino — CC BY-SA 4.0 (same licence as the specification).
"""
from __future__ import annotations

import hashlib
import random
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

CORE_KEYS = ("title", "updated", "tags", "summary", "keywords", "rev")
ALL_INFERRED = ("title", "id", "updated", "tags", "status", "summary",
                "keywords", "entities", "relations", "links", "rev")

EXCLUDED_DIRS = frozenset({
    "_inbox", "_private", ".obsidian", ".git", "node_modules",
    ".trash", "__pycache__", ".vault-ingest",
})

META_DIRS   = frozenset({"_meta", "99-meta", "meta"})
META_NAMES  = frozenset({
    "conventions", "metodo e convenzioni", "claude", "readme",
    "taxonomy", "tag index", "tassonomia", "indice tag",
})
LEDGER_NAMES = frozenset({"open questions", "assunzioni da confermare", "domande aperte"})
MOC_NAMES   = frozenset({"home", "00-index", "index", "00-indice", "indice"})

# Italian → English canonical mapping (§3.1 KEY_ALIASES)
KEY_ALIASES: dict[str, str] = {
    "titolo": "title",
    "aggiornato": "updated",
    "riassunto": "summary",
    "parole_chiave": "keywords",
    "mcp_entita": "entities",
    "mcp_relazioni": "relations",
    "mcp_collegamenti": "links",
    "mcp_rev": "rev",
    "mcp_frammenti": "fragments",
    "mcp_pool": "pool",
    "mcp_layout": "layout",
    "tipo": "type",
    "stato": "status",
}

# ── ULID generation ────────────────────────────────────────────────────────────

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid() -> str:
    """Generate a valid ULID (48-bit ms timestamp + 80-bit random, Crockford Base32)."""
    ms = int(time.time() * 1000)
    rand = random.getrandbits(80)
    # Timestamp: 10 chars (48-bit value encoded in 50 bits → top 2 bits always 0 → first char 0-7)
    ts_chars: list[str] = []
    v = ms & 0xFFFFFFFFFFFF
    for _ in range(10):
        ts_chars.append(_CROCKFORD[v & 0x1F])
        v >>= 5
    ts_chars.reverse()
    # Random: 16 chars (80 bits)
    rand_chars: list[str] = []
    for _ in range(16):
        rand_chars.append(_CROCKFORD[rand & 0x1F])
        rand >>= 5
    rand_chars.reverse()
    return "".join(ts_chars) + "".join(rand_chars)


# ── Stopwords (EN + IT, ~200 words) ───────────────────────────────────────────

_STOPWORDS = frozenset("""
a about above after again against all also am an and any are arent as at
be because been before being below between both but by cant cannot could
couldnt did didnt do does doesnt doing dont down during each few for from
further get got had hadnt has hasnt have havent having he hed hell hes her
here heres hers herself him himself his how hows i id ill im ive if in
into is isnt it its itself lets me more most mustnt my myself no nor not
of off on once only or other ought our ours ourselves out over own same
shant she shed shell shes should shouldnt so some such than that thats
the their theirs them themselves then there theres these they theyd theyll
theyre theyve this those through to too under until up very was wasnt we
wed well were weve were werent what whats when whens where wheres which
while who whos whom why whys will with wont would wouldnt you youd youll
youre youve your yours yourself yourselves
a ad agli al alla alle allo anche avere avevano aveva avevo
chi ci cio come con cosa cui
da dagli dal dalla dalle dallo degli dei del della dello delle di dove
e ed era erano essere
fa fare fatto fu
gli
ha hanno ho
i il in io
la le li lo loro
ma me mia mio mi
ne nel nella nello nell nelle non
o
per poi pure però
qui
se si sia siamo siete siano sono sua sue sul sulla sulle suo suoi
ti tra tu tua tue tuo tuoi
un una uno uno
vi
""".split())


# ── Regex ──────────────────────────────────────────────────────────────────────

_WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
_BODY_TAG  = re.compile(r"(?<![\w/&])#((?![0-9A-Fa-f]{3,8}\b)[A-Za-z][A-Za-z0-9_/\-]*)")
_H1        = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_TOKEN     = re.compile(r"[A-Za-zÀ-ÿ]{3,}")
_ULID_RE   = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")


# ── Frontmatter split ──────────────────────────────────────────────────────────

def _split_frontmatter(text: str) -> tuple[str | None, str, int]:
    """
    Return (raw_fm_block, body, close_pos).
    raw_fm_block is the YAML content between the two --- markers (may start with \\n).
    close_pos is the index in text where \\n--- ends (text[close_pos + 4:] is the body).
    Returns (None, text, -1) when no valid frontmatter is found.
    """
    if not text.startswith("---"):
        return None, text, -1
    end = text.find("\n---", 3)
    if end < 0:
        return None, text, -1
    raw = text[3:end]        # YAML block (starts with \n)
    body = text[end + 4:]    # content after \n---
    return raw, body, end


def _fm_keys(raw: str) -> dict[str, str]:
    """
    Extract top-level YAML keys from a raw frontmatter block.
    Returns {canonical_key: original_key_name}.
    Only processes unindented lines (top-level keys).
    """
    found: dict[str, str] = {}
    for line in raw.splitlines():
        if not line or line[0] in (" ", "\t", "#", "-"):
            continue
        if ":" in line:
            k = line.split(":")[0].strip()
            if k:
                canon = KEY_ALIASES.get(k, k)
                found[canon] = k
    return found


# ── Inference helpers ──────────────────────────────────────────────────────────

def _infer_title(path: Path, body: str) -> str:
    m = _H1.search(body)
    if m:
        return m.group(1).strip()
    stem = re.sub(r"[-_]+", " ", path.stem)
    return stem.title()


def _mtime_date(path: Path) -> str:
    return time.strftime("%Y-%m-%d", time.localtime(path.stat().st_mtime))


def _git_date(path: Path) -> str | None:
    try:
        r = subprocess.run(
            ["git", "log", "--format=%aI", "-1", "--", str(path)],
            capture_output=True, text=True, timeout=5,
        )
        out = r.stdout.strip()
        if out:
            return out[:10]
    except Exception:
        pass
    return None


def _infer_updated(path: Path, git_dates: bool) -> str:
    if git_dates:
        d = _git_date(path)
        if d:
            return d
    return _mtime_date(path)


def _extract_body_tags(body: str) -> list[str]:
    """Extract inline Obsidian-style #tags from body, skipping heading lines."""
    seen: set[str] = set()
    result: list[str] = []
    for line in body.splitlines():
        s = line.lstrip()
        # Skip ATX headings: # ... ## ... etc. (# followed by space)
        if s.startswith("#") and (len(s) < 2 or s[1] in (" ", "\t", "#")):
            continue
        for m in _BODY_TAG.finditer(line):
            t = m.group(1)
            if t not in seen:
                seen.add(t)
                result.append(t)
    return result


def _infer_summary(body: str) -> str:
    """
    Extract 120–240 chars of plain text from body, cutting at the last sentence
    boundary (period or semicolon) within that window.
    Uses the full body if shorter than 120 chars.
    Returns empty string if body is essentially empty.
    """
    # Strip wikilink syntax and resolve to display text
    clean = _WIKILINK.sub(lambda m: m.group(1), body)
    # Remove heading markers
    clean = re.sub(r"^#+\s+", "", clean, flags=re.MULTILINE)
    # Collapse whitespace within each paragraph, then join paragraphs with space
    # Collapse all whitespace (including soft line breaks within a paragraph) to single spaces
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n{2,}", clean)]
    text = " ".join(p for p in paras if p)

    if not text:
        return ""
    if len(text) <= 120:
        return text
    if len(text) <= 240:
        return text

    # Find last sentence boundary in 120–240 range (scan backwards from 240)
    window = min(240, len(text) - 1)
    for i in range(window, 119, -1):
        if text[i] in ".;":
            return text[: i + 1]

    # No boundary found — cut at 240, respecting word boundary
    cut = text[:240]
    last_space = cut.rfind(" ")
    return cut[:last_space] if last_space > 120 else cut


def _infer_keywords(body: str, title: str) -> list[str]:
    """Top 6–8 significant words by frequency, supplemented from title if needed."""
    tokens = _TOKEN.findall((body + " " + title).lower())
    counts = Counter(
        t for t in tokens
        if t not in _STOPWORDS and len(t) >= 4
    )
    top = [w for w, _ in counts.most_common(8)]
    if len(top) < 6:
        for w in _TOKEN.findall(title.lower()):
            if w not in _STOPWORDS and len(w) >= 4 and w not in top:
                top.append(w)
                if len(top) == 6:
                    break
    return top[:8]


def _extract_links(body: str) -> list[str]:
    """Extract wikilink targets from body, deduplicated, in order of appearance."""
    seen: set[str] = set()
    result: list[str] = []
    for m in _WIKILINK.finditer(body):
        t = m.group(1).strip()
        if t and t not in seen:
            seen.add(t)
            result.append(t)
    return result


def _rev(body: str) -> str:
    return hashlib.sha256(body.strip().encode("utf-8")).hexdigest()[:12]


# ── YAML serialisation (for appended keys only) ────────────────────────────────

def _yaml_str(v: str) -> str:
    """Serialise a string value for YAML, quoting when necessary."""
    special = set(':"\'\n#[]{}|>&*!%@`')
    if not v:
        return '""'
    if any(c in v for c in special) or v[0] == " " or v[-1] == " ":
        escaped = (
            v.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'
    return v


def _yaml_list(items: list) -> str:
    """Serialise a list as a YAML flow sequence."""
    if not items:
        return "[]"
    parts = []
    for x in items:
        if isinstance(x, str):
            parts.append(_yaml_str(x) if any(c in x for c in '",[]{}:') else x)
        else:
            parts.append(str(x))
    return "[" + ", ".join(parts) + "]"


def _append_keys(raw_fm: str, additions: dict) -> str:
    """
    Append new key: value lines to a raw frontmatter block.
    Returns the updated block (retains the original content verbatim).
    """
    new_lines: list[str] = []
    for k, v in additions.items():
        if isinstance(v, list):
            new_lines.append(f"{k}: {_yaml_list(v)}")
        elif isinstance(v, str):
            new_lines.append(f"{k}: {_yaml_str(v)}")
        else:
            new_lines.append(f"{k}: {v}")

    if raw_fm.strip():
        # Preserve existing content exactly; append after a single newline
        return raw_fm.rstrip("\n") + "\n" + "\n".join(new_lines) + "\n"
    else:
        # Fresh frontmatter block (no prior content)
        return "\n".join(new_lines) + "\n"


# ── Single-file migration ──────────────────────────────────────────────────────

def migrate_file(
    path: Path,
    vault: Path,
    dry_run: bool,
    git_dates: bool,
) -> tuple[bool, dict]:
    """
    Inspect one .md file and add missing CORE keys + id/status.

    Returns (modified, additions_dict).
    modified=False means the file was already conformant (or unreadable/unparseable).
    In dry_run mode the file is never written; additions_dict still shows what would change.
    """
    try:
        # utf-8-sig strips the BOM that some editors (and PowerShell 5.1) prepend
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError as exc:
        print(f"  ⚠ Cannot read {path.relative_to(vault)}: {exc}", file=sys.stderr)
        return False, {}

    raw_fm, body, close_pos = _split_frontmatter(text)

    # Paranoid guard: if frontmatter marker found but position lost, skip safely
    if raw_fm is not None and close_pos < 0:
        print(
            f"  ⚠ Unclosed frontmatter in {path.relative_to(vault)}, skipping",
            file=sys.stderr,
        )
        return False, {}

    existing = _fm_keys(raw_fm) if raw_fm is not None else {}

    def missing(key: str) -> bool:
        return key not in existing

    # Infer title early (shared by keywords and fallback)
    title = _infer_title(path, body)

    additions: dict = {}

    if missing("title"):
        additions["title"] = title
    if missing("id"):
        additions["id"] = _ulid()
    if missing("updated"):
        additions["updated"] = _infer_updated(path, git_dates)
    if missing("status"):
        additions["status"] = "to-confirm"
    if missing("tags"):
        tags = _extract_body_tags(body)
        additions["tags"] = tags  # may be [] — tells the user to fill it in
    if missing("summary"):
        s = _infer_summary(body)
        if s:
            additions["summary"] = s
    if missing("keywords"):
        kw = _infer_keywords(body, title)
        additions["keywords"] = kw  # may be [] for very short or stop-word-only bodies
    if missing("entities"):
        additions["entities"] = []
    if missing("relations"):
        additions["relations"] = []
    if missing("links"):
        additions["links"] = _extract_links(body)
    if missing("rev"):
        additions["rev"] = _rev(body)

    if not additions:
        return False, {}

    if dry_run:
        return True, additions

    # Reconstruct the file with new keys appended to the frontmatter block
    if raw_fm is not None:
        new_fm = _append_keys(raw_fm, additions)
        new_text = "---" + new_fm + "---" + text[close_pos + 4:]
    else:
        new_fm = _append_keys("", additions)
        new_text = "---\n" + new_fm + "---\n" + text

    path.write_text(new_text, encoding="utf-8")
    return True, additions


# ── Vault structure helpers ────────────────────────────────────────────────────

def _is_meta(path: Path, vault: Path) -> bool:
    rel_parts = path.relative_to(vault).parts
    return (
        path.stem.lower() in META_NAMES
        or any(part.lower() in META_DIRS for part in rel_parts[:-1])
    )


def _collect_all_tags(vault: Path) -> list[str]:
    """Aggregate all tags found across vault: frontmatter tags + inline body #tags."""
    seen: set[str] = set()
    for p in vault.rglob("*.md"):
        rel_parts = p.relative_to(vault).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
            continue
        try:
            text = p.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        raw_fm, body, _ = _split_frontmatter(text)
        # Frontmatter tags (simple extraction: find tags: [...] or tags:\n  - x lines)
        if raw_fm:
            in_tags = False
            for line in raw_fm.splitlines():
                stripped = line.strip()
                if not in_tags:
                    m = re.match(r"^tags\s*:\s*(.*)", stripped)
                    if m:
                        rest = m.group(1).strip()
                        if rest.startswith("[") and rest.endswith("]"):
                            for t in rest[1:-1].split(","):
                                t = t.strip().strip("\"'")
                                if t:
                                    seen.add(t)
                        elif rest:
                            seen.add(rest.strip("\"'"))
                        else:
                            in_tags = True
                else:
                    if stripped.startswith("- "):
                        t = stripped[2:].strip().strip("\"'")
                        if t:
                            seen.add(t)
                    elif stripped and not stripped.startswith("#"):
                        in_tags = False
        # Inline body tags
        for t in _extract_body_tags(body):
            seen.add(t)
    return sorted(seen)


def _normalize_stem(stem: str) -> str:
    """Normalise a file stem for name-based detection (lowercase, hyphens/underscores → spaces)."""
    return re.sub(r"[-_]+", " ", stem).lower()


def _full_fm(
    title: str,
    ntype: str,
    tags: list[str],
    summary: str,
    keywords: list[str],
    body: str,
    extra: dict | None = None,
) -> str:
    """Build a complete Mosaix frontmatter block for a generated vault-structure file."""
    today = time.strftime("%Y-%m-%d")
    note_id = _ulid()
    note_rev = _rev(body)
    lines = [
        f"title: {_yaml_str(title)}",
        f"id: {note_id}",
        f"type: {ntype}",
        f"updated: {today}",
        f"tags: {_yaml_list(tags)}",
        "status: sourced",
        f"summary: {_yaml_str(summary)}",
        f"keywords: {_yaml_list(keywords)}",
        "entities: []",
        "relations: []",
        "links: []",
        f"rev: {note_rev}",
    ]
    if extra:
        for k, v in extra.items():
            lines.append(f"{k}: {_yaml_str(str(v)) if isinstance(v, str) else v}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def _ensure_moc(vault: Path, dry_run: bool, note_stems: list[str]) -> tuple[bool, str]:
    """Create Home.md if no MOC exists. Returns (created, rel_path)."""
    for p in vault.rglob("*.md"):
        low = p.stem.lower()
        if low in MOC_NAMES or "moc" in low:
            return False, str(p.relative_to(vault)).replace("\\", "/")

    moc_path = vault / "Home.md"
    rel = "Home.md"
    links_block = "\n".join(f"- [[{s}]]" for s in sorted(note_stems))
    body = (
        "\n# Home\n\n"
        "Map of content for this vault. "
        "An index of all notes — follow the links to any note.\n\n"
        "## Notes\n\n"
        f"{links_block}\n"
    )
    summary = (
        "Map of content for this vault. "
        "An index of all notes, organized as a starting point for exploration. "
        "Follow the links to any note."
    )
    keywords = ["home", "index", "map", "content", "vault", "notes"]
    fm = _full_fm("Home", "moc", ["moc"], summary, keywords, body)
    content = fm + body
    if not dry_run:
        moc_path.write_text(content, encoding="utf-8")
    return True, rel


def _ensure_meta(
    vault: Path, dry_run: bool, all_tags: list[str]
) -> tuple[bool, str]:
    """Create _meta/meta.md if no meta note exists. Returns (created, rel_path)."""
    for p in vault.rglob("*.md"):
        if _is_meta(p, vault):
            return False, str(p.relative_to(vault)).replace("\\", "/")

    meta_dir = vault / "_meta"
    meta_path = meta_dir / "meta.md"
    rel = "_meta/meta.md"
    # Declare moc and ledger tags in addition to vault-specific ones
    declared_tags = sorted(set(all_tags) | {"moc", "ledger"})
    tag_lines = "\n".join(f"- #{t}" for t in declared_tags) or "(none found)"
    body = (
        "\n# Vault Conventions\n\n"
        "Meta note for Mosaix Format v1.0. "
        "Declare your taxonomy, reliability convention, and domain keys here.\n\n"
        "Reliability: key `status` with values `sourced`, `to-confirm`, `superseded`.\n\n"
        f"## Tags\n\n{tag_lines}\n"
    )
    summary = (
        "Meta note for Mosaix Format v1.0 — declares the vault's tag taxonomy, "
        "reliability convention (status key: sourced, to-confirm, superseded), "
        "domain keys, entity types, and relation types."
    )
    keywords = ["conventions", "meta", "taxonomy", "tags", "reliability", "vault"]
    fm = _full_fm(
        "Vault Conventions", "meta", declared_tags, summary, keywords, body,
        extra={"mosaix": '"1.0"'},
    )
    content = fm + body
    if not dry_run:
        meta_dir.mkdir(exist_ok=True)
        meta_path.write_text(content, encoding="utf-8")
    return True, rel


def _ensure_ledger(vault: Path, dry_run: bool) -> tuple[bool, str]:
    """
    Create _meta/Open questions.md if no ledger exists. Returns (created, rel_path).
    The stem 'Open questions' matches audit_reference's LEDGER_NAMES ('open questions').
    """
    for p in vault.rglob("*.md"):
        # Normalise stem so "open-questions" also matches "open questions"
        if _normalize_stem(p.stem) in LEDGER_NAMES:
            return False, str(p.relative_to(vault)).replace("\\", "/")

    meta_dir = vault / "_meta"
    ledger_path = meta_dir / "Open questions.md"
    rel = "_meta/Open questions.md"
    body = (
        "\n# Open Questions\n\n"
        "Ledger of open questions and unverified assumptions.\n\n"
        "Add one entry per open question or assumption that needs to be resolved.\n"
    )
    summary = (
        "Ledger of open questions, unverified assumptions, and items requiring follow-up. "
        "Each entry records a question or assumption to be resolved or confirmed before "
        "a note can be marked sourced."
    )
    keywords = ["questions", "open", "ledger", "assumptions", "verify", "confirm"]
    fm = _full_fm("Open Questions", "ledger", ["ledger"], summary, keywords, body)
    content = fm + body
    if not dry_run:
        meta_dir.mkdir(exist_ok=True)
        ledger_path.write_text(content, encoding="utf-8")
    return True, rel


# ── Entry point ────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 2

    vault = Path(argv[1]).resolve()
    dry_run   = "--dry-run"   in argv
    git_dates = "--git-dates" in argv

    if not vault.is_dir():
        print(f"Error: {vault} is not a directory", file=sys.stderr)
        return 1

    # Collect all .md files (respecting EXCLUDED_DIRS)
    files: list[Path] = []
    for p in vault.rglob("*.md"):
        rel_parts = p.relative_to(vault).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
            continue
        files.append(p)
    files.sort()

    processed = 0
    modified  = 0
    skipped   = 0
    note_stems: list[str] = []

    for p in files:
        rel = str(p.relative_to(vault)).replace("\\", "/")
        processed += 1
        note_stems.append(p.stem)

        changed, additions = migrate_file(p, vault, dry_run, git_dates)

        if changed:
            modified += 1
            if dry_run:
                print(f"[DRY RUN] Would modify: {rel}")
                for k, v in additions.items():
                    if isinstance(v, list):
                        print(f"  + {k}: {_yaml_list(v)}")
                    else:
                        print(f"  + {k}: {_yaml_str(str(v))}")
        else:
            skipped += 1

    # Vault structure
    all_tags = _collect_all_tags(vault)
    moc_created,    moc_path    = _ensure_moc(vault, dry_run, note_stems)
    meta_created,   meta_path   = _ensure_meta(vault, dry_run, all_tags)
    ledger_created, ledger_path = _ensure_ledger(vault, dry_run)

    # ── Report ─────────────────────────────────────────────────────────────────
    prefix = "[DRY RUN] " if dry_run else ""
    print()
    print(f"{prefix}Migration complete.")
    print()
    print(f"  Notes processed:  {processed:6d}")
    print(f"  Notes modified:   {modified:6d}  (frontmatter added/updated)")
    print(f"  Notes skipped:    {skipped:6d}  (already conformant)")
    print()
    print("  Vault structure:")
    moc_label    = "(created)"    if moc_created    else "(existing)"
    meta_label   = f"(created, {len(all_tags)} tags collected)" if meta_created else "(existing)"
    ledger_label = "(created)"    if ledger_created else "(existing)"
    print(f"    MOC:              {moc_path} {moc_label}")
    print(f"    Meta note:        {meta_path} {meta_label}")
    print(f"    Ledger:           {ledger_path} {ledger_label}")
    print()
    if modified:
        print("  ⚠ All migrated notes have status: to-confirm")
        print("    Review each note and change to status: sourced when verified.")
        print()
    print(f"  Next: python audit_reference.py {argv[1]}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
