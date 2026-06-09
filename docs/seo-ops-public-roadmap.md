# SEO Ops Public Roadmap

## Working Thesis

SEO Ops Command Center should become a clean, reusable public SEO operations tool rather than a one-off personal automation system. The public version needs generic configuration, fake examples, redacted fixtures, and explicit approval boundaries before it can be useful to other operators.

The project should focus first on monitoring, issue ingestion, structured fix queues, and human-approved repairs. AI content generation, publishing, ads, and other high-risk automation should be optional advanced modules with explicit opt-in controls.

## Product Positioning

SEO Ops is an operator-in-the-loop toolkit for technical site owners. It monitors Search Console, PageSpeed, indexing health, SERP visibility, and SEO vendor alerts, then turns issues into a prioritized fix queue with optional safe repo-backed repairs.

The public-facing pitch should not lead with automated AI publishing. A stronger initial positioning is:

> A technical SEO operations cockpit that finds issues, explains impact, queues fixes, and helps site owners safely repair their sites with human approval.

## Public-Ready Scope

Public releases should avoid project-specific assumptions and private operational state:

- Real domains, customer names, and strategic buckets.
- Business-specific reputation, content, or platform rules.
- Local machine paths and repo paths.
- Daily run logs or generated operational history.
- Provider credentials, OAuth artifacts, cookies, or tokens.
- Raw email bodies or unredacted vendor alerts.
- SQLite databases, queues, reports, and runtime artifacts.
- Any private business strategy or source-system implementation detail.

The public project should stay generic and reusable: fake example domains, redacted fixtures, provider-neutral interfaces, and configuration that starts from zero.

## Target Users

Primary users:

- Technical founders running several small websites.
- SEO consultants who work with repo-backed static sites.
- Indie SaaS owners with Google Search Console access.
- Site owners using Cloudflare Pages, Render, GitHub, SFTP/cPanel, WordPress, Webflow, or Blogger.

Secondary users:

- Agencies that want internal issue queues instead of scattered email alerts.
- Developers who want a safer alternative to ad hoc SEO scripts.

Not the initial target:

- Casual users who expect one-click fully autonomous SEO.
- Large agencies needing multi-client billing, RBAC, and enterprise reporting.
- Users who want an unsupervised AI content mill.

## Core Principles

1. **Report-only by default.** The first run should not modify files, sites, repos, or provider settings.
2. **Human at the keyboard.** Risky operations should require an operator to review and approve.
3. **Explicit escalation.** Fixes, publishing, redirects, deploys, cross-site links, and AI content should require explicit config and command flags.
4. **Provider modularity.** GSC is the baseline. Supplemental providers enrich the picture but do not replace it.
5. **Structured findings first.** Everything should normalize into findings and actions before fixes are attempted.
6. **Secrets never enter reports.** All provider outputs must pass through redaction before storage or display.
7. **No raw email persistence by default.** Parse vendor emails into structured records; store redacted fixtures only for parser tests.
8. **Safe automation boundary.** Auto-fix only deterministic, repo-backed, low-risk issues.
9. **Configurable ownership.** The tool should understand sites, groups, edit policies, deploy adapters, and approval requirements.
10. **Draft-only AI by default.** AI-generated content should be opt-in, advanced, and draft-only unless the user deliberately enables publishing.

## Permission Model

The public tool should use escalating operating modes.

```yaml
mode: report_only

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

automation:
  safe_fixes:
    enabled: false
  content_generation:
    enabled: false
    mode: draft_only
  publishing:
    enabled: false
```

### Modes

**Report-only**

- Collects provider data.
- Writes findings.
- Produces reports.
- Does not edit files or call mutation APIs.

**Queue mode**

- Produces `fix_queue.json` and/or SQLite findings/actions.
- Assigns recommended actions.
- Does not edit files.

**Assisted mode**

- Presents one proposed fix at a time.
- Applies only after user approval.
- Shows diffs before commit/deploy.

