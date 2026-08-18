#!/usr/bin/env python3
"""Separate state and prospective records for configured market commentary."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SOURCE_ID = "citadel-securities-market-insights"
CATEGORY_URL = "https://www.citadelsecurities.com/news-and-insights/category/market-insights/"
CATEGORY_SITEMAP_URL = "https://www.citadelsecurities.com/category-sitemap.xml"
POST_SITEMAP_URL = "https://www.citadelsecurities.com/post-sitemap.xml"
ALLOWED_HOSTS = {"citadelsecurities.com", "www.citadelsecurities.com"}
ARTICLE_PREFIX = "/news-and-insights/"


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def paths(root: Path) -> dict[str, Path]:
    base = root / "market-insights"
    return {
        "base": base,
        "state": base / "state.json",
        "records": base / "records",
    }


def initial_state() -> dict[str, Any]:
    return {
        "version": 1,
        "source_id": SOURCE_ID,
        "category_url": CATEGORY_URL,
        "last_successful_check": None,
        "last_attempted_at": None,
        "last_error": None,
        "category_lastmod": None,
        "items": {},
    }


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_input(value: str) -> Any:
    if value == "-":
        return json.load(sys.stdin)
    return read_json(Path(value))


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temp.replace(path)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content.rstrip() + "\n")
    temp.replace(path)


def load_state(root: Path) -> dict[str, Any]:
    state = read_json(paths(root)["state"], initial_state())
    if not isinstance(state, dict) or state.get("source_id") != SOURCE_ID:
        raise ValueError("market-insight state is invalid or belongs to another source")
    state.setdefault("items", {})
    return state


def command_init(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    p = paths(root)
    p["records"].mkdir(parents=True, exist_ok=True)
    if not p["state"].exists():
        atomic_write_json(p["state"], initial_state())
    return {"status": "initialized", "state": str(p["state"])}


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    state = load_state(root)
    known = [
        {"url": url, **metadata}
        for url, metadata in sorted(
            state["items"].items(),
            key=lambda item: item[1].get("first_seen_at", ""),
            reverse=True,
        )
    ]
    return {
        "source_id": SOURCE_ID,
        "category_url": CATEGORY_URL,
        "category_sitemap_url": CATEGORY_SITEMAP_URL,
        "post_sitemap_url": POST_SITEMAP_URL,
        "baseline_required": state.get("last_successful_check") is None,
        "last_successful_check": state.get("last_successful_check"),
        "last_attempted_at": state.get("last_attempted_at"),
        "category_lastmod": state.get("category_lastmod"),
        "known_items": known,
    }


def validate_url(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("url is required")
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("url must be an HTTPS Citadel Securities URL")
    if not parsed.path.startswith(ARTICLE_PREFIX) or "/category/" in parsed.path:
        raise ValueError("url must identify a Citadel Securities article")
    return value.strip()


def require_text(record: dict[str, Any], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()


def validate_record(record: Any, baseline: bool) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    record = dict(record)
    record["url"] = validate_url(record.get("url"))
    record["title"] = require_text(record, "title")
    if baseline:
        for field in ("series", "published_at"):
            if field in record and record[field] is not None and not isinstance(record[field], str):
                raise ValueError(f"{field} must be a string when present")
        return record

    for field in ("published_at", "retrieved_at", "series", "summary_zh"):
        record[field] = require_text(record, field)
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("evidence must be a non-empty array")
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("each evidence item must be an object")
        require_text(item, "fact")
        require_text(item, "basis")
    forecasts = record.get("forecasts", [])
    if not isinstance(forecasts, list):
        raise ValueError("forecasts must be an array")
    for item in forecasts:
        if not isinstance(item, dict):
            raise ValueError("each forecast must be an object")
        for field in ("claim", "horizon", "verification"):
            require_text(item, field)
    caveats = record.get("caveats", [])
    if not isinstance(caveats, list) or any(not isinstance(item, str) for item in caveats):
        raise ValueError("caveats must be an array of strings")
    return record


def safe_segment(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9-]+", "-", value).strip("-").lower()
    return value[:80] or hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def markdown_record(record: dict[str, Any]) -> str:
    lines = [
        f"# {record['title']}",
        "",
        "- 来源：Citadel Securities Market Insights（机构市场观点，非官方数据）",
        f"- 发布日期：{record['published_at']}",
        f"- 检索时间：{record['retrieved_at']}",
        f"- 系列：{record['series']}",
    ]
    if record.get("author"):
        lines.append(f"- 作者：{record['author']}")
    lines.extend(["", "## 核心判断", "", record["summary_zh"], "", "## 主要证据", ""])
    for item in record["evidence"]:
        lines.append(f"- {item['fact']}（依据：{item['basis']}）")
    forecasts = record.get("forecasts", [])
    if forecasts:
        lines.extend(["", "## 可验证预测", ""])
        for item in forecasts:
            lines.append(
                f"- {item['claim']}；窗口：{item['horizon']}；验证：{item['verification']}"
            )
    caveats = record.get("caveats", [])
    lines.extend(["", "## 边界", ""])
    if caveats:
        lines.extend(f"- {item}" for item in caveats)
    lines.append("- 这是出版方观点及其所引用数据的记录，不是独立验证，也不构成投资建议。")
    lines.extend(["", f"[原文]({record['url']})"])
    return "\n".join(lines)


def command_commit(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    p = paths(root)
    state = load_state(root)
    record = validate_record(read_input(args.input), args.baseline)
    url = record["url"]
    if url in state["items"]:
        return {"status": "unchanged", "url": url}

    seen_at = record.get("retrieved_at") or args.seen_at or now_iso()
    item = {
        "title": record["title"],
        "series": record.get("series", ""),
        "published_at": record.get("published_at", ""),
        "first_seen_at": seen_at,
        "baseline": bool(args.baseline),
    }
    result: dict[str, Any] = {"status": "baseline" if args.baseline else "new", "url": url}
    if not args.baseline:
        slug = safe_segment(urlparse(url).path.rstrip("/").split("/")[-1])
        date = safe_segment(record["published_at"][:10])
        json_path = p["records"] / f"{date}--{slug}.json"
        md_path = p["records"] / f"{date}--{slug}.md"
        atomic_write_json(json_path, record)
        atomic_write_text(md_path, markdown_record(record))
        item["record_path"] = str(md_path)
        result["record_path"] = str(md_path)
    state["items"][url] = item
    atomic_write_json(p["state"], state)
    return result


def command_finish(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root)
    state = load_state(root)
    result = read_input(args.input)
    if not isinstance(result, dict):
        raise ValueError("finish input must be a JSON object")
    checked_at = result.get("checked_at")
    if not isinstance(checked_at, str) or not checked_at.strip():
        raise ValueError("checked_at is required")
    state["last_attempted_at"] = checked_at
    if result.get("checked") is True:
        lastmod = result.get("category_lastmod")
        if not isinstance(lastmod, str) or not lastmod.strip():
            raise ValueError("category_lastmod is required for a successful check")
        state["last_successful_check"] = checked_at
        state["category_lastmod"] = lastmod
        state["last_error"] = None
        status = "watch-finished"
    else:
        error = result.get("error")
        if not isinstance(error, str) or not error.strip():
            raise ValueError("error is required for a failed check")
        state["last_error"] = error
        status = "watch-error-recorded"
    atomic_write_json(paths(root)["state"], state)
    return {
        "status": status,
        "last_successful_check": state.get("last_successful_check"),
        "category_lastmod": state.get("category_lastmod"),
        "known_count": len(state["items"]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, handler in (("init", command_init), ("plan", command_plan)):
        child = sub.add_parser(name)
        child.add_argument("--root", required=True)
        child.set_defaults(handler=handler)

    commit = sub.add_parser("commit")
    commit.add_argument("--root", required=True)
    commit.add_argument("--input", required=True)
    commit.add_argument("--baseline", action="store_true")
    commit.add_argument("--seen-at")
    commit.set_defaults(handler=command_commit)

    finish = sub.add_parser("finish")
    finish.add_argument("--root", required=True)
    finish.add_argument("--input", required=True)
    finish.set_defaults(handler=command_finish)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        output = args.handler(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
