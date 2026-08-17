#!/usr/bin/env python3
"""Deterministic state and deduplication for the official-data-daily skill."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


STATE_VERSION = 1
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REGISTRY = SCRIPT_DIR.parent / "assets" / "source-registry.json"


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    return dt.datetime.now().astimezone().date().isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        if default is not None:
            return copy.deepcopy(default)
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def initial_state() -> dict[str, Any]:
    return {"version": STATE_VERSION, "updated_at": None, "datasets": {}, "releases": {}}


def runtime_paths(root: Path) -> dict[str, Path]:
    return {
        "sources": root / "sources.json",
        "schedule": root / "schedule.json",
        "state": root / "state" / "state.json",
        "runs": root / "state" / "runs.jsonl",
        "releases": root / "releases",
        "daily": root / "daily",
    }


def validate_sources_data(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("datasets"), list):
        return ["sources.json must be an object with a datasets array"]
    seen: set[str] = set()
    allowed_modes = {"daily", "window", "calendar", "weekly", "interval"}
    allowed_record_types = {"series", "event"}
    for index, item in enumerate(data["datasets"]):
        prefix = f"datasets[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("dataset_id", "name", "institution", "release_url", "official_domain", "check_policy"):
            if not item.get(field):
                errors.append(f"{prefix}.{field} is required")
        dataset_id = item.get("dataset_id")
        if dataset_id:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", dataset_id):
                errors.append(f"{prefix}.dataset_id must be lowercase hyphen-case")
            if dataset_id in seen:
                errors.append(f"duplicate dataset_id: {dataset_id}")
            seen.add(dataset_id)
        policy = item.get("check_policy", {})
        if not isinstance(policy, dict) or policy.get("mode") not in allowed_modes:
            errors.append(f"{prefix}.check_policy.mode must be one of {sorted(allowed_modes)}")
        if isinstance(policy, dict) and policy.get("mode") == "window":
            windows = policy.get("day_windows")
            if not isinstance(windows, list) or not windows:
                errors.append(f"{prefix}.check_policy.day_windows must be non-empty")
        if isinstance(policy, dict) and policy.get("mode") == "weekly":
            weekdays = policy.get("weekdays")
            if (
                not isinstance(weekdays, list)
                or not weekdays
                or any(not isinstance(day, int) or day < 0 or day > 6 for day in weekdays)
            ):
                errors.append(f"{prefix}.check_policy.weekdays must contain integers from 0 to 6")
        if isinstance(policy, dict) and policy.get("mode") == "interval":
            interval_days = policy.get("interval_days")
            if not isinstance(interval_days, int) or isinstance(interval_days, bool) or interval_days < 1:
                errors.append(f"{prefix}.check_policy.interval_days must be a positive integer")
        if isinstance(policy, dict) and "months" in policy:
            months = policy.get("months")
            if (
                not isinstance(months, list)
                or not months
                or any(not isinstance(month, int) or month < 1 or month > 12 for month in months)
            ):
                errors.append(f"{prefix}.check_policy.months must contain integers from 1 to 12")
        record_type = item.get("record_type", "series")
        if record_type not in allowed_record_types:
            errors.append(f"{prefix}.record_type must be one of {sorted(allowed_record_types)}")
        for plural_field, singular_field in (
            ("release_urls", "release_url"),
            ("official_domains", "official_domain"),
        ):
            values = item.get(plural_field)
            if values is not None and (
                not isinstance(values, list)
                or not values
                or any(not isinstance(value, str) or not value.strip() for value in values)
            ):
                errors.append(f"{prefix}.{plural_field} must be a non-empty string array")
            if isinstance(values, list) and item.get(singular_field) not in values:
                errors.append(f"{prefix}.{plural_field} must include {singular_field}")
    return errors


def load_sources(root: Path) -> dict[str, Any]:
    data = read_json(runtime_paths(root)["sources"])
    errors = validate_sources_data(data)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    p = runtime_paths(root)
    p["releases"].mkdir(parents=True, exist_ok=True)
    p["daily"].mkdir(parents=True, exist_ok=True)
    p["state"].parent.mkdir(parents=True, exist_ok=True)
    if not p["sources"].exists():
        shutil.copyfile(DEFAULT_REGISTRY, p["sources"])
    if not p["state"].exists():
        atomic_write_json(p["state"], initial_state())
    if not p["schedule"].exists():
        atomic_write_json(p["schedule"], {"refreshed_at": None, "covered_datasets": [], "events": []})
    if not p["runs"].exists():
        atomic_write_text(p["runs"], "")
    sources = load_sources(root)
    return {
        "status": "initialized",
        "root": str(root),
        "dataset_count": len(sources["datasets"]),
        "sources": str(p["sources"]),
        "state": str(p["state"]),
    }


def parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value[:10])


def within_windows(day: int, windows: list[list[int]]) -> bool:
    return any(int(start) <= day <= int(end) for start, end in windows)


def optional_date(value: Any) -> dt.date | None:
    if not value:
        return None
    try:
        return parse_date(str(value))
    except (TypeError, ValueError):
        return None


def optional_datetime(value: Any, fallback_tz: dt.tzinfo | None = None) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None and fallback_tz is not None:
        parsed = parsed.replace(tzinfo=fallback_tz)
    return parsed


def active_in_month(policy: dict[str, Any], candidate: dt.date) -> bool:
    months = policy.get("months")
    return not months or candidate.month in months


def policy_is_due(policy: dict[str, Any], last_checked_at: Any, target: dt.date) -> bool:
    """Return true when a scheduled check is still uncovered as of target."""
    mode = policy["mode"]
    last_checked = optional_date(last_checked_at)
    if last_checked is None:
        return True
    if last_checked >= target:
        return False
    first = last_checked + dt.timedelta(days=1)
    candidates = (first + dt.timedelta(days=offset) for offset in range((target - first).days + 1))

    for candidate in candidates:
        if not active_in_month(policy, candidate):
            continue
        if mode == "daily":
            return True
        if mode == "window" and within_windows(candidate.day, policy["day_windows"]):
            return True
        if mode == "weekly" and candidate.weekday() in policy.get("weekdays", []):
            return True
        if (
            mode == "interval"
            and (candidate - last_checked).days >= policy["interval_days"]
        ):
            return True
    return False


def event_is_due(
    event: dict[str, Any],
    last_checked_at: Any,
    target: dt.date,
    scan_end_at: dt.datetime,
) -> bool:
    try:
        start = parse_date(event["window_start"])
        end = parse_date(event["window_end"])
    except (KeyError, TypeError, ValueError):
        return False
    expected_at = optional_datetime(event.get("expected_at"), scan_end_at.tzinfo)
    last_checked_time = optional_datetime(last_checked_at, scan_end_at.tzinfo)
    if expected_at and scan_end_at < expected_at:
        return False
    if expected_at and last_checked_time and last_checked_time < expected_at <= scan_end_at:
        return True
    last_checked = optional_date(last_checked_at)
    if last_checked is None:
        return start <= target <= end
    if last_checked >= target:
        return False
    return start <= target and end >= last_checked + dt.timedelta(days=1)


def scan_end_for_target(target: dt.date) -> dt.datetime:
    current = dt.datetime.now().astimezone()
    if target == current.date():
        return current
    return dt.datetime.combine(target, dt.time(23, 59, 59), tzinfo=current.tzinfo)


def schedule_is_stale(schedule: dict[str, Any], target: dt.date) -> bool:
    refreshed = schedule.get("refreshed_at")
    if not refreshed:
        return True
    try:
        refreshed_date = parse_date(refreshed)
    except (TypeError, ValueError):
        return True
    return (refreshed_date.year, refreshed_date.month) != (target.year, target.month) or (target - refreshed_date).days >= 7


def latest_for_dataset(state: dict[str, Any], dataset_id: str) -> dict[str, Any] | None:
    return state.get("datasets", {}).get(dataset_id, {}).get("latest")


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    sources = load_sources(root)
    p = runtime_paths(root)
    state = read_json(p["state"], initial_state())
    schedule = read_json(p["schedule"], {"refreshed_at": None, "covered_datasets": [], "events": []})
    target = parse_date(args.date or today_iso())
    scan_end_at = scan_end_for_target(target)
    scan_end = scan_end_at.isoformat(timespec="seconds")
    stale = schedule_is_stale(schedule, target)
    covered_datasets = set(schedule.get("covered_datasets", []))
    events_by_dataset: dict[str, list[dict[str, Any]]] = {}
    for event in schedule.get("events", []):
        events_by_dataset.setdefault(event.get("dataset_id", ""), []).append(event)

    due: list[dict[str, Any]] = []
    calendar_urls: set[str] = set()
    calendar_sources: list[dict[str, Any]] = []
    for dataset in sources["datasets"]:
        if not dataset.get("enabled", True):
            continue
        dataset_id = dataset["dataset_id"]
        ds_state = state.get("datasets", {}).get(dataset_id, {})
        last_checked_at = ds_state.get("last_checked_at")
        baseline_required = optional_date(last_checked_at) is None
        if baseline_required:
            last_checked_at = None
        policy = dataset["check_policy"]
        mode = policy["mode"]
        scan_window = {"start_exclusive": last_checked_at, "end_inclusive": scan_end}
        matched_events: list[dict[str, Any]] = []
        if mode == "calendar":
            matched_events = [
                event for event in events_by_dataset.get(dataset_id, [])
                if event_is_due(event, last_checked_at, target, scan_end_at)
            ]
            is_due = baseline_required or bool(matched_events)
            if (stale or dataset_id not in covered_datasets) and dataset.get("calendar_url"):
                calendar_urls.add(dataset["calendar_url"])
                calendar_sources.append({
                    "dataset_id": dataset_id,
                    "calendar_url": dataset["calendar_url"],
                    "scan_window": scan_window,
                    "baseline_required": baseline_required,
                })
        else:
            is_due = policy_is_due(policy, last_checked_at, target)
        if is_due:
            latest = latest_for_dataset(state, dataset_id)
            due.append({
                "dataset_id": dataset_id,
                "name": dataset["name"],
                "jurisdiction": dataset.get("jurisdiction", dataset.get("region")),
                "record_type": dataset.get("record_type", "series"),
                "release_url": dataset["release_url"],
                "release_urls": dataset.get("release_urls", [dataset["release_url"]]),
                "official_domain": dataset["official_domain"],
                "official_domains": dataset.get("official_domains", [dataset["official_domain"]]),
                "retrieval": dataset.get("retrieval"),
                "filters": dataset.get("filters", []),
                "latest_known": latest,
                "previous_record": (latest or {}).get("record_path"),
                "schedule_events": matched_events,
                "scan_window": scan_window,
                "baseline_required": baseline_required,
            })
    return {
        "date": target.isoformat(),
        "coverage_end": scan_end,
        "calendar_refresh_required": bool(calendar_urls),
        "calendar_urls": sorted(calendar_urls),
        "calendar_sources": calendar_sources,
        "due_datasets": due,
        "due_count": len(due),
    }


def command_set_schedule(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    sources = load_sources(root)
    known = {item["dataset_id"] for item in sources["datasets"]}
    expected_coverage = {
        item["dataset_id"] for item in sources["datasets"]
        if item.get("enabled", True) and item.get("check_policy", {}).get("mode") == "calendar"
    }
    schedule = read_json(Path(args.input))
    if not isinstance(schedule, dict) or not isinstance(schedule.get("events"), list):
        raise ValueError("schedule must contain an events array")
    if not schedule.get("refreshed_at"):
        raise ValueError("schedule.refreshed_at is required")
    covered = set(schedule.get("covered_datasets", []))
    missing = sorted(expected_coverage - covered)
    if missing:
        raise ValueError("schedule.covered_datasets is incomplete: " + ", ".join(missing))
    for index, event in enumerate(schedule["events"]):
        required = ("dataset_id", "expected_at", "window_start", "window_end", "reference_period", "calendar_url")
        for field in required:
            if not event.get(field):
                raise ValueError(f"events[{index}].{field} is required")
        if event["dataset_id"] not in known:
            raise ValueError(f"unknown dataset_id in schedule: {event['dataset_id']}")
        if parse_date(event["window_end"]) < parse_date(event["window_start"]):
            raise ValueError(f"events[{index}] has window_end before window_start")
    atomic_write_json(runtime_paths(root)["schedule"], schedule)
    return {"status": "schedule-updated", "event_count": len(schedule["events"])}


def record_fingerprint(record: dict[str, Any]) -> str:
    payload = {
        "dataset_id": record["dataset_id"],
        "reference_period": record["reference_period"],
        "published_at": record["published_at"],
        "source_url": record["source_url"],
        "values": record["values"],
        "revisions": record.get("revisions", []),
        "methodology_changes": record.get("methodology_changes", []),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def safe_segment(value: str) -> str:
    safe = re.sub(r"[^0-9A-Za-z._-]+", "-", value).strip("-.")
    return safe or "unknown"


def validate_record(record: Any, known_ids: set[str]) -> None:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    required = ("dataset_id", "reference_period", "published_at", "retrieved_at", "source_title", "source_url", "values")
    for field in required:
        if not record.get(field):
            raise ValueError(f"record.{field} is required")
    if record["dataset_id"] not in known_ids:
        raise ValueError(f"unknown dataset_id: {record['dataset_id']}")
    if not isinstance(record["values"], list) or not record["values"]:
        raise ValueError("record.values must be a non-empty array")


def validate_analysis(record: dict[str, Any]) -> None:
    analysis = record.get("analysis")
    if not isinstance(analysis, dict):
        raise ValueError("record.analysis is required for new or revised releases")
    for field in ("headline", "behavioral_readout"):
        if not isinstance(analysis.get(field), str) or not analysis[field].strip():
            raise ValueError(f"record.analysis.{field} is required for new or revised releases")
    if analysis.get("confidence") not in {"high", "medium", "low"}:
        raise ValueError("record.analysis.confidence must be high, medium, or low")


def markdown_record(record: dict[str, Any], status: str, version: int, fingerprint: str) -> str:
    analysis = record.get("analysis", {})
    lines = [
        f"# {record['source_title']}", "",
        f"- 数据集：`{record['dataset_id']}`",
        f"- 数据所属期：`{record['reference_period']}`",
        f"- 官方发布时间：`{record['published_at']}`",
        f"- 采集时间：`{record['retrieved_at']}`",
        f"- 记录类型：`{status}`，版本 `v{version}`",
        f"- 内容指纹：`{fingerprint}`",
        f"- 官方原文：[{record['source_title']}]({record['source_url']})",
        "", "## 标准化数据", "",
        "| 指标 | 数值 | 单位 | 比较口径 | 季调 | 备注 |",
        "|---|---:|---|---|---|---|",
    ]
    for item in record["values"]:
        cells = [item.get("metric", ""), item.get("value", ""), item.get("unit", ""),
                 item.get("basis", ""), item.get("seasonal_adjustment", ""), item.get("note", "")]
        cells = [str(cell).replace("|", "\\|").replace("\n", " ") for cell in cells]
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(["", "## 分析", ""])
    if analysis.get("headline"):
        lines.extend([analysis["headline"], ""])
    if analysis.get("behavioral_readout"):
        lines.extend(["### 直观解读", "", analysis["behavioral_readout"], ""])
    if analysis.get("affected_groups"):
        lines.extend(["### 可能受影响的人群（推论）", ""])
        for item in analysis["affected_groups"]:
            lines.append(
                f"- **{item.get('group', '未命名人群')}**：{item.get('inference', '')}"
                f"（置信度：`{item.get('confidence', 'medium')}`）"
            )
        lines.append("")
    for title, key in (("变化", "changes"), ("有限推论", "implications"), ("限制与口径", "caveats")):
        items = analysis.get(key, [])
        if items:
            lines.extend([f"### {title}", ""] + [f"- {item}" for item in items] + [""])
    for title, key in (("其他可能解释", "alternative_explanations"), ("下一步官方验证", "verification_needed")):
        items = analysis.get(key, [])
        if items:
            lines.extend([f"### {title}", ""] + [f"- {item}" for item in items] + [""])
    if analysis.get("confidence"):
        lines.extend([f"置信度：`{analysis['confidence']}`", ""])
    if record.get("revisions"):
        lines.extend(["## 官方修订", ""] + [f"- {item}" for item in record["revisions"]] + [""])
    if record.get("methodology_changes"):
        lines.extend(["## 方法与口径变化", ""] + [f"- {item}" for item in record["methodology_changes"]] + [""])
    if record.get("official_citations"):
        lines.extend(["## 官方来源", ""])
        for citation in record["official_citations"]:
            lines.append(f"- [{citation.get('label', '官方来源')}]({citation.get('url', '')})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def relative_to_cwd(path: Path) -> str:
    return os.path.relpath(path.resolve(), Path.cwd().resolve()).replace("\\", "/")


def command_commit(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    sources = load_sources(root)
    known_ids = {item["dataset_id"] for item in sources["datasets"]}
    record = read_json(Path(args.input))
    validate_record(record, known_ids)
    state_path = runtime_paths(root)["state"]
    state = read_json(state_path, initial_state())
    fingerprint = record_fingerprint(record)
    release_key = f"{record['dataset_id']}::{record['reference_period']}"
    existing = state.get("releases", {}).get(release_key)
    if existing and existing.get("latest_fingerprint") == fingerprint:
        return {"dataset_id": record["dataset_id"], "reference_period": record["reference_period"],
                "status": "unchanged", "record_path": existing.get("latest_record_path"),
                "fingerprint": fingerprint}

    validate_analysis(record)
    version = int(existing.get("version_count", 0) if existing else 0) + 1
    status = "revision" if existing else "new"
    dataset_dir = runtime_paths(root)["releases"] / record["dataset_id"]
    stem = f"{safe_segment(record['reference_period'])}--v{version}"
    json_path, md_path = dataset_dir / f"{stem}.json", dataset_dir / f"{stem}.md"
    stored = copy.deepcopy(record)
    stored.update({"record_status": status, "record_version": version, "content_fingerprint": fingerprint})
    atomic_write_json(json_path, stored)
    atomic_write_text(md_path, markdown_record(stored, status, version, fingerprint))
    md_relative, json_relative = relative_to_cwd(md_path), relative_to_cwd(json_path)
    entry = {
        "dataset_id": record["dataset_id"], "reference_period": record["reference_period"],
        "version_count": version, "latest_fingerprint": fingerprint,
        "latest_record_path": md_relative, "latest_json_path": json_relative,
        "published_at": record["published_at"], "source_url": record["source_url"],
    }
    state.setdefault("releases", {})[release_key] = entry
    ds_state = state.setdefault("datasets", {}).setdefault(record["dataset_id"], {})
    prior_latest = ds_state.get("latest")
    ds_state["latest"] = {
        "release_key": release_key, "reference_period": record["reference_period"],
        "published_at": record["published_at"], "record_path": md_relative,
        "json_path": json_relative, "fingerprint": fingerprint,
    }
    ds_state["previous_latest"] = prior_latest
    state["updated_at"] = now_iso()
    atomic_write_json(state_path, state)
    return {
        "dataset_id": record["dataset_id"], "reference_period": record["reference_period"],
        "status": status, "version": version, "record_path": md_relative,
        "json_path": json_relative, "previous_record_path": (existing or {}).get("latest_record_path"),
        "fingerprint": fingerprint,
    }


def validate_synthesis(run: dict[str, Any]) -> None:
    changed_ids = {
        item.get("dataset_id")
        for item in run.get("results", [])
        if item.get("status") in {"new", "revision"}
    }
    changed_ids.discard(None)
    if not changed_ids:
        return

    synthesis = run.get("synthesis")
    if not isinstance(synthesis, dict):
        raise ValueError("run.synthesis is required when new or revised items exist")
    if not isinstance(synthesis.get("headline"), str) or not synthesis["headline"].strip():
        raise ValueError("run.synthesis.headline is required")
    if synthesis.get("confidence") not in {"high", "medium", "low"}:
        raise ValueError("run.synthesis.confidence must be high, medium, or low")

    sections = synthesis.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValueError("run.synthesis.sections must be a non-empty array")
    if len(sections) > 3:
        raise ValueError("run.synthesis.sections must contain at most 3 grouped judgments")

    allowed_significance = {"high", "medium", "low", "routine"}
    for index, section in enumerate(sections):
        prefix = f"run.synthesis.sections[{index}]"
        if not isinstance(section, dict):
            raise ValueError(f"{prefix} must be an object")
        for field in ("scope", "stage", "judgment", "watch_next"):
            if not isinstance(section.get(field), str) or not section[field].strip():
                raise ValueError(f"{prefix}.{field} is required")
        if section.get("significance") not in allowed_significance:
            raise ValueError(
                f"{prefix}.significance must be one of {sorted(allowed_significance)}"
            )
        dataset_ids = section.get("dataset_ids")
        if (
            not isinstance(dataset_ids, list)
            or not dataset_ids
            or any(not isinstance(dataset_id, str) or not dataset_id.strip() for dataset_id in dataset_ids)
        ):
            raise ValueError(f"{prefix}.dataset_ids must be a non-empty array")
        unknown_ids = sorted(set(dataset_ids) - changed_ids)
        if unknown_ids:
            raise ValueError(
                f"{prefix}.dataset_ids contains datasets without new or revised results: "
                + ", ".join(unknown_ids)
            )

    candidates = synthesis.get("deep_dive_candidates", [])
    if (
        not isinstance(candidates, list)
        or any(not isinstance(item, str) or not item.strip() for item in candidates)
        or len(candidates) > 3
    ):
        raise ValueError("run.synthesis.deep_dive_candidates must contain at most 3 strings")


def validate_run_summary(run: dict[str, Any]) -> None:
    changed = any(
        item.get("status") in {"new", "revision"}
        for item in run.get("results", [])
    )
    if changed:
        return
    summary = run.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("run.summary is required when no new or revised items exist")


def daily_markdown(run: dict[str, Any]) -> str:
    results = run.get("results", [])
    changed = [item for item in results if item.get("status") in {"new", "revision"}]
    unchanged = [item for item in results if item.get("status") == "unchanged"]
    lines = [f"# 官方数据日报 {run['date']}", "", f"- 成功检查：{len(run.get('checked', []))}",
             f"- 新发布或修订：{len(changed)}", f"- 已知且未变化：{len(unchanged)}",
             f"- 错误：{len(run.get('errors', []))}", ""]
    synthesis = run.get("synthesis")
    summary = synthesis.get("headline", "") if changed and isinstance(synthesis, dict) else run.get("summary", "")
    lines.extend(["## 今日判断", "", summary, ""])
    if changed and isinstance(synthesis, dict):
        for section in synthesis.get("sections", []):
            lines.extend([
                f"### {section.get('scope', '综合')}",
                "",
                f"- 重要性：`{section.get('significance', 'medium')}`",
                f"- 所处阶段：{section.get('stage', '')}",
                f"- 判断：{section.get('judgment', '')}",
                f"- 下一步验证：{section.get('watch_next', '')}",
                "",
            ])
        candidates = synthesis.get("deep_dive_candidates", [])
        if candidates:
            lines.extend(["### 值得深挖", ""] + [f"- {item}" for item in candidates] + [""])
        lines.extend([f"综合判断置信度：`{synthesis.get('confidence', 'medium')}`", ""])
    if changed:
        lines.extend(["## 新发布与修订", ""])
        for item in changed:
            path = item.get("record_path", "")
            lines.append(f"- `{item.get('status')}` `{item.get('dataset_id')}`：[{path}]({path})")
        lines.append("")
    if run.get("errors"):
        lines.extend(["## 待重试", ""])
        for error in run["errors"]:
            lines.append(f"- `{error.get('dataset_id')}`：{error.get('message')}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def command_finish(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    run = read_json(Path(args.input))
    for field in ("date", "started_at", "coverage_end", "finished_at", "checked", "results", "errors"):
        if field not in run:
            raise ValueError(f"run.{field} is required")
    local_tz = dt.datetime.now().astimezone().tzinfo
    started_at = optional_datetime(run["started_at"], local_tz)
    coverage_end = optional_datetime(run["coverage_end"], local_tz)
    finished_at = optional_datetime(run["finished_at"], local_tz)
    if started_at is None or coverage_end is None or finished_at is None:
        raise ValueError("run timestamps must use ISO 8601")
    if not started_at <= coverage_end <= finished_at:
        raise ValueError("run timestamps must satisfy started_at <= coverage_end <= finished_at")
    validate_synthesis(run)
    validate_run_summary(run)
    p = runtime_paths(root)
    state = read_json(p["state"], initial_state())
    for dataset_id in run["checked"]:
        ds_state = state.setdefault("datasets", {}).setdefault(dataset_id, {})
        ds_state["last_checked_at"] = run["coverage_end"]
        ds_state["last_attempted_at"] = run["finished_at"]
        ds_state.pop("last_error", None)
    for error in run["errors"]:
        dataset_id = error.get("dataset_id")
        if dataset_id:
            ds_state = state.setdefault("datasets", {}).setdefault(dataset_id, {})
            ds_state["last_attempted_at"] = run["finished_at"]
            ds_state["last_error"] = error.get("message", "unknown error")
    state["updated_at"] = now_iso()
    atomic_write_json(p["state"], state)
    compact = {
        "date": run["date"], "started_at": run["started_at"],
        "coverage_end": run["coverage_end"], "finished_at": run["finished_at"],
        "checked_count": len(run["checked"]),
        "new_count": sum(item.get("status") == "new" for item in run["results"]),
        "revision_count": sum(item.get("status") == "revision" for item in run["results"]),
        "unchanged_count": sum(item.get("status") == "unchanged" for item in run["results"]),
        "error_count": len(run["errors"]),
        "synthesis_section_count": len(run.get("synthesis", {}).get("sections", [])),
    }
    with p["runs"].open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(compact, ensure_ascii=False, sort_keys=True) + "\n")
    daily_path = p["daily"] / f"{run['date']}.md"
    atomic_write_text(daily_path, daily_markdown(run))
    return {"status": "run-finished", "daily_report": relative_to_cwd(daily_path), **compact}


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    state = read_json(runtime_paths(root)["state"], initial_state())
    if args.dataset:
        return {
            "dataset_id": args.dataset,
            "state": state.get("datasets", {}).get(args.dataset),
            "releases": [value for value in state.get("releases", {}).values()
                         if value.get("dataset_id") == args.dataset],
        }
    return {"updated_at": state.get("updated_at"), "dataset_state_count": len(state.get("datasets", {})),
            "release_count": len(state.get("releases", {})), "datasets": state.get("datasets", {})}


def command_validate_sources(args: argparse.Namespace) -> dict[str, Any]:
    errors = validate_sources_data(read_json(runtime_paths(Path(args.root))["sources"]))
    return {"status": "valid" if not errors else "invalid", "errors": errors}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "plan", "set-schedule", "commit", "finish", "status", "validate-sources"):
        child = sub.add_parser(name)
        child.add_argument("--root", default="work/official-data")
        if name == "plan":
            child.add_argument("--date")
        elif name in {"set-schedule", "commit", "finish"}:
            child.add_argument("--input", required=True)
        elif name == "status":
            child.add_argument("--dataset")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    commands = {"init": command_init, "plan": command_plan, "set-schedule": command_set_schedule,
                "commit": command_commit, "finish": command_finish, "status": command_status,
                "validate-sources": command_validate_sources}
    try:
        result = commands[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1 if result.get("status") == "invalid" else 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
