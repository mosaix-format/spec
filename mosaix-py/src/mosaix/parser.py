"""parse_note(path) → Note dataclass."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ._yaml import parse_frontmatter, normalise


@dataclass
class Entity:
    name: str
    type: str


@dataclass
class Relation:
    from_: str  # 'from' is a Python keyword
    type: str
    to: str


@dataclass
class Note:
    path: Path
    title: str
    id: str | None
    updated: str | None
    tags: list[str]
    summary: str | None
    keywords: list[str]
    entities: list[Entity]
    relations: list[Relation]
    links: list[str]
    rev: str | None
    body: str
    frontmatter_raw: dict | None = field(repr=False)

    @property
    def frontmatter(self) -> dict:
        return self.frontmatter_raw or {}


def _to_entity(d: Any) -> Entity:
    if isinstance(d, dict):
        return Entity(name=str(d.get("name", "")), type=str(d.get("type", "")))
    return Entity(name=str(d), type="")


def _to_relation(d: Any) -> Relation:
    if isinstance(d, dict):
        return Relation(
            from_=str(d.get("from", d.get("from_", ""))),
            type=str(d.get("type", "")),
            to=str(d.get("to", "")),
        )
    return Relation(from_="", type=str(d), to="")


def parse_note(path: Path | str) -> Note:
    """Parse a single Mosaix-format markdown file into a Note."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    fm_raw, body = parse_frontmatter(text)
    fm = normalise(fm_raw) if fm_raw is not None else {}

    def _list(key: str) -> list:
        v = fm.get(key)
        return v if isinstance(v, list) else ([] if v is None else [v])

    return Note(
        path=path,
        title=str(fm.get("title", path.stem)),
        id=fm.get("id") or None,
        updated=fm.get("updated") or None,
        tags=_list("tags"),
        summary=fm.get("summary") or None,
        keywords=_list("keywords"),
        entities=[_to_entity(e) for e in _list("entities")],
        relations=[_to_relation(r) for r in _list("relations")],
        links=[str(x) for x in _list("links")],
        rev=fm.get("rev") or None,
        body=body,
        frontmatter_raw=fm_raw,
    )
