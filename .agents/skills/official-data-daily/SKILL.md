---
name: official-data-daily
description: Incrementally collect and analyze new or revised official macroeconomic, financial, trade, housing, fiscal, employment, price, energy, central-bank, and Shanghai city/district data or planning events, with a strictly separate watch for configured institution-published market commentary. Use for daily monitoring, multi-month retrospectives, coverage audits, release-calendar checks, deduplication, revision detection, market-insight alerts, and concise source-grounded analysis.
---

# Official Data Daily

Run an idempotent daily monitor: inspect compact local state first, visit only due official sources, process only new or revised releases, synthesize what matters across them, and persist reusable data cards for later tasks.

## Hard Rules

- Accept only the exact official sources registered in `work/official-data/sources.json`. Treat media, research firms, social posts, and search snippets as discovery leads, never as completed collection.
- Separate `reference_period` from `published_at`.
- Use `dataset_id + reference_period` as the natural release key. Let the state script compare content fingerprints.
- If the key and fingerprint are unchanged, skip extraction and analysis.
- If the key exists but the fingerprint changes, record an official revision as a new version.
- Never manually edit `state/state.json` or `state/runs.jsonl`; use the bundled script.
- Treat each dataset's `last_checked_at` as its successful coverage watermark; failed checks never advance it.
- Do not write routine monitoring output into `library/`. A separate caller may later invoke `library-integrate` for a durable conclusion.
- Do not manufacture values when an official page is unavailable. Record the error and retry on the next run.
- Use `tavily-skill` only as a constrained discovery fallback when a registered official endpoint cannot be accessed or located. Tavily results do not establish coverage.
- Keep statistical series and official events distinct. A draft plan, approval, budget, construction notice, and completed project are different stages.
- Keep configured market commentary outside the official registry, official release cards, official synthesis, and official watermarks. Label it as publisher analysis, not official data or independently verified fact.

## Runtime

Use repository-relative runtime root `work/official-data/`.

Run commands from the repository root. Set:

```text
SKILL_DIR=<the directory containing this SKILL.md>
STATE_SCRIPT=<SKILL_DIR>/scripts/official_data_state.py
MARKET_WATCH_SCRIPT=<SKILL_DIR>/scripts/market_insight_state.py
RUNTIME=work/official-data
```

Read `references/runtime-schema.md` before creating a schedule or release record. Read `references/analysis-protocol.md` before analyzing a new or revised release. Also read `references/shanghai-monitoring.md` when any due dataset has `region: CN-SH` or the task is a Shanghai retrospective or coverage audit.

For the configured Citadel Securities watch, read `references/market-insight-watch.md` and run it only as the separate final lane described there.

## Mode Selection

- **Daily incremental mode:** follow `init -> plan -> commit -> finish -> plan`; the returned `due_datasets` and `scan_window` are the browsing boundary.
- **Retrospective or coverage-audit mode:** read current state and sources, then define a compact manifest covering the publication-date window, geography, required evidence lanes, registered listings, and known gaps. Do not reuse today's `due_datasets` as historical scope or move routine watermarks merely because history was reviewed. Store the review under `work/official-data/retrospectives/` unless the user explicitly requests ingestion through `commit`.

For Shanghai geography semantics, mandatory lanes, and strategic-plan inclusion rules, follow `references/shanghai-monitoring.md`. A required lane without a verified registered endpoint is a named coverage gap, not implicit completeness.

## Daily Workflow

### 1. Initialize and plan before browsing

```powershell
python "$STATE_SCRIPT" init --root "$RUNTIME"
python "$STATE_SCRIPT" plan --root "$RUNTIME"
```

The plan is the token budget boundary. Do not inspect datasets absent from `due_datasets`. Each due item includes its incremental `scan_window`; it may span several missed days. When `baseline_required` is true, establish the current official baseline once rather than inventing a historical lower bound. Preserve the final plan's `coverage_end` for `finish`.

If `calendar_refresh_required` is true:

1. Open only the returned official `calendar_urls`.
2. For each `calendar_source`, cover its returned `scan_window` plus the upcoming schedule horizon, including events missed since the previous successful check.
3. Mark every enabled calendar-driven dataset as covered, even when it has no event in that period.
4. Create a schedule JSON matching `references/runtime-schema.md`, store it with `set-schedule`, then rerun `plan`.

### 2. Check listing pages cheaply

For each due dataset:

1. Open its registered `release_url` or official API/listing endpoint.
   - When `release_urls` is returned, inspect each registered listing relevant to the dataset.
   - Apply returned `filters` to avoid collecting unrelated notices from broad official listings.
