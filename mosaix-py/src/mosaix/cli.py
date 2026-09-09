"""CLI: mosaix check <vault> [--json] [--check-rev] [--verbose]"""
from __future__ import annotations

import argparse
import json as _json
import sys
from pathlib import Path

from .validator import validate_vault


def main() -> None:
    parser = argparse.ArgumentParser(prog="mosaix", description="Mosaix Format tools")
    sub = parser.add_subparsers(dest="command")

    check = sub.add_parser("check", help="Validate a vault")
    check.add_argument("vault", type=Path)
    check.add_argument("--json", action="store_true", help="Output JSON")
    check.add_argument("--check-rev", action="store_true", help="Check rev digest")
    check.add_argument("--verbose", action="store_true", help="Show all issues")
    check.add_argument(
        "--exclude",
        default="",
        metavar="PATHS",
        help="Comma-separated path prefixes to exclude",
    )

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # command == "check"
    vault = args.vault.resolve()
    exclude = tuple(x.strip() for x in args.exclude.split(",") if x.strip())
    report = validate_vault(vault, check_rev=args.check_rev, exclude=exclude)

    if args.json:
        data = {
            "vault": str(vault),
            "errors": [{"code": i.code, "message": i.message, "path": i.path} for i in report.errors],
            "warnings": [{"code": i.code, "message": i.message, "path": i.path} for i in report.warnings],
            "conformant": report.conformant,
        }
        print(_json.dumps(data, ensure_ascii=False, indent=2))
    else:
        status = "CONFORMANT" if report.conformant else "NOT CONFORMANT"
        print(f"Mosaix audit — {vault}")
        print(f"errors: {len(report.errors)}  warnings: {len(report.warnings)}  {status}")
        for issue in report.errors:
            print(f"  E  [{issue.code}] {issue.message}")
        if args.verbose or not report.errors:
            for issue in report.warnings:
                print(f"  W  [{issue.code}] {issue.message}")

    if report.errors:
        sys.exit(1)
    if report.warnings:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
