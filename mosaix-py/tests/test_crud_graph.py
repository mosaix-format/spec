"""Tests for mosaix.crud and mosaix.graph."""
from __future__ import annotations

import hashlib
import re
import tempfile
from pathlib import Path

import pytest

from mosaix import parse_note, create_note, update_frontmatter, delete_note, VaultGraph

ULID_RE = re.compile(r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")

# Conformance fixtures live two directories above mosaix-py
CONFORMANCE = Path(__file__).parent.parent.parent / "tests" / "conformance"
VALID_VAULT = CONFORMANCE / "valid"
ORPHAN_VAULT = CONFORMANCE / "edge-cases" / "e007_orphan_vault"


# ---------- CRUD tests ----------

def test_create_note_generates_ulid(tmp_path):
    p = tmp_path / "note.md"
    fm = {
        "title": "Test",
        "updated": "2026-09-09",
        "tags": ["test"],
        "summary": "x" * 120,
        "keywords": ["a", "b", "c", "d", "e", "f"],
        "rev": "abc123",
    }
    create_note(p, fm)
    note = parse_note(p)
    assert note.id is not None, "id should have been auto-generated"
    assert ULID_RE.match(note.id), f"id {note.id!r} is not a valid ULID"


def test_create_note_preserves_explicit_id(tmp_path):
    p = tmp_path / "note.md"
    explicit = "01JZZZZZZZZZZZZZZZZZZZZZZA"
    create_note(p, {"title": "T", "id": explicit})
    note = parse_note(p)
    assert note.id == explicit


def test_create_note_frontmatter_round_trip(tmp_path):
    p = tmp_path / "note.md"
    fm = {
        "title": "Round Trip",
        "updated": "2026-09-09",
        "tags": ["alpha", "beta"],
        "summary": "y" * 130,
        "keywords": ["k1", "k2", "k3", "k4", "k5", "k6"],
        "rev": "deadbeef",
    }
    create_note(p, fm, body="Hello world.\n")
    note = parse_note(p)
    assert note.title == "Round Trip"
    assert note.tags == ["alpha", "beta"]
    assert len(note.keywords) == 6
    assert ULID_RE.match(note.id)


def test_update_frontmatter_body_byte_identical(tmp_path):
    p = tmp_path / "note.md"
    body = "Hello\nworld\n\nParagraph with special chars: €, ñ, 日本語.\n"
    create_note(p, {"title": "Body Test", "rev": "000"}, body=body)

    # Body string as parse_frontmatter returns it (what update_frontmatter preserves)
    note_before = parse_note(p)
    h_before = hashlib.sha256(note_before.body.encode("utf-8")).hexdigest()

    update_frontmatter(p, {"rev": "111", "status": "sourced"})

    note_after = parse_note(p)
    h_after = hashlib.sha256(note_after.body.encode("utf-8")).hexdigest()

    assert h_before == h_after, "body changed after update_frontmatter"


def test_update_frontmatter_changes_applied(tmp_path):
    p = tmp_path / "note.md"
    create_note(p, {"title": "Old", "rev": "aaa"})
    update_frontmatter(p, {"title": "New", "rev": "bbb"})
    note = parse_note(p)
    assert note.title == "New"


def test_delete_note_raises(tmp_path):
    p = tmp_path / "del.md"
    with pytest.raises(NotImplementedError):
        delete_note(p)


# ---------- Graph tests ----------

def test_valid_vault_zero_orphans():
    assert VALID_VAULT.exists(), f"missing fixture: {VALID_VAULT}"
    g = VaultGraph(VALID_VAULT)
    orphans = g.orphans()
    assert orphans == [], f"unexpected orphans: {[o.name for o in orphans]}"


def test_valid_vault_zero_broken_links():
    assert VALID_VAULT.exists(), f"missing fixture: {VALID_VAULT}"
    g = VaultGraph(VALID_VAULT)
    broken = g.broken_links()
    assert broken == [], f"unexpected broken links: {broken}"


def test_orphan_vault_detects_orphan():
    assert ORPHAN_VAULT.exists(), f"missing fixture: {ORPHAN_VAULT}"
    g = VaultGraph(ORPHAN_VAULT)
    orphans = g.orphans()
    stems = {o.stem for o in orphans}
    assert "orphan_note" in stems, f"orphan_note not detected; got: {stems}"


def test_orphan_vault_excludes_structural():
    """MOC, meta, and ledger notes must not appear in orphans()."""
    assert ORPHAN_VAULT.exists(), f"missing fixture: {ORPHAN_VAULT}"
    g = VaultGraph(ORPHAN_VAULT)
    orphan_stems = {o.stem for o in g.orphans()}
    assert "moc" not in orphan_stems
    assert "conventions" not in orphan_stems
    assert "open questions" not in orphan_stems


def test_graph_note_and_edge_count():
    assert VALID_VAULT.exists(), f"missing fixture: {VALID_VAULT}"
    g = VaultGraph(VALID_VAULT)
    assert g.note_count() > 0
    assert g.edge_count() > 0


def test_graph_components_non_empty():
    assert VALID_VAULT.exists(), f"missing fixture: {VALID_VAULT}"
    g = VaultGraph(VALID_VAULT)
    comps = g.components()
    assert len(comps) > 0
    assert all(len(c) > 0 for c in comps)
