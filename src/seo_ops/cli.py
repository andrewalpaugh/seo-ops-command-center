"""Command-line entry point for SEO Ops Command Center."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from seo_ops.config import ConfigError, load_config
from seo_ops.core.reporting import build_doctor_findings, write_report_only_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="seo-ops")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="Check local configuration")
    doctor.add_argument("--config", default="config.yaml", help="Path to config file")

    run = subparsers.add_parser("run", help="Run report-only checks")
    run.add_argument("--config", default="config.yaml", help="Path to config file")
    run.add_argument("--mode", default=None, choices=["report-only", "report_only"], help="Run mode")
    run.add_argument("--output-dir", default=None, help="Directory for report artifacts")

    queue = subparsers.add_parser("queue", help="Inspect the fix queue")
    queue.add_argument("action", nargs="?", default="list", choices=["list"], help="Queue action")
    queue.add_argument("--path", default=".seo-ops/reports/fix_queue.json", help="Path to fix_queue.json")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        from seo_ops import __version__

        print(__version__)
        return 0
    if not args.command:
        parser.print_help()
        return 0
    try:
        if args.command == "doctor":
            return _doctor(args.config)
        if args.command == "run":
            return _run(args.config, args.mode, args.output_dir)
        if args.command == "queue":
            return _queue_list(args.path)
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 2

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _doctor(config_path: str) -> int:
    config = load_config(config_path)
    findings = build_doctor_findings(config)
    print(f"Configuration OK: {config_path}")
    print(f"mode: {config.mode}")
    print(f"sites: {len(config.sites)}")
    print(f"doctor findings: {len(findings)}")
    return 0


def _run(config_path: str, mode: str | None, output_dir: str | None) -> int:
    config = load_config(config_path)
    requested_mode = (mode or config.mode).replace("-", "_")
    if requested_mode != "report_only":
        print("Only report-only runs are implemented in Phase 1.")
        return 2

    report_dir = Path(output_dir) if output_dir else config.workspace.report_dir
    report_path, queue_path = write_report_only_run(config, report_dir)
    print(f"Report written: {report_path}")
    print(f"Fix queue written: {queue_path}")
    return 0


def _queue_list(path: str) -> int:
    queue_path = Path(path)
    if not queue_path.exists():
        print(f"Fix queue not found: {queue_path}")
        return 1
    payload = json.loads(queue_path.read_text(encoding="utf-8"))
    findings = payload.get("findings", [])
    print(f"findings: {len(findings)}")
    for finding in findings:
        print(f"- [{finding.get('severity')}] {finding.get('site')}: {finding.get('title')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
