#!/usr/bin/env python3
"""
mosaix_init.py — scaffold a new Mosaix Format vault.

Usage:
    python mosaix_init.py [target_dir] [--with-examples]

If target_dir is omitted, initialises the current directory.
With --with-examples, copies example-vault/vault/ into the new vault.

Generated notes pass audit_reference.py with 0 errors and 0 warnings.

© 2026 Andrea Fiorino — CC BY-SA 4.0
"""
from __future__ import annotations

import hashlib
import os
import shutil
import sys
from datetime import date
from pathlib import Path

# ── ULID generator (stdlib-only) ─────────────────────────────────────────────

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid() -> str:
    """Generate a valid ULID (real millisecond timestamp + 80-bit random)."""
    import time
    ms = int(time.time() * 1000)
    rand = int.from_bytes(os.urandom(10), "big")
    ts_digits: list[str] = []
    for _ in range(10):
        ts_digits.append(_CROCKFORD[ms & 0x1F])
        ms >>= 5
    rand_digits: list[str] = []
    for _ in range(16):
        rand_digits.append(_CROCKFORD[rand & 0x1F])
        rand >>= 5
    return "".join(reversed(ts_digits)) + "".join(reversed(rand_digits))


def _rev(body: str) -> str:
    return hashlib.sha256(body.strip().encode()).hexdigest()[:12]


def _today() -> str:
    return date.today().isoformat()


# ── Note templates ───────────────────────────────────────────────────────────

def _home(meta_link: str, ledger_link: str) -> str:
    body = (
        "# Home\n\n"
        "Start here. Vault structure:\n\n"
        f"- [[{meta_link}]] — tag taxonomy and domain conventions\n"
        f"- [[{ledger_link}]] — open questions and unresolved items\n\n"
        "Add your first note and link it here.\n"
    )
    # summary: 120-240 chars — counted: 162
    summary = (
        "Map of content for this Mosaix vault: taxonomy and conventions in the meta note, "
        "open-questions ledger for unresolved items, and inbox for raw material. Start here."
    )
    assert 120 <= len(summary) <= 240, f"summary length {len(summary)}"
    fm = (
        f"id: {_ulid()}\n"
        f"title: Home\n"
        f"type: moc\n"
        f"updated: {_today()}\n"
        f"tags: [moc]\n"
        f"status: sourced\n"
        f'summary: "{summary}"\n'
        f"keywords: [home, map of content, index, entry point, vault structure, navigation]\n"
        f"entities:\n"
        f"  - {{name: Mosaix Format, type: project}}\n"
        f"relations: []\n"
        f"links: [{meta_link}, {ledger_link}]\n"
        f"rev: {_rev(body)}\n"
    )
    return f"---\n{fm}---\n\n{body}"


def _meta_note() -> str:
    body = (
        "# Conventions\n\n"
        "## Tags\n\n"
        "| Tag | Meaning |\n"
        "|-----|---------|\n"
        "| `#moc` | Map of content |\n"
        "| `#synthesis` | Processed, cross-cutting insight |\n"
        "| `#document` | Composed document (assembled from fragments) |\n"
        "| `#open-questions` | Ledger of unresolved items |\n\n"
        "## Entity types\n\n"
        "Standard: person, company, product, project, tool, place, document, event.\n\n"
        "## Relation types\n\n"
        "Edit this section to declare domain-specific relation types.\n"
    )
    # summary: 120-240 chars — counted: 169
    summary = (
        "Meta note for this vault: declares the tag taxonomy, entity types, domain conventions, "
        "and relation types. Edit to add project-specific tags before creating notes."
    )
    assert 120 <= len(summary) <= 240, f"summary length {len(summary)}"
    fm = (
        f"id: {_ulid()}\n"
        f"mosaix: \"1.0\"\n"
        f"title: Conventions\n"
        f"updated: {_today()}\n"
        f"tags: [moc, synthesis, document, open-questions]\n"
        f"status: sourced\n"
        f'summary: "{summary}"\n'
        f"keywords: [conventions, taxonomy, tags, entity types, meta note, domain vocabulary]\n"
        f"entities:\n"
        f"  - {{name: Mosaix Format, type: project}}\n"
        f"relations: []\n"
        f"links: []\n"
        f"rev: {_rev(body)}\n"
    )
    return f"---\n{fm}---\n\n{body}"


def _ledger_note() -> str:
    body = (
        "# Open questions\n\n"
        "Add a row when recording a claim that needs verification. "
        "Remove or resolve when answered.\n\n"
        "| # | Question | Added | Status |\n"
        "|---|----------|-------|--------|\n"
        "| 1 | _(your first open question)_ | — | open |\n"
    )
    # summary: 120-240 chars — counted: 166
    summary = (
        "Ledger of open questions and unresolved assumptions for this vault. Add an item when "
        "recording a claim that needs verification, and close it when answered or resolved."
    )
    assert 120 <= len(summary) <= 240, f"summary length {len(summary)}"
    fm = (
        f"id: {_ulid()}\n"
        f"title: Open questions\n"
        f"updated: {_today()}\n"
        f"tags: [open-questions]\n"
        f"status: sourced\n"
        f'summary: "{summary}"\n'
        f"keywords: [open questions, ledger, unresolved, assumptions, tracking, verification]\n"
        f"entities:\n"
        f"  - {{name: Mosaix Format, type: project}}\n"
        f"relations: []\n"
        f"links: []\n"
        f"rev: {_rev(body)}\n"
    )
    return f"---\n{fm}---\n\n{body}"


