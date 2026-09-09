"""Conformance test: validate_vault on the canonical valid corpus."""
from pathlib import Path

from mosaix import validate_vault

VALID_VAULT = Path(__file__).parent.parent.parent / "tests" / "conformance" / "valid"


def test_valid_vault_is_conformant():
    report = validate_vault(VALID_VAULT)
    errors = [f"{i.code}: {i.message}" for i in report.errors]
    assert report.is_conformant, f"Unexpected errors:\n" + "\n".join(errors)
