# Shanghai Monitoring Protocol

Use this reference when a due dataset has `region: CN-SH`.

## Two Monitoring Lanes

Keep two distinct evidence models:

1. **Statistical series**: a repeated metric with a defined period, unit, coverage, and comparison basis.
2. **Official events**: a plan, public notice, decision, approval, budget, or project milestone whose meaning depends on its administrative stage.

Do not force a planning event into a growth-rate narrative. Do not treat a statistical movement as proof that a specific project or neighborhood will change.

## Registered Shanghai Sources

| Dataset | What it owns | Primary listing |
|---|---|---|
| `sh-tjj-activity` | Shanghai output, industry, investment, real estate development, consumption, trade, services, transport, and household income/expenditure | `https://tjj.sh.gov.cn/sjfb/index.html` |
| `sh-tjj-prices` | Shanghai CPI, PPI, purchasing-price indices, and published components | `https://tjj.sh.gov.cn/sjfb/index.html` |
| `sh-wsjkw-population` | Annual population monitoring, births, resident-registration coverage, age structure, and district detail actually published | `https://wsjkw.sh.gov.cn/tjsj2/index.html` |
| `sh-rsj-minimum-wage` | Monthly and hourly minimum-wage standards and exclusions | `https://rsj.sh.gov.cn/tgzfl_17732/index.html` |
| `sh-rsj-average-wage` | Full-caliber urban-unit average wage and social-insurance contribution bounds | Registered RSJ listings |
| `sh-ghzyj-approved-plans` | Municipal planning-resource statutory overall, unit, detailed, and special plans | `https://ghzyj.sh.gov.cn/shgtgh/index.html` |
| `sh-ghzyj-planning-notices` | Draft plans, detailed-plan changes, and public-comment notices | `https://ghzyj.sh.gov.cn/` |
| `sh-district-strategic-plans` | District-government development outlines plus strategic spatial-layout and urban-renewal plans | `https://www.shanghai.gov.cn/gwk/search/index.html` |
| `sh-jtw-transport-plans` | Formal rail, road, tunnel, and transport special-plan decisions | `https://jtw.sh.gov.cn/zdgc/index.html` |

For formal metro-planning status, prefer the Municipal Transportation Commission and Planning and Natural Resources Bureau. Treat Shanghai Metro's corporate site as a future supplementary construction/operation source, not as proof that a plan has been approved.

## Scope and Coverage

Translate the user's geography before browsing:

- `上海市级` means municipal statistics, departments, and citywide plans.
- `上海本地` or `上海重要信息` means the municipal lane plus district strategic plans unless the user narrows the scope.
- A named district means that district's registered strategic lane plus relevant municipal planning or statistical sources.

For a retrospective, list every applicable lane in the coverage manifest and mark it `covered`, `not due`, `failed`, or `unregistered`. Use the portal publication timestamp for interval inclusion. One pre-window governing plan may be opened as a labeled context anchor when an in-window plan depends on it, but it is not an in-window release.

## Statistical Extraction

For `sh-tjj-activity`, prioritize category detail over one headline:

- consumption: total retail sales plus published category or format detail;
- investment: total, sector, infrastructure, manufacturing, and real estate when comparable;
- housing: development investment, construction/completion, sales area, and other officially published operating measures;
- households: disposable income and consumption expenditure, with nominal/real and cumulative/current-period bases separated;
- production: industrial output, products, and profits without equating them directly to household demand.

For population releases, distinguish:

- births versus the stock of newborn residents;
- permanent-resident, registered-resident, and floating-population coverage;
- calendar-year reference period versus publication date;
- city total versus district distribution.

For wages, do not call the full-caliber urban-unit average wage the income of a typical Shanghai worker. Keep it separate from median pay, disposable income, minimum wage, and the social-insurance base.

## Planning Event Record

Use a stable event key as `reference_period`, preferably:

```text
YYYY-MM-DD--short-project-slug--stage
```

Store the event in `values` with rows such as:

- `行政阶段`: 草案公示 / 征求意见 / 审议通过 / 正式批复 / 设计方案公示 / 开工 / 完工;
- `规划层级`: 总体 / 单元 / 详细或控规 / 专项;
- `空间范围`: district, unit, parcel, line, road, tunnel, station, or work site;
- `核心变化`: only what the official document changes;
- `反馈截止日` or `批准日期`;
- `法律或执行状态`: the shortest defensible description.

