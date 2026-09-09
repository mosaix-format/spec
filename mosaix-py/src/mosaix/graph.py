"""VaultGraph: orphans, broken_links, connected components — stdlib only."""
from __future__ import annotations

import re
from pathlib import Path

from ._yaml import parse_frontmatter, normalise

WIKILINK = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
ULID_RE = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")
EXCLUDED_DIRS = {"_inbox", "_private", ".obsidian", ".git", "node_modules", ".trash", "__pycache__", ".vault-ingest"}

META_NAMES = {"conventions", "metodo e convenzioni", "claude", "readme", "taxonomy", "tag index", "tassonomia", "indice tag"}
META_DIRS = {"_meta", "99-meta", "meta"}
LEDGER_NAMES = {"open questions", "assunzioni da confermare", "domande aperte"}
MOC_NAMES = {"home", "00-index", "index", "00-indice", "indice"}


class VaultGraph:
    """Directed link graph over a Mosaix vault."""

    def __init__(self, vault: Path | str) -> None:
        self.vault = Path(vault)
        self._stems: dict[str, Path] = {}         # stem → path
        self._id_to_stem: dict[str, str] = {}     # ULID id → stem
        self._edges: dict[str, set[str]] = {}     # stem → {stem, ...} (outgoing)
        self._incoming: dict[str, set[str]] = {}  # stem → {stem, ...}
        self._types: dict[str, str | None] = {}   # stem → type field
        self._build()

    def _build(self) -> None:
        files: list[tuple[Path, str]] = []
        for p in self.vault.rglob("*.md"):
            rel_parts = p.relative_to(self.vault).parts
            if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
                continue
            self._stems[p.stem] = p
            files.append((p, p.stem))

        for p, stem in files:
            text = p.read_text(encoding="utf-8", errors="replace")
            fm_raw, body = parse_frontmatter(text)
            fm = normalise(fm_raw) if fm_raw else {}
            if isinstance(fm.get("id"), str):
                self._id_to_stem[fm["id"]] = stem
            self._types[stem] = (fm.get("type") or None)
            self._edges.setdefault(stem, set())
            self._incoming.setdefault(stem, set())

        for p, stem in files:
            text = p.read_text(encoding="utf-8", errors="replace")
            fm_raw, body = parse_frontmatter(text)
            fm = normalise(fm_raw) if fm_raw else {}

            # wikilinks in body
            for target in WIKILINK.findall(body):
                t = target.strip().split("/")[-1]
                if t in self._stems:
                    self._edges[stem].add(t)
                    self._incoming.setdefault(t, set()).add(stem)

            # frontmatter links
            for link in fm.get("links", []) or []:
                t = str(link).strip()
                if ULID_RE.match(t) and t in self._id_to_stem:
                    dest = self._id_to_stem[t]
                elif t in self._stems:
                    dest = t
                else:
                    continue
                self._edges[stem].add(dest)
                self._incoming.setdefault(dest, set()).add(stem)

    # ------------------------------------------------------------------

    def _is_structural(self, stem: str) -> bool:
        """Return True if the note is a MOC, meta note, or ledger (excluded from orphan check)."""
        s = stem.lower()
        if s in META_NAMES or s in LEDGER_NAMES or s in MOC_NAMES:
            return True
        path = self._stems[stem]
        if path.parent.name.lower() in META_DIRS:
            return True
        typ = (self._types.get(stem) or "").lower()
        if typ in {"moc", "meta", "ledger"}:
            return True
        return False

    def orphans(self) -> list[Path]:
        """Notes with no incoming links, excluding MOC, meta, and ledger notes."""
        return [
            self._stems[s]
            for s in self._stems
            if not self._incoming.get(s) and not self._is_structural(s)
        ]

    def broken_links(self) -> list[tuple[Path, str]]:
        """(source_path, target_stem) pairs where target_stem is not in the vault."""
        broken = []
        for p in self.vault.rglob("*.md"):
            rel_parts = p.relative_to(self.vault).parts
            if any(part in EXCLUDED_DIRS for part in rel_parts[:-1]):
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            _, body = parse_frontmatter(text)
            for target in WIKILINK.findall(body):
                t = target.strip().split("/")[-1]
                if "." not in t and t not in self._stems:
                    broken.append((p, target.strip()))
        return broken

    def components(self) -> list[list[Path]]:
        """Connected components (undirected). Returns list of groups, largest first."""
        undirected: dict[str, set[str]] = {s: set() for s in self._stems}
        for src, dests in self._edges.items():
            for d in dests:
                undirected[src].add(d)
                undirected.setdefault(d, set()).add(src)

        visited: set[str] = set()
        groups: list[list[Path]] = []
        for stem in self._stems:
            if stem in visited:
                continue
            stack = [stem]
            component: list[Path] = []
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                if node in self._stems:
                    component.append(self._stems[node])
                for nbr in undirected.get(node, set()):
                    if nbr not in visited:
                        stack.append(nbr)
            groups.append(component)
        groups.sort(key=len, reverse=True)
        return groups

    def note_count(self) -> int:
        return len(self._stems)

    def edge_count(self) -> int:
        return sum(len(dests) for dests in self._edges.values())