**Batch mode**

- Applies approved low-risk fixes from the queue.
- Requires explicit config.
- Should still show a preflight summary.

**Advanced mode**

- Enables AI content drafting, publishing integrations, ads draft creation, and other sensitive modules.
- Requires explicit setup, config flags, and command flags.

## Suggested Repository Shape

```text
seo-ops/
  README.md
  config.example.yaml
  .env.example
  pyproject.toml
  src/
    seo_ops/
      cli.py
      config/
        loader.py
        schema.py
      core/
        assets.py
        findings.py
        fix_queue.py
        redaction.py
        reporting.py
      providers/
        gsc.py
        pagespeed.py
        gmail_seo.py
        indexnow.py
        serper.py
        cloudflare.py
        repo_scan.py
      parsers/
        ahrefs_email.py
        semrush_email.py
      deploy/
        git_push.py
        sftp.py
        cloudflare_pages.py
        render.py
        wordpress.py
        webflow.py
        blogger.py
      fixes/
        robots.py
        sitemaps.py
        internal_links.py
        redirects.py
      content/
        drafts.py
        guardrails.py
  docs/
    quickstart.md
    configuration.md
    safety-model.md
    setup-google-search-console.md
    setup-gmail-alerts.md
    setup-indexnow.md
    deploy-adapters.md
    ai-content.md
  examples/
    simple-static-site.yaml
    multi-site-portfolio.yaml
    sftp-cpanel-site.yaml
  tests/
    fixtures/
      email/
        ahrefs/
        semrush/
```

## Configuration Model

The public version should be driven by one or more config files.

```yaml
workspace:
  data_dir: .seo-ops/data
  report_dir: .seo-ops/reports

sites:
  - name: example-business-site
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
    providers:
      gsc:
        property: sc-domain:example.com
      pagespeed:
        enabled: true
      indexnow:
        enabled: true

groups:
  business:
    allowed_topics:
      - product
      - documentation
      - tutorials
    disallowed_topics:
      - personal reputation

fixes:
  auto_fix:
    enabled: false
  require_approval: true
```

## Deploy Adapters

Deploy support should be adapter-based. Public adoption will require more than git-backed static sites.

### Adapter List

- `none`: report-only, no deploy.
- `git_push`: commit/push into a repo-backed deploy pipeline.
- `cloudflare_pages`: inspect/deploy via Cloudflare.
- `render`: inspect deploy status for Render-hosted apps.
- `sftp`: upload static files to cPanel/shared hosting/VPS.
- `wordpress`: future adapter for common public use.
- `webflow`: gated adapter; report-only by default.
- `blogger`: gated adapter; report-only by default.

### SFTP Requirements

SFTP should be included in the public roadmap because many small site owners still publish through cPanel, shared hosting, or static SFTP upload.

Example:

```yaml
sites:
  - name: static-cpanel-site
    domain: example.net
    source:
      type: local_static
      path: ./dist/example-net
    deploy:
      type: sftp
      host_env: EXAMPLE_SFTP_HOST
      port: 22
      username_env: EXAMPLE_SFTP_USER
      password_env: EXAMPLE_SFTP_PASSWORD
      remote_path: /public_html
      strategy: sync
      dry_run_first: true
      delete_remote_extra_files: false
      require_approval: true
```

SFTP safety controls:

- Dry-run manifest before upload.
- Remote path allowlist.
- No remote deletes by default.
- Optional deletes require explicit approval.
- Exclude patterns.
- Upload temp file then rename when possible.
- Verify size/checksum after upload when possible.
- Save upload manifest for rollback guidance.

## Provider Roadmap

### V1 Providers

**Google Search Console**

- Search analytics.
- Sitemap status.
- URL inspection where available.
- Page/indexing issue ingestion from exports.

**PageSpeed Insights**

- Mobile performance score.
- SEO score.
- Core Web Vitals fields where available.