2. Walk entries newest-first until crossing `scan_window.start_exclusive`; collect every release or update inside the window, not only the newest one.
3. Compare with `latest_known`, then process unseen periods oldest-first. If none exists and no revision is indicated, stop without opening older history.
4. If direct access or official listing navigation fails, use `tavily-skill` as fallback discovery, constrained to the registered official domain and relevant `scan_window`; build the query from the dataset name, indicators, and returned `filters`.
   - Treat each result as a lead and open the canonical official page before extraction.
   - Do not substitute a media reproduction or count the dataset as checked unless its full `scan_window` was covered.
   - If fallback discovery is unavailable or insufficient, record an access error and leave the watermark unchanged.

### 3. Extract only new or possibly revised releases

Open the official release and capture:

- exact title and canonical official URL;
- publication timestamp and data reference period;
- metric, value, unit, seasonal basis, comparison basis, and status such as preliminary or final;
- explicit historical revisions and methodology changes;
- official tables or API series identifiers used.

For `record_type: event`, capture the administrative stage, planning level, spatial scope, stated change, decision or comment date, and next required official step. Use a stable event key rather than a statistical reference month.

Create one staging JSON record per changed release. Use the available file-editing tool rather than shell redirection.

Before analysis, open only `previous_record` from the plan when it exists. Do not reread the whole archive.

### 4. Analyze compactly

Follow `references/analysis-protocol.md`. For Shanghai datasets, also follow `references/shanghai-monitoring.md`. Keep fact, calculation, and inference separate. Do not add market consensus or third-party estimates unless a future caller explicitly broadens the source policy.

Translate related official indicators into an intuitive behavioral chain when evidence permits: what choice changed, what constraint could cause it, which group may be more exposed, and which next official indicator can verify or falsify that reading. Never jump from one category to a social-group conclusion.

Write user-facing `headline` and `behavioral_readout` in concise Chinese unless the caller requests another language. `commit` rejects new or revised records without them.

### 5. Commit idempotently

```powershell
python "$STATE_SCRIPT" commit --root "$RUNTIME" --input <staging-record.json>
```

Interpret the result:

- `new`: new reference period; include it in today's report.
- `revision`: same reference period, changed official content; state exactly what changed.
- `unchanged`: discard the staging record and produce no duplicate analysis.

The script writes versioned JSON and Markdown data cards and updates the compact index atomically.

### 6. Add the judgment layer

When any commit is `new` or `revision`, synthesize the changed items before finishing:

1. Write one overall judgment about what matters today.
2. Add 1-3 grouped judgments using only useful scopes such as `上海`, `全国`, or `全球`.
3. For each group, state importance, current stage, bounded meaning, and the next official verification point.
4. Name at most three deep-dive candidates. Do not recommend routine items merely because many were released.

Follow the cross-release synthesis rules in `references/analysis-protocol.md`. Put the result in `run-result.json` as `synthesis`; `finish` rejects changed runs without it.

### 7. Finish every run

Create a run-result JSON containing the plan's `coverage_end`, successful checks, commit results, errors, and either changed-item `synthesis` or a no-change `summary`, then run:

```powershell
python "$STATE_SCRIPT" finish --root "$RUNTIME" --input <run-result.json>
```

Count a dataset as `checked` only after its full `scan_window` was inspected. Put access failures under `errors`; failures remain eligible with the same lower bound.

### 8. Run the separate market-insight watch

After the official `finish`, follow `references/market-insight-watch.md`. This lane is a narrow exception to the official-source-only browsing boundary, not an official dataset:

- do not add it to `sources.json`, `due_datasets`, official `releases/`, or official `synthesis`;
- establish a current-page baseline once, then alert only on a newly listed article URL;
- retain a compact prospective forecast record when an article makes a testable claim;
- if access fails, keep its separate watermark unchanged and report the failure without affecting the official run.

## Output

Return a short daily result:

1. `今日判断`: one overall sentence.
2. Grouped judgments with importance, stage, meaning, and next verification.
3. Up to three items worth deeper investigation.
4. New releases and official revisions.
5. Checked with no change, errors, and clickable artifact paths.
6. When present, a separate `市场洞察提醒` containing only newly discovered configured commentary.

When Shanghai items changed, separate `上海数据` from `上海规划与项目`; always state the stage for planning or project events.

If there is no new or revised official data, omit official synthesis and say so in one sentence. A new market-insight alert may still follow in its clearly labeled separate section.

## Scope Changes

- Add a dataset only after verifying a direct official release/archive and at least one historical issue.
- Give every dataset an immutable, descriptive `dataset_id`.
- Use `record_type: series` for repeated metrics and `record_type: event` for plans, notices, decisions, budgets, and project milestones.
- Use `check_policy.mode: interval` for irregular sources that should be revisited after `interval_days`; add `months` only when the official publication season is established.
- Keep ambiguous themes such as “local housing,” “judicial enforcement,” or “policy changes” out of the registry until they are decomposed into a named metric, jurisdiction, and exact official endpoint.
- Validate `sources.json` after editing it:

```powershell
python "$STATE_SCRIPT" validate-sources --root "$RUNTIME"
```