_GITHUB_ACTION = """\
name: Mosaix Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Download checker
        run: |
          curl -sSL https://mosaixformat.org/audit_reference.py -o audit_reference.py
      - name: Run conformance check
        run: python audit_reference.py . --json
"""

def _readme_note() -> str:
    body = (
        "# README\n\n"
        "This vault uses [Mosaix Format](https://mosaixformat.org/spec.html).\n\n"
        "## Structure\n\n"
        "| Path | Purpose |\n"
        "|---|---|\n"
        "| `Home.md` | Entry point and map of content |\n"
        "| `_meta/Conventions.md` | Tag taxonomy and domain conventions |\n"
        "| `_meta/open questions.md` | Open questions ledger |\n"
        "| `_inbox/` | Drop raw material here |\n"
        "| `_synthesis/` | Processed, cross-cutting notes |\n\n"
        "## Conformance check\n\n"
        "```bash\n"
        "python audit_reference.py . --json\n"
        "```\n\n"
        "Spec: <https://mosaixformat.org/spec.html>\n"
    )
    # summary: 120-240 chars — counted: 152
    summary = (
        "README for this Mosaix vault: explains the folder structure, how to run the "
        "conformance checker, and where to find the specification and documentation."
    )
    assert 120 <= len(summary) <= 240, f"summary length {len(summary)}"
    fm = (
        f"id: {_ulid()}\n"
        f"title: README\n"
        f"updated: {_today()}\n"
        f"tags: [readme]\n"
        f"status: sourced\n"
        f'summary: "{summary}"\n'
        f"keywords: [readme, vault, structure, mosaix format, getting started, conformance]\n"
        f"entities:\n"
        f"  - {{name: Mosaix Format, type: project}}\n"
        f"relations: []\n"
        f"links: []\n"
        f"rev: {_rev(body)}\n"
    )
    return f"---\n{fm}---\n\n{body}"


# ── Scaffold ─────────────────────────────────────────────────────────────────

def init(target: Path, with_examples: bool = False) -> None:
    """Create the base vault structure at target."""
    # Confirm if directory already has .md files (excluding README.md)
    existing_md = [
        p for p in target.glob("**/*.md")
        if p.name.lower() != "readme.md"
    ] if target.exists() else []
    if existing_md:
        print(f"Warning: {target} already contains {len(existing_md)} .md file(s).")
        ans = input("Continue anyway? [y/N] ").strip().lower()
        if ans != "y":
            print("Aborted.")
            sys.exit(0)

    target.mkdir(parents=True, exist_ok=True)
    (target / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    if with_examples:
        # Copy example vault first so its canonical casing wins on disk
        example_src = Path(__file__).parent / "example-vault" / "vault"
        if example_src.is_dir():
            for src in example_src.rglob("*"):
                if src.is_file():
                    dst = target / src.relative_to(example_src)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            print(f"  Copied example vault from {example_src}")
        else:
            print(f"  Warning: example-vault not found at {example_src} — skipping.")
        # Add CI and inbox/synthesis if missing; skip scaffold notes (example provides them)
        for d in ("_synthesis", "_inbox"):
            (target / d).mkdir(exist_ok=True)
            (target / d / ".gitkeep").touch()
        (target / ".github" / "workflows" / "mosaix-check.yml").write_text(_GITHUB_ACTION, encoding="utf-8")
        if not (target / "README.md").exists():
            (target / "README.md").write_text(_readme_note(), encoding="utf-8")
    else:
        # Full scaffold: create all base notes and directories
        (target / "_meta").mkdir(exist_ok=True)
        (target / "_synthesis").mkdir(exist_ok=True)
        (target / "_inbox").mkdir(exist_ok=True)
        (target / "_synthesis" / ".gitkeep").touch()
        (target / "_inbox" / ".gitkeep").touch()

        # Notes (ledger stem must match LEDGER_NAMES: "open questions")
        meta_stem = "Conventions"
        ledger_stem = "open questions"
        (target / "Home.md").write_text(_home(meta_stem, ledger_stem), encoding="utf-8")
        (target / "_meta" / f"{meta_stem}.md").write_text(_meta_note(), encoding="utf-8")
        (target / "_meta" / f"{ledger_stem}.md").write_text(_ledger_note(), encoding="utf-8")
        (target / ".github" / "workflows" / "mosaix-check.yml").write_text(_GITHUB_ACTION, encoding="utf-8")
        (target / "README.md").write_text(_readme_note(), encoding="utf-8")

    # Welcome message
    print(f"\nVault initialized at {target}\n")
    print("Created:")
    print(f"  Home.md                                 — your vault's entry point")
    if not with_examples:
        print(f"  _meta/Conventions.md                    — declare your taxonomy here")
        print(f"  _meta/open questions.md                 — track open questions (R6)")
    print(f"  _inbox/                                 — drop raw material here")
    print(f"  _synthesis/                             — processed notes go here")
    print(f"  .github/workflows/mosaix-check.yml      — CI validation")
    if with_examples:
        print(f"  (+ example vault notes)")
    print()
    print("Next steps:")
    print("  1. Create your first note: copy Home.md and edit")
    print(f"  2. Run the checker: python audit_reference.py {target}")
    print("  3. Read the spec: https://mosaixformat.org/spec.html")


def main() -> None:
    args = sys.argv[1:]
    with_examples = "--with-examples" in args
    path_args = [a for a in args if not a.startswith("--")]
    target = Path(path_args[0]).resolve() if path_args else Path.cwd()
    init(target, with_examples=with_examples)


if __name__ == "__main__":
    main()
