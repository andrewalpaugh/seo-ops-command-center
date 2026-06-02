# SEO Ops Command Center

Operator-in-the-loop SEO operations toolkit for monitoring Search Console, vendor alerts, indexing health, and site issues, with structured fix queues and human-approved repairs.

## Status

Early extraction scaffold. This repository is intended to become a clean, public-safe version of a private SEO operations workflow. It should default to report-only behavior and require explicit approval before edits, deploys, publishing, redirects, paid API calls, or AI-generated content.

## Initial Goals

- Monitor Google Search Console, PageSpeed, indexing health, SERP visibility, and vendor alerts.
- Parse Ahrefs/Semrush/GSC/Bing alert emails into structured findings.
- Write a prioritized fix queue.
- Support human-approved repairs for safe repo-backed issues.
- Keep AI content generation and publishing disabled by default.
- Support common deploy adapters, including git-backed deploys and SFTP.

## Safety Defaults

- Report-only by default.
- No raw email body persistence by default.
- No secrets in reports or fixtures.
- No production changes without human approval.
- No AI publishing by default.

## Planned Commands

```bash
seo-ops init
seo-ops doctor
seo-ops run --mode report-only
seo-ops gmail discover-templates --days 30
seo-ops queue list
seo-ops fix propose <id>
seo-ops fix apply <id> --require-approval
seo-ops deploy --dry-run
```

## Roadmap

See [docs/seo-ops-public-roadmap.md](docs/seo-ops-public-roadmap.md).
