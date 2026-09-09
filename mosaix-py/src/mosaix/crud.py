"""CRUD operations for Mosaix notes — stdlib only."""
from __future__ import annotations

import secrets
import time
from pathlib import Path
from typing import Any

from ._yaml import parse_frontmatter

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _generate_ulid() -> str:
    """Generate a ULID: 48-bit ms timestamp + 80-bit random, Crockford Base32."""
    ts = int(time.time() * 1000) & 0xFFFFFFFFFFFF  # 48 bits
    rand = secrets.randbits(80)
    chars = [_CROCKFORD[(ts >> s) & 0x1F] for s in range(45, -1, -5)]
    chars += [_CROCKFORD[(rand >> s) & 0x1F] for s in range(75, -1, -5)]
    return "".join(chars)


def create_note(path: Path | str, frontmatter: dict[str, Any], body: str = "") -> Path:
    """Write a new Mosaix note. Auto-generates id (ULID) if absent. Raises FileExistsError if it already exists."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    fm = dict(frontmatter)
    if not fm.get("id"):
        fm["id"] = _generate_ulid()
    fm_block = _serialise_frontmatter(fm)
    path.write_text(f"---\n{fm_block}---\n{body}", encoding="utf-8")
    return path


def update_frontmatter(path: Path | str, changes: dict[str, Any]) -> None:
    """Rewrite only the frontmatter of a note, leaving the body byte-identical."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    fm_raw, body = parse_frontmatter(text)
    if fm_raw is None:
        raise ValueError(f"{path}: note has no frontmatter")
    fm_raw.update(changes)
    fm_block = _serialise_frontmatter(fm_raw)
    # body from parse_frontmatter already starts with \n (the separator after ---)
    path.write_text(f"---\n{fm_block}---{body}", encoding="utf-8")


def delete_note(path: Path | str) -> None:  # noqa: ARG001
    raise NotImplementedError("Use supersede, don't delete (R7)")


# ---------- internal serialiser ----------

def _serialise_frontmatter(fm: dict[str, Any]) -> str:
    lines = []
    for k, v in fm.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}:")
            else:
                lines.append(f"{k}:")
                for item in v:
                    if isinstance(item, dict):
                        pairs = ", ".join(f"{ik}: {iv}" for ik, iv in item.items())
                        lines.append(f"  - {{{pairs}}}")
                    else:
                        lines.append(f"  - {item}")
        elif v is None:
            lines.append(f"{k}:")
        else:
            sv = str(v)
            if any(c in sv for c in (':', '#', '[', ']', '{', '}')):
                sv = f'"{sv}"'
            lines.append(f"{k}: {sv}")
    return "\n".join(lines) + "\n"
