"""Load and validate public-safe SEO Ops configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from seo_ops.config.schema import (
    SAFE_MODES,
    ApprovalConfig,
    AutomationConfig,
    SeoOpsConfig,
    SiteConfig,
    WorkspaceConfig,
)


class ConfigError(ValueError):
    """Raised when configuration is missing, invalid, or unsafe."""


def load_config(path: str | Path = "config.yaml") -> SeoOpsConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    data = _load_yaml(config_path)
    if not isinstance(data, dict):
        raise ConfigError("Config root must be a mapping")

    config = _build_config(data)
    _validate_config(config)
    return config


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise ConfigError("PyYAML is required to read YAML config. Install the project dependencies.") from exc

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigError("Config root must be a mapping")
    return data


def _build_config(data: dict[str, Any]) -> SeoOpsConfig:
    workspace_data = _mapping(data.get("workspace"), "workspace")
    approvals_data = _mapping(data.get("approvals"), "approvals")
    automation_data = _mapping(data.get("automation"), "automation")

    raw_mode = data.get("mode", "report_only")
    if not isinstance(raw_mode, str):
        raise ConfigError("mode must be a string")
    mode = _normalize_mode(raw_mode)

    raw_sites = data.get("sites", [])
    if not isinstance(raw_sites, list):
        raise ConfigError("sites must be a list")

    sites = []
    for index, site_data in enumerate(raw_sites):
        if not isinstance(site_data, dict):
            raise ConfigError(f"sites[{index}] must be a mapping")
        sites.append(_build_site(site_data, index))

    groups = data.get("groups", {})
    if groups is None:
        groups = {}
    if not isinstance(groups, dict):
        raise ConfigError("groups must be a mapping")

    return SeoOpsConfig(
        workspace=WorkspaceConfig(
            data_dir=Path(str(workspace_data.get("data_dir", ".seo-ops/data"))),
            report_dir=Path(str(workspace_data.get("report_dir", ".seo-ops/reports"))),
            import_dir=Path(str(workspace_data.get("import_dir", ".seo-ops/imports"))),
        ),
        mode=mode,
        approvals=ApprovalConfig(required_for=tuple(_strings(approvals_data.get("required_for", [])))),
        automation=_build_automation(automation_data),
        sites=tuple(sites),
        groups=groups,
    )


def _build_site(site_data: dict[str, Any], index: int) -> SiteConfig:
    name = site_data.get("name")
    domain = site_data.get("domain")
    if not isinstance(name, str) or not name.strip():
        raise ConfigError(f"sites[{index}].name is required")
    if not isinstance(domain, str) or not domain.strip():
        raise ConfigError(f"sites[{index}].domain is required")

    return SiteConfig(
        name=name.strip(),
        domain=domain.strip(),
        group=_optional_string(site_data.get("group")),
        ownership=_optional_string(site_data.get("ownership")),
        edit_policy=_optional_string(site_data.get("edit_policy")),
        source=_mapping(site_data.get("source"), f"sites[{index}].source"),
        deploy=_mapping(site_data.get("deploy"), f"sites[{index}].deploy"),
        providers=_mapping(site_data.get("providers"), f"sites[{index}].providers"),
    )


def _build_automation(data: dict[str, Any]) -> AutomationConfig:
    safe_fixes = _mapping(data.get("safe_fixes"), "automation.safe_fixes")
    content_generation = _mapping(data.get("content_generation"), "automation.content_generation")
    publishing = _mapping(data.get("publishing"), "automation.publishing")

    return AutomationConfig(
        safe_fixes_enabled=bool(safe_fixes.get("enabled", False)),
        content_generation_enabled=bool(content_generation.get("enabled", False)),
        content_generation_mode=str(content_generation.get("mode", "draft_only")),
        publishing_enabled=bool(publishing.get("enabled", False)),
    )


def _validate_config(config: SeoOpsConfig) -> None:
    if config.mode not in SAFE_MODES:
        raise ConfigError(f"Unsupported mode: {config.mode}")
    if not config.sites:
        raise ConfigError("At least one site is required")

    if config.automation.publishing_enabled and not config.approvals.requires("publishing"):
        raise ConfigError("publishing automation requires publishing approval")
    if config.automation.content_generation_enabled and not config.approvals.requires("content_generation"):
        raise ConfigError("content generation requires content_generation approval")
    if config.automation.safe_fixes_enabled and not config.approvals.requires("file_edits"):
        raise ConfigError("safe fixes require file_edits approval")

    for site in config.sites:
        if site.deploy and not config.approvals.requires("deploys") and site.deploy.get("require_approval") is not True:
            raise ConfigError(f"site {site.name} deploy adapter requires deploy approval")


def _normalize_mode(value: str) -> str:
    return value.strip().replace("-", "_")


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return value


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError("approval requirements must be a list of strings")
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError("optional string field must be a string")
    return value
