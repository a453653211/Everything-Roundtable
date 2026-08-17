# Runtime Schema

## Directory Layout

```text
work/official-data/
├── sources.json
├── schedule.json
├── state/
│   ├── state.json
│   └── runs.jsonl
├── releases/<dataset-id>/<reference-period>--vN.{json,md}
└── daily/YYYY-MM-DD.md
```

`state.json` is a compact index, not a research document. Read it through `plan` or `status`; open release cards only when their paths are returned as relevant context.

## Source Registry

Each source requires `dataset_id`, `name`, `institution`, `release_url`, `official_domain`, and `check_policy`.

Optional routing fields:

- `jurisdiction`: human-readable geographic scope such as `上海市`;
- `record_type`: `series` (default) or `event`;
- `release_urls`: multiple registered official listings; it must include `release_url`;
- `official_domains`: multiple allowed official domains; it must include `official_domain`;
- `filters`: title or content terms used to keep a broad official listing in scope.

Supported check modes:

- `daily`;
- `weekly` with `weekdays` (`0` is Monday);
- `window` with inclusive `day_windows`;
- `calendar`;
- `interval` with positive `interval_days`.

`daily`, `weekly`, `window`, and `interval` may include `months` as integers from `1` to `12`.

## Plan Output

Each due dataset includes:

```json
"scan_window": {
  "start_exclusive": "2026-07-29T20:10:00+08:00",
  "end_inclusive": "2026-08-01T10:20:00+08:00"
}
```

This is a per-dataset coverage window, not merely the current calendar day. Walk an official listing far enough to cover every item in the window. A missing lower bound is returned as `baseline_required: true`: inspect the current official listing and establish its latest valid release as a one-time baseline, without inventing an unlimited historical backfill.

## Schedule Input

```json
{
  "refreshed_at": "2026-07-12T09:00:00+08:00",
  "covered_datasets": ["cn-nbs-cpi"],
  "events": [
    {
      "dataset_id": "cn-nbs-cpi",
      "expected_at": "2026-08-10T09:30:00+08:00",
      "window_start": "2026-08-10",
      "window_end": "2026-08-11",
      "reference_period": "2026-07",
      "calendar_url": "https://www.stats.gov.cn/fbyg/"
    }
  ]
}
```

Use ISO 8601 timestamps. `window_start` and `window_end` are inclusive calendar dates in the release institution's relevant timezone.

`covered_datasets` must list every enabled calendar-driven dataset reviewed during the refresh, including datasets with no event in the covered period. For each item returned in `plan.calendar_sources`, calendar review must include its `scan_window` as well as the upcoming schedule horizon; `baseline_required` has the same one-time, non-historical meaning described above. `set-schedule` rejects incomplete dataset coverage so an omitted release cannot silently become “not due.”

## Release Record Input

```json
{
  "dataset_id": "cn-nbs-cpi",
  "reference_period": "2026-06",
  "published_at": "2026-07-10T09:30:00+08:00",
  "retrieved_at": "2026-07-10T18:30:00+08:00",
  "source_title": "2026年6月份居民消费价格……",
  "source_url": "https://www.stats.gov.cn/...",
  "release_status": "official",
  "values": [
    {
      "metric": "CPI",
      "value": 1.2,
      "unit": "%",
      "basis": "同比",
      "seasonal_adjustment": "原始值",
      "note": ""
    }
  ],
  "revisions": [],
  "methodology_changes": [],
  "analysis": {
    "headline": "一句话事实判断",
    "changes": ["相对上期发生了什么"],
    "behavioral_readout": "把多个分项翻译成普通人可以感知的选择变化",
    "affected_groups": [
      {
        "group": "可能受影响的人群",
        "inference": "为什么这组官方数据更指向该人群",
        "confidence": "medium"
      }
    ],
    "implications": ["有事实支撑的有限推论"],
    "alternative_explanations": ["可能产生同样数据表现的其他机制"],
    "verification_needed": ["下一项用于证实或证伪的官方指标"],
    "caveats": ["口径、缺项或不可比较处"],
    "confidence": "high"
  },
  "official_citations": [
    {
      "label": "国家统计局原文",
      "url": "https://www.stats.gov.cn/..."
    }
  ]
}
```

Required fields are `dataset_id`, `reference_period`, `published_at`, `retrieved_at`, `source_title`, `source_url`, and non-empty `values`. When the fingerprint is new or changed, `analysis.headline`, `analysis.behavioral_readout`, and `analysis.confidence` are also required. An unchanged fingerprint returns `unchanged` without requiring duplicate analysis.

For `record_type: event`, keep the same release-record schema but use a stable event-and-stage key as `reference_period`. Put the administrative stage, spatial scope, exact change, and relevant dates into `values`.

The script computes the content fingerprint from source identity, dates, values, revisions, and methodology changes. Analysis prose is deliberately excluded so rewriting prose cannot create a false revision.

## Run Result Input

```json
{
  "date": "2026-07-12",
  "started_at": "2026-07-12T18:30:00+08:00",
  "coverage_end": "2026-07-12T18:30:05+08:00",
  "finished_at": "2026-07-12T18:42:00+08:00",
  "checked": ["cn-nbs-cpi", "cn-pbc-financial"],
  "results": [
    {
      "dataset_id": "cn-nbs-cpi",
      "status": "new",
      "record_path": "work/official-data/releases/cn-nbs-cpi/2026-06--v1.md"
    }
  ],
  "synthesis": {
    "headline": "今天最值得注意的是价格变化尚未得到需求侧数据的同步确认。",
    "sections": [
      {
        "scope": "全国",
        "dataset_ids": ["cn-nbs-cpi"],
        "significance": "medium",
        "stage": "统计结果已发布，机制解释仍待验证",
        "judgment": "价格变化本身有意义，但不足以单独证明需求发生趋势性转折。",
        "watch_next": "下一期社会消费品零售总额及居民收入支出数据"
      }
    ],
    "deep_dive_candidates": ["价格分项与消费量指标是否背离"],
    "confidence": "medium"
  },
  "errors": [
    {
      "dataset_id": "cn-customs-trade",
      "message": "official query timed out"
    }
  ]
}
```

When any result is `new` or `revision`, `synthesis` is required:

- `headline`: non-empty overall judgment;
- `sections`: 1-3 grouped judgments;
- `sections[].dataset_ids`: non-empty subset of datasets with changed results;
- `sections[].significance`: `high`, `medium`, `low`, or `routine`;
- `sections[].stage`, `judgment`, and `watch_next`: non-empty concise strings;
- `deep_dive_candidates`: optional array of at most three strings;
- `confidence`: `high`, `medium`, or `low`.

When there is no new or revised result, omit `synthesis` and provide a non-empty one-sentence `summary`, for example:

```json
"summary": "本次检查了2个到期官方来源，没有发现新增或官方修订，现有判断不变。"
```

Copy `plan.coverage_end` into the run result. Only full successful inspections of the returned `scan_window` belong in `checked`; `finish` advances their `last_checked_at` only to `coverage_end`, never the later task finish time. An error updates only `last_attempted_at`, so the uncovered interval remains due.
