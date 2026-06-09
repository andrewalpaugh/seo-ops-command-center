"""Configuration objects for SEO Ops Command Center."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SAFE_MODES = {"report_only", "queue", "assisted", "batch", "advanced"}


@dataclass(frozen=True)
class WorkspaceConfig:
    data_dir: Path = Path(".seo-ops/data")
    report_dir: Path = Path(".seo-ops/reports")
    import_dir: Path = Path(".seo-ops/imports")


@dataclass(frozen=True)
class ApprovalConfig:
    required_for: tuple[str, ...] = (
        "file_edits",
        "git_commits",
        "deploys",
        "redirects",
        "content_generation",
        "publishing",
        "cross_site_links",
        "paid_api_calls",
        "ads_changes",
    )

    def requires(self, operation: str) -> bool:
        return operation in self.required_for


@dataclass(frozen=True)
class AutomationConfig:
    safe_fixes_enabled: bool = False
    content_generation_enabled: bool = False
    content_generation_mode: str = "draft_only"
    publishing_enabled: bool = False


@dataclass(frozen=True)
class SiteConfig:
    name: str
    domain: str
    group: str | None = None
    ownership: str | None = None
    edit_policy: str | None = None
    source: dict[str, Any] = field(default_factory=dict)
    deploy: dict[str, Any] = field(default_factory=dict)
    providers: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SeoOpsConfig:
    workspace: WorkspaceConfig
    mode: str
    approvals: ApprovalConfig
    automation: AutomationConfig
    sites: tuple[SiteConfig, ...]
    groups: dict[str, Any] = field(default_factory=dict)