Interpret the stage ladder conservatively:

```text
研究或目录
  -> 草案公示
  -> 审议或批复
  -> 项目立项/可研/初设
  -> 建设工程设计方案或施工许可
  -> 开工
  -> 完工或运营
```

A higher-level plan is direction, not parcel execution. A draft is not an approval. An approval is not funding. A design-scheme notice is not a demolition decision. Score significance separately from maturity and state the next required official step: a high-signal plan can remain unlanded, while a small completed project can be mature without citywide significance.

## District Strategic Plans

Classify candidates before deciding whether they belong in the judgment layer:

| Document class | Default handling |
|---|---|
| District-wide national-economic and social-development five-year outline | Mandatory candidate after district people's-congress approval or formal issuance |
| Formally issued district spatial-layout or urban-renewal five-year plan | Mandatory candidate when it names areas, measurable targets, or an implementation framework |
| Formal revision of either class | Revision candidate when it changes targets, boundaries, priorities, or responsibilities |
| Thematic five-year plan | Mechanical update unless it adds material targets, spatial allocation, funding/responsibility mechanisms, or a clear change from the governing outline |
| Compilation meeting, research/printing budget, or consultation activity | Record only at its actual preparatory stage; never treat it as an issued plan |

Retrieve candidates through the Shanghai Government policy-library search page and registered JSON endpoint. POST to `/gwk/search/data` with `pageNo`, `pageSize`, and `keyword`; send `unitType`, `publishDate`, `indexNo`, `documentAgency`, `documentPublishYear`, `documentNum`, and `theme` as blank filters. Paginate until every returned item is older than `scan_window.start_exclusive`, deduplicate keyword results by `id`, and construct detail URLs as `/gwk/search/content/<id>`. Retain title-matched district outlines, spatial-layout plans, and urban-renewal plans; a full-text mention alone is insufficient. Treat `display_date` as the portal timestamp and `publish_date` as a possible document/issuance date, verify both on the detail page, and extract scope, targets, stage, and next checkpoint. Do not substitute the non-exhaustive `近期信息公开` page.

## Housing Transactions: Pending Registration

`fangdi.com.cn` is an official Shanghai real-estate transaction-center domain. Its `https://www.fangdi.com.cn/old_house/old_house.html` surface reports the previous day's second-hand transaction count and area. The current monitor does not register it yet because both the homepage and this endpoint reject automated access with HTTP 412, and a stable historical archive or reproducible query has not been verified. A daily snapshot alone cannot reconstruct past calendar-month totals.

Do not substitute brokerage, research-firm, or media totals. Add this dataset only after verifying:

1. the exact official second-hand endpoint;
2. its coverage and cancellation/revision treatment;
3. at least one historical issue or query;
4. whether the period is calendar month, rolling 30 days, or daily cumulative.

Treat 18,000 and 30,000 units as user-defined watch thresholds, not official “prosperity lines.” Label them as thresholds and analyze crossings only after fixing the transaction definition and comparing same-definition history.

## District Renewal Budgets: Pending Expansion

District budget reports are official but not one standardized metric. Before registering each district, verify its stable budget-publication directory and at least two annual issues. Extract separately:

- land-acquisition cost settlement;
- old-neighborhood or old-town redevelopment settlement;
- land reserve and government-fund expenditure;
- special-bond funding;
- housing-expropriation-center departmental budgets;
- budget, adjusted budget, and final execution.

Do not rank districts using unmatched subjects. A high budget is financing capacity or intent, not proof that a named block will be expropriated. For a specific location, require a matching project, responsible body, planning basis, and later process signal.

Verified examples currently exist on the official Jing'an, Huangpu, and Hongkou domains, but stable district-by-district listing endpoints have not yet been registered. Keep them outside routine `due_datasets` until that source map is complete.

## Shanghai Output

Within the daily report, group changed Shanghai items into:

1. **上海数据**: combine new or revised statistical releases into one bounded city-level reading when their definitions permit.
2. **上海规划与项目**: state whether each meaningful signal is only a meeting/mention, draft, approval, funded action, active construction, or completed result.
3. **上海待补源**: only access errors or explicitly pending registered sources; do not fill gaps with third-party figures.
