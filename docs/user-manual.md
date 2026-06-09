# User Manual

This manual explains how to run SEO Ops Command Center safely in a public, configurable setup.

## Operating Model

SEO Ops Command Center is not an autonomous production editor. It is a command-line operations assistant that reads configuration, produces sanitized reports, and writes a fix queue for human review.

Phase 1 supports report-only operation. That means it can write local artifacts, but it does not modify your site, commit code, deploy changes, create redirects, publish content, or mutate provider accounts.

## First-Time Setup

Create a virtual environment and install the project:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Create local config:

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml` for your sites. Keep this file local. It is ignored by git because real site metadata can be sensitive.

## Configuring Sites

Each site entry needs at least:

```yaml
sites:
  - name: example-static-site
    domain: example.com
```

Optional fields describe ownership, source code, deploy target, and providers:

```yaml
sites:
  - name: example-static-site
    domain: example.com
    group: business
    ownership: owned
    edit_policy: repo_backed_safe_fixes
    source:
      type: git_worktree
      path: ./sites/example
      branch: main
    deploy:
      type: git_push
      remote: origin
      branch: main
      require_approval: true
    providers:
      gsc:
        property: sc-domain:example.com
      pagespeed:
        enabled: true
```

Do not put credentials in `config.yaml`. Use environment variables or a local secret manager.

## Approval Gates

Approval gates are explicit by design:

```yaml
approvals:
  required_for:
    - file_edits
    - git_commits
    - deploys
    - redirects
    - content_generation
    - publishing
    - cross_site_links
    - paid_api_calls
    - ads_changes
```

If you enable a risky automation setting without the matching approval gate, `seo-ops doctor` fails.

## Running Checks

Validate config:

```bash
seo-ops doctor --config config.yaml
```

Run report-only:

```bash
seo-ops run --config config.yaml --mode report-only
```

By default, artifacts are written to:

```text
.seo-ops/reports/report.json
.seo-ops/reports/fix_queue.json
```

You can choose a different output directory:

```bash
seo-ops run --config config.yaml --mode report-only --output-dir /tmp/seo-ops-report
```

## Importing GSC Exports

You can use Google Search Console data without OAuth by exporting reports as CSV and dropping them into the local import folder:

```text
.seo-ops/imports/gsc/<domain>/
```

Example:

```text
.seo-ops/imports/gsc/example.com/performance-pages.csv
```

Enable the import parser for the matching site:

```yaml
workspace:
  import_dir: .seo-ops/imports

sites:
  - name: example-static-site
    domain: example.com
    providers:
      gsc_exports:
        enabled: true
```

Phase 1 recognizes Performance > Pages-style CSV exports and queues findings for pages with high impressions and low CTR. Unknown CSV shapes create low-severity findings so you can see which exports are not supported yet.

## Inspecting the Queue

```bash
seo-ops queue list --path .seo-ops/reports/fix_queue.json
```

Findings are sorted by severity. Phase 1 queue entries come from local doctor checks. Future providers will add real GSC, PageSpeed, vendor alert, indexing, and repo-scan findings.

## Sanitization

Before writing queue and report data, SEO Ops redacts common secret keys and inline secret patterns such as:

- API keys
- tokens
- client secrets
- refresh tokens
- passwords
- credentials
- private keys

Redaction is a safety layer, not permission to store secrets in config. Keep secrets out of config and fixtures.

## What Phase 1 Does Not Do

Phase 1 does not:

- Connect to Google Search Console.
- Read Gmail.
- Call PageSpeed APIs.
- Modify site files.
- Create redirects.
- Commit or push git changes.
- Deploy sites.
- Generate or publish AI content.
- Call paid APIs.

Those features should be added as provider or adapter modules behind explicit config and approval gates.
