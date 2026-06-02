"""Command-line entry point for SEO Ops Command Center."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="seo-ops")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("doctor", help="Check local configuration")
    subparsers.add_parser("run", help="Run report-only checks")
    subparsers.add_parser("queue", help="Inspect the fix queue")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.version:
        from seo_ops import __version__

        print(__version__)
        return 0
    if not args.command:
        parser.print_help()
        return 0
    print(f"{args.command}: scaffold only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
