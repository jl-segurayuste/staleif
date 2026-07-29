from __future__ import annotations

import argparse
import sys
from pathlib import Path

from staleif.analyze import analyze_repo
from staleif.report import to_console, to_json


def _cmd_scan(args: argparse.Namespace) -> int:
    repo_path = Path(args.path).resolve()
    findings = analyze_repo(repo_path)

    if findings is None:
        print("No aplica: no hay 'requires-python' en pyproject.toml, o no es un repo git.")
        return 0

    if args.json:
        print(to_json(findings))
    else:
        print(to_console(findings))

    if args.fail_on_found and findings:
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="staleif")
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="Busca guardas de sys.version_info ya muertas")
    p_scan.add_argument("path", nargs="?", default=".")
    p_scan.add_argument("--json", action="store_true")
    p_scan.add_argument("--fail-on-found", action="store_true")
    p_scan.set_defaults(func=_cmd_scan)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
