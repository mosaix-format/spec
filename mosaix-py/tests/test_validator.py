"""Conformance test: validate_vault on the canonical valid corpus."""
from pathlib import Path

from mosaix import validate_vault, VaultGraph

VALID_VAULT = Path(__file__).parent.parent.parent / "tests" / "conformance" / "valid"


def test_valid_vault_is_conformant():
    report = validate_vault(VALID_VAULT)
    errors = [f"{i.code}: {i.message}" for i in report.errors]
    assert report.is_conformant, f"Unexpected errors:\n" + "\n".join(errors)


def test_superseded_note_not_orphan():
    """R7: _superseded copies have no incoming links by construction.
    They must NOT trigger E007 in validate_vault or appear in VaultGraph.orphans().
    """
    # validator: no E007 for Home_superseded
    report = validate_vault(VALID_VAULT)
    e007_paths = [i.path for i in report.errors if i.code == "E007"]
    for p in e007_paths:
        assert "superseded" not in (p or "").lower(), (
            f"E007 raised on superseded note: {p}"
        )

    # graph: orphans() must not include _superseded stems
    g = VaultGraph(VALID_VAULT)
    orphan_stems = [p.stem for p in g.orphans()]
    for stem in orphan_stems:
        assert not stem.endswith("_superseded"), (
            f"VaultGraph.orphans() includes superseded note: {stem}"
        )
