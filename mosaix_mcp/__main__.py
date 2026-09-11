"""Entry point: python -m mosaix_mcp [vault_path] [--writable] [--verbose]"""
import sys
from pathlib import Path


def main() -> None:
    args = sys.argv[1:]
    vault_args = [a for a in args if not a.startswith("--")]
    vault_path = None
    if vault_args:
        vault_path = Path(vault_args[0]).resolve()
        if not vault_path.is_dir():
            print(f"mosaix-mcp: vault directory not found: {vault_path}", file=sys.stderr)
            sys.exit(1)
    writable = "--writable" in args
    verbose = "--verbose" in args
    from .server import run
    run(vault_path, writable=writable, verbose=verbose)


main()