**Gmail SEO Vendor Sweep**

- Ahrefs/Semrush alert parsing.
- Body parsing, not subject-only.
- One-time template discovery pass.
- Structured fix queue.

**Repo Scan**

- Robots.txt.
- Sitemaps.
- Canonicals.
- Metadata.
- Internal links.
- Redirect files/config.

**IndexNow**

- URL submission.
- Per-domain key support.

### V1.1 Providers

- Cloudflare Pages/DNS/cache.
- Render deploy status.
- SERP provider such as Serper or DataForSEO.
- WordPress read/report adapter.

### Later Providers

- Ahrefs API.
- Semrush API.
- Webflow write adapter.
- Blogger write adapter.
- Google Ads draft creation.

## Gmail Vendor Email Parser

The private source system revealed that subject-only parsing is not enough. The public version should make email parsing a first-class provider.

### One-Time Template Discovery

Users should run a one-time baseline scan:

```bash
seo-ops gmail discover-templates --days 30
```

Purpose:

- Group Ahrefs/Semrush emails by provider and template pattern.
- Build redacted fixtures.
- Identify fields available in bodies.
- Speed up daily parsing by using known templates.

The daily run should not repeat this expensive pass.

### Daily Fast Path

```bash
seo-ops run --providers gmail_seo --days 2
```

Daily behavior:

- Fetch full message body.
- Prefer `text/plain`.
- Fallback to cleaned `text/html`.
- Parse only relevant vendor messages.
- Redact before writing.
- Normalize into findings/fix queue.

### Extracted Fields

- Provider.
- Source email ID/date/sender/subject.
- Site/property.
- Issue type.
- New/existing flag.
- Count.
- Affected URLs.
- Health score.
- Keyword ranking movement.
- Crawl error counts.
- Severity.
- Critical flag.
- Recommended action.

## Findings And Fix Queue

All provider output should normalize into a shared finding model.

```yaml
id: ahrefs:example.com:orphan-page:path-hash
provider: ahrefs
site: example.com
group: business
category: internal_links
severity: warning
title: Orphan page has no incoming internal links
count: 23
affected_urls:
  - https://example.com/blog/example
recommended_action: Add relevant internal links from index and related posts.
approval_required: true
auto_fixable: false
target_repo: ./sites/example
state: open
first_seen: 2026-06-02T11:00:00Z
last_seen: 2026-06-02T11:00:00Z
source:
  provider_email_id: "37267"
  subject: "(Example) Orphan page (has no incoming internal links) [New]: 23 URLs"
```

Queue behavior:

- Dedupe across runs.
- Update `last_seen`, count, and affected URLs.
- Allow states: `open`, `proposed`, `resolved`, `ignored`.
- Keep raw provider data separate and redacted.

## Fix Automation Boundary

### Safe To Propose

- Internal links to orphan repo-backed pages.
- Robots sitemap line corrections.
- Missing `llms.txt` for static repo-backed sites.
- Broken sitemap references where target is obvious.
- Metadata length suggestions.
- Redirect cleanup where target is unambiguous.

### Usually Requires Approval

- Redirect changes.
- Publishing or deleting content.
- Cross-site links.
- Webflow edits.
- Blogger edits.
- WordPress writes.
- Any legal/privacy/terms edits.
- AI-generated content.
- Ad/campaign creation.

### Should Not Auto-Fix

- Brand positioning rewrites.
- Legal pages.
- Large redirect migrations.
- Paid ads activation.
- Live campaign changes.
- Unverified properties.
- Ambiguous canonical changes.

## AI Content Module

AI content should not be part of the core v1 default workflow.

Recommended default:

```yaml
content_generation:
  enabled: false
  mode: draft_only
  require_human_approval: true
```

Risks:

