"""Smoke tests for mosaix.parser."""
import textwrap
import tempfile
from pathlib import Path

import pytest

from mosaix import parse_note, Note


SAMPLE = textwrap.dedent("""\
    ---
    title: Test Note
    id: 01JZZZZZZZZZZZZZZZZZZZZZZA
    updated: "2026-09-09"
    tags: [test, mosaix]
    summary: This is a test summary that must be between 120 and 240 characters long, so here is some additional padding text to make it reach the minimum.
    keywords: [alpha, beta, gamma, delta, epsilon, zeta]
    rev: abc123def456
    ---
    Body content here.
""")


def _write_tmp(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


def test_parse_returns_note():
    p = _write_tmp(SAMPLE)
    note = parse_note(p)
    assert isinstance(note, Note)
    p.unlink()


def test_parse_title():
    p = _write_tmp(SAMPLE)
    note = parse_note(p)
    assert note.title == "Test Note"
    p.unlink()


def test_parse_id():
    p = _write_tmp(SAMPLE)
    note = parse_note(p)
    assert note.id == "01JZZZZZZZZZZZZZZZZZZZZZZA"
    p.unlink()


def test_parse_keywords():
    p = _write_tmp(SAMPLE)
    note = parse_note(p)
    assert len(note.keywords) == 6
    p.unlink()


def test_parse_no_frontmatter():
    p = _write_tmp("Just body text, no frontmatter.")
    note = parse_note(p)
    assert note.frontmatter_raw is None
    assert note.body == "Just body text, no frontmatter."
    p.unlink()


def test_parse_body():
    p = _write_tmp(SAMPLE)
    note = parse_note(p)
    assert "Body content here" in note.body
    p.unlink()
