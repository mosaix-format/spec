#!/usr/bin/env python3
"""
run_conformance.py — stdlib-only conformance test runner for Mosaix Format.

Usage:
    python tests/run_conformance.py

Prerequisite: audit_reference.py must be in the same directory as this script
              (i.e. the repository root), or on sys.path.

For each entry in tests/conformance/expected.json:
  - File entry  ("dir/file.md"): runs audit_reference.py on the parent directory,
    filters the JSON output for messages that mention the specific file, then checks
    that every expected error/warning code is present for that file.
  - Directory entry ("dir/subdir/"): runs audit_reference.py on that directory,
    then checks vault-level (non-file-prefixed) messages for expected codes.

Semantics:
  - For VALID file entries  (expected errors=[], warnings=[]): PASS only if no
    per-file messages are produced.
  - For INVALID/WARNING file entries: PASS if all expected codes are found in the
    per-file messages. Extra codes that appear only in the baseline-noise set
    (defined below) do not cause a failure, because scaffold notes in the same
    directory may produce them.
  - For directory entries: PASS only when the found vault-level codes exactly
    match the expected set (no extras, no missing).
  - W008 is only checked when "flags": ["--check-rev"] appears in expected.json.

Exit: 0 if all tests pass, 1 otherwise.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent          # tests/
REPO_ROOT    = SCRIPT_DIR.parent              # spec/ root
CHECKER      = REPO_ROOT / "audit_reference.py"
SUITE_DIR    = SCRIPT_DIR / "conformance"
EXPECTED_FILE = SUITE_DIR / "expected.json"

# ── code-detection signatures ─────────────────────────────────────────────────
# Each code is identified by a unique substring in the checker's output messages.
# Vault-level codes (E012-E015, W006) start with "vault:".

CODE_SIG: dict[str, str] = {
    # More-specific patterns are listed before less-specific ones to avoid
    # substring collisions when detect_codes breaks after the first match.
    "E001": "no frontmatter",
    "E003": "summary length",
    "E004": "keywords count",
    "E005": "entity type `",
    "E006": "broken link",
    "E007": "orphan (no incoming link)",
    "E008": "links id `",
    "E009": "links target `",
    "E010": "document with",
    "E011": "fragment `",
    "E012": "no MOC note",
    "E013": "no meta note",
    "E014": "no open-questions",
    "E015": "entities coverage",
    "W001": "entities (>12)",
    "W002": "relation type `",
    # W003 must come before E002: both contain "missing `" but W003 is more specific
    "W003": "missing `id`",
    "W004": "`id` is not a valid ULID",
    "W005": "tag #",
    "W006": "meta note declares no tags",
    "W007": "no reliability marker",
    "W008": "rev may be stale",
    # E002 must come last among these: "missing `" is a substring of W003's message
    "E002": "missing `",
}

# Codes that may appear legitimately in the scaffold context of per-file tests.
# We allow these as "noise" and don't fail a per-file test because of them.
BASELINE_NOISE: set[str] = {"W003", "W006", "E015"}

# ── helpers ───────────────────────────────────────────────────────────────────

def detect_codes(messages: list[str]) -> set[str]:
    """Map a list of checker message strings to a set of matching error/warning codes."""
    found: set[str] = set()
    for msg in messages:
        for code, sig in CODE_SIG.items():
            if sig in msg:
                found.add(code)
                break  # one message → one code (signatures are unique)
    return found


def messages_for_file(all_messages: list[str], rel_path: str) -> list[str]:
    """
    Filter checker messages that pertain to a specific file.
    The checker prefixes file-level messages with the file's vault-relative path
    (e.g. "E001_no_frontmatter.md: no frontmatter").
    We match by filename (basename with .md extension).
    """
    filename = Path(rel_path).name          # e.g. "E001_no_frontmatter.md"
    prefix   = filename + ":"              # e.g. "E001_no_frontmatter.md:"
    return [m for m in all_messages
            if m.startswith(prefix) or ("/" + prefix) in m or ("\\" + prefix) in m]


def run_checker(vault_dir: Path, extra_flags: list[str] | None = None) -> dict:
    """Run audit_reference.py on vault_dir and return the parsed JSON result."""
    cmd = [sys.executable, str(CHECKER), str(vault_dir), "--json"]
    if extra_flags:
        cmd.extend(extra_flags)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(cmd, capture_output=True, env=env)
    try:
        return json.loads(result.stdout.decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, Exception):
        return {"errors": [], "warnings": [], "notes": 0}


# ── test logic ────────────────────────────────────────────────────────────────

def run_tests(expected: dict) -> tuple[int, int]:
    """
    Run all test cases. Returns (pass_count, fail_count).
    """
    passed = 0
    failed = 0
    results: list[tuple[str, str, str]] = []  # (status, key, detail)

    # Cache checker results per vault directory to avoid re-running.
    _cache: dict[str, dict] = {}

    def get_result(vault_path: Path, flags: list[str]) -> dict:
        key = str(vault_path) + "|" + " ".join(flags)
        if key not in _cache:
            _cache[key] = run_checker(vault_path, flags)
        return _cache[key]

    for entry_key, spec in expected.items():
        if entry_key.startswith("_"):
            continue  # skip comment keys

        expected_errors: list[str] = spec.get("errors", [])
        expected_warnings: list[str] = spec.get("warnings", [])
        extra_flags: list[str] = spec.get("flags", [])

        is_dir_entry = entry_key.endswith("/")

        if is_dir_entry:
            # ── vault-level test ──────────────────────────────────────────────
            # Scan ALL messages (vault: and per-file) — directory tests assert
            # which codes appear anywhere in the vault audit result.
            vault_path = SUITE_DIR / entry_key.rstrip("/")
            if not vault_path.is_dir():
                results.append(("SKIP", entry_key, f"directory not found: {vault_path}"))
                continue

            r = get_result(vault_path, extra_flags)
            found_errors   = detect_codes(r.get("errors", []))
            found_warnings = detect_codes(r.get("warnings", []))

            exp_e = set(expected_errors)
            exp_w = set(expected_warnings)

            ok = (found_errors == exp_e) and (found_warnings == exp_w)
            if ok:
                passed += 1
                results.append(("PASS", entry_key, ""))
            else:
                failed += 1
                detail_parts = []
                missing_e = exp_e - found_errors
                extra_e   = found_errors - exp_e
                missing_w = exp_w - found_warnings
                extra_w   = found_warnings - exp_w
                if missing_e: detail_parts.append(f"missing errors: {sorted(missing_e)}")
                if extra_e:   detail_parts.append(f"unexpected errors: {sorted(extra_e)}")
                if missing_w: detail_parts.append(f"missing warnings: {sorted(missing_w)}")
                if extra_w:   detail_parts.append(f"unexpected warnings: {sorted(extra_w)}")
                results.append(("FAIL", entry_key, "; ".join(detail_parts)))

        else:
            # ── file-level test ───────────────────────────────────────────────
            file_path = SUITE_DIR / entry_key
            if not file_path.exists():
                results.append(("SKIP", entry_key, f"file not found: {file_path}"))
                continue

            vault_path = file_path.parent
            r = get_result(vault_path, extra_flags)

            all_errors   = r.get("errors", [])
            all_warnings = r.get("warnings", [])

            file_errors   = messages_for_file(all_errors, entry_key)
            file_warnings = messages_for_file(all_warnings, entry_key)

            found_errors   = detect_codes(file_errors)
            found_warnings = detect_codes(file_warnings)

            exp_e = set(expected_errors)
            exp_w = set(expected_warnings)

            is_valid_test = not exp_e and not exp_w

            if is_valid_test:
                # Valid notes: zero per-file messages expected.
                ok = not found_errors and not found_warnings
                if ok:
                    passed += 1
                    results.append(("PASS", entry_key, ""))
                else:
                    failed += 1
                    detail = f"unexpected errors: {sorted(found_errors)}; unexpected warnings: {sorted(found_warnings)}"
                    results.append(("FAIL", entry_key, detail))
            else:
                # Invalid/warning notes: expected codes must be present; baseline noise is allowed.
                missing_e = exp_e - found_errors
                missing_w = exp_w - found_warnings
                unexpected_e = found_errors - exp_e - BASELINE_NOISE
                unexpected_w = found_warnings - exp_w - BASELINE_NOISE

                ok = not missing_e and not missing_w and not unexpected_e and not unexpected_w
                if ok:
                    passed += 1
                    results.append(("PASS", entry_key, ""))
                else:
                    failed += 1
                    detail_parts = []
                    if missing_e:     detail_parts.append(f"missing errors: {sorted(missing_e)}")
                    if unexpected_e:  detail_parts.append(f"unexpected errors: {sorted(unexpected_e)}")
                    if missing_w:     detail_parts.append(f"missing warnings: {sorted(missing_w)}")
                    if unexpected_w:  detail_parts.append(f"unexpected warnings: {sorted(unexpected_w)}")
                    results.append(("FAIL", entry_key, "; ".join(detail_parts)))

    # ── report ────────────────────────────────────────────────────────────────
    width = max((len(k) for _, k, _ in results), default=20)
    for status, key, detail in results:
        marker = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "SKIP")
        line = f"  {marker} {key:<{width}}"
        if detail:
            line += f"  <- {detail}"
        print(line)

    total = passed + failed
    skipped = sum(1 for s, _, _ in results if s == "SKIP")
    print()
    print(f"Results: {passed}/{total} passed", end="")
    if skipped:
        print(f", {skipped} skipped", end="")
    print()

    return passed, failed


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> int:
    if not CHECKER.exists():
        print(f"ERROR: checker not found at {CHECKER}", file=sys.stderr)
        print("Run from the spec/ repository root or ensure audit_reference.py is present.")
        return 2

    if not EXPECTED_FILE.exists():
        print(f"ERROR: expected.json not found at {EXPECTED_FILE}", file=sys.stderr)
        return 2

    with EXPECTED_FILE.open(encoding="utf-8") as f:
        expected = json.load(f)

    print(f"Mosaix conformance suite — {len([k for k in expected if not k.startswith('_')])} test cases")
    print()

    _, failed = run_tests(expected)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