- Brand violations.
- Thin SEO spam.
- Legal/compliance claims.
- Reputation damage.
- Index pollution.
- Wrong-site publishing.
- Copyright or derivative-content risk.
- Prompt injection from vendor reports or webpages.

When enabled, it should:

- Produce drafts only.
- Enforce site/group topic boundaries.
- Require human approval before publishing.
- Include source/citation constraints.
- Log every generated draft.
- Refuse publishing by default.

## CLI Shape

Suggested commands:

```bash
seo-ops init
seo-ops doctor
seo-ops run --mode report-only
seo-ops gmail discover-templates --days 30
seo-ops queue list
seo-ops queue show <id>
seo-ops fix propose <id>
seo-ops fix apply <id> --require-approval
seo-ops deploy --dry-run
seo-ops report open
```

Risky commands should require explicit flags:

```bash
seo-ops publish --i-understand-this-changes-production
seo-ops content draft --site example --keyword "walmart edi"
seo-ops ads draft --paused-only
```

## Documentation Requirements

Public docs should include:

- README with clear value proposition.
- Quickstart.
- Configuration reference.
- Provider setup guides.
- Gmail alert parsing guide.
- SFTP deploy guide.
- Safety model.
- Approval model.
- Redaction policy.
- Examples with fake domains.
- Troubleshooting.

## Extraction Plan

### Phase 0: Private Audit

- Identify reusable files.
- Identify source-project-specific assumptions.
- Identify secrets/data/log paths that must never move.
- List modules to rewrite versus copy.

### Phase 1: Clean Skeleton

- New repo.
- CLI scaffold.
- Config loader.
- Redaction layer.
- Findings/fix queue model.
- Report-only mode.

### Phase 2: Baseline Providers

- GSC.
- PageSpeed.
- Repo scan.
- Gmail SEO parser.
- IndexNow.

### Phase 3: Fix Queue

- Normalize findings.
- Dedupe queue.
- Daily report.
- Human-approved fix workflow.

### Phase 4: Deploy Adapters

- Git push.
- SFTP.
- Cloudflare Pages.
- Render status.

### Phase 5: Optional Advanced Modules

- Webflow/Blogger/WordPress gated writes.
- AI draft generation.
- Google Ads paused draft creation.

## V1 Definition

V1 should be considered ready when:

- A new user can configure one repo-backed site.
- The tool runs report-only without mutations.
- GSC/PageSpeed/repo scan/Gmail parser produce structured findings.
- Findings are written to a queue.
- The daily report is readable and actionable.
- At least one safe fix can be proposed and applied with approval.
- SFTP deploy dry-run works for static files.
- No raw secrets or email bodies are written by default.
- Tests cover parsing, redaction, queue dedupe, and approval gates.

## Non-Goals For V1

- Fully autonomous publishing.
- Fully autonomous SEO fixing.
- Multi-tenant SaaS dashboard.
- Billing.
- Agency client management.
- Live ad campaign activation.
- AI content publishing without review.
- Enterprise-grade RBAC.

## Open Questions

1. Should the public repo be Python-only at first, or allow a Node/TypeScript CLI?
2. Should SQLite be required, or should `fix_queue.json` be the first storage layer?
3. Should WordPress be v1 or v1.1?
4. Should SFTP deploy support be v1 or v1.1?
5. Should the first release include GSC OAuth setup, or expect users to provide credentials?
6. Should AI content be completely excluded from the first public release?
7. Should the public name be `seo-ops`, `siteops-seo`, or something more brandable?

## Recommended First Move

Start with a focused Phase 1 foundation:

- Implement config loading, redaction, findings, and queue.
- Add a first useful provider behind report-only boundaries.
- Prefer the Gmail SEO parser path because vendor alerts are immediately useful and easy to demonstrate with fake fixtures.
- Add fake fixtures from redacted Ahrefs/Semrush templates.
- Keep everything report-only until the queue model is solid.

This creates a credible public foundation without exposing the risky content-generation and production-mutation parts too early.
