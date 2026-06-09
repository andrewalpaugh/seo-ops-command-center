# SEO Ops Command Center

SEO Ops Command Center is a public-safe, operator-in-the-loop toolkit for technical SEO operations. It validates site configuration, keeps risky automation disabled by default, writes sanitized reports, and produces a structured fix queue that future providers and repair workflows can build on.

This repository is designed for public consumption. Examples use fake domains, reports are redacted before writing, local config is ignored by git, and production-changing actions must be explicitly configured and approved.

## Current Status

Phase 1 foundation is implemented:

- YAML config loading and safety validation.
- Secret redaction for reports and fix queues.
- Finding and fix queue data models.
- `seo-ops doctor` for configuration checks.
- `seo-ops run --mode report-only` for local report and queue artifacts.
- `seo-ops queue list` for inspecting generated queue files.
- Unit tests using Python's built-in `unittest`.

Live provider integrations such as Google Search Console, Gmail vendor alerts, PageSpeed, IndexNow, and deploy adapters are planned but not implemented yet.

## Safety Defaults

- Report-only by default.
- No file edits without approval.
- No commits without approval.
- No deploys without approval.
- No redirects without approval.
- No paid API calls without approval.
- No AI content generation or publishing by default.
- No raw email body persistence by default.
- No secrets in reports, queues, fixtures, or docs.

## Install

Requirements:

- Python 3.11 or newer.

Recommended local setup:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Confirm the CLI works:

```bash
seo-ops --version
```

## Quick Start

Copy the example config and keep your local copy untracked:

```bash
cp config.example.yaml config.yaml
```

Validate configuration:

```bash
seo-ops doctor --config config.yaml
```

Run a report-only pass:

```bash
seo-ops run --config config.yaml --mode report-only
```

Inspect the generated fix queue:

```bash
seo-ops queue list --path .seo-ops/reports/fix_queue.json
```

Generated files are written under `.seo-ops/` by default and are ignored by git.

## Configuration

The tool is configured entirely through YAML. Start with `config.example.yaml` and replace the fake site values with your own.

Important top-level sections:

- `workspace`: local data and report directories.
- `mode`: current operating mode. Phase 1 supports `report_only`.
- `approvals`: operations that require human approval.
- `automation`: explicit toggles for safe fixes, content generation, and publishing.
- `groups`: optional site grouping metadata.
- `sites`: site definitions, provider settings, source metadata, and deploy metadata.

The example config intentionally uses `example.com` and contains no real credentials. Put secrets in environment variables or local secret stores, never in tracked config or fixtures.

## Commands

```bash
seo-ops doctor --config config.yaml
```

Loads config, validates safety gates, and prints a concise summary.

```bash
seo-ops run --config config.yaml --mode report-only
```

Writes a sanitized `report.json` and `fix_queue.json`. This command does not edit files, deploy sites, call provider mutation APIs, publish content, or make paid API calls.

```bash
seo-ops queue list --path .seo-ops/reports/fix_queue.json
```

Prints queue findings by severity.

## Public Data Rules

Do not commit:

- `.env`
- `config.yaml`
- `.seo-ops/`
- API keys, tokens, OAuth client secrets, refresh tokens, passwords, cookies, or private keys
- Raw email bodies
- Real customer domains in fixtures
- Private strategy notes or local machine paths

Use fake domains such as `example.com`, `example.net`, and `example.org` in docs and tests.

## Development

Run tests:

```bash
.venv/bin/python -m unittest discover -v
```

Run the CLI without activating the venv:

```bash
.venv/bin/seo-ops doctor --config config.example.yaml
```

## Roadmap

See `docs/seo-ops-public-roadmap.md` for the broader product direction.

Next planned milestones:

- Google Search Console provider.
- PageSpeed provider.
- Gmail SEO vendor alert parser for Ahrefs/Semrush-style emails.
- Repo scanner provider.
- Deterministic safe-fix proposal flow.
- Approval-gated deploy adapters.

AI content generation and publishing remain advanced, opt-in, and draft-first.
