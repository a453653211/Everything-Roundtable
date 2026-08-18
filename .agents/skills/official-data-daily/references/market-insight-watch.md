# Citadel Securities Market-Insight Watch

Use this only after the official-data run is finished. It is a separate publisher-commentary lane and never changes official source coverage or conclusions.

## Source and state

- Source ID: `citadel-securities-market-insights`
- Category: `https://www.citadelsecurities.com/news-and-insights/category/market-insights/`
- Cheap change signal: `https://www.citadelsecurities.com/category-sitemap.xml`
- Optional discovery cross-check: `https://www.citadelsecurities.com/post-sitemap.xml`
- State: `work/official-data/market-insights/state.json`
- Records: `work/official-data/market-insights/records/`

Run from the repository root:

```powershell
python "$MARKET_WATCH_SCRIPT" init --root "$RUNTIME"
python "$MARKET_WATCH_SCRIPT" plan --root "$RUNTIME"
```

## Daily procedure

1. Fetch `category-sitemap.xml` and read the `lastmod` for the exact Market Insights category URL.
2. If it equals `plan.category_lastmod`, call `finish` as a successful unchanged check. Do not open article pages.
3. If it differs or `baseline_required` is true, open the category page in a normal browser. Direct non-browser requests may return `403`; do not replace the page with search snippets.
4. Read page 1 only and collect every visible article's title, canonical URL, and series. The optional post sitemap can confirm a URL and `lastmod`, but cannot by itself prove category membership.
5. On the first run, submit the current page-1 items with `commit --baseline`. Do not alert on this historical baseline or backfill older pages.
6. Later, compare page-1 URLs with `plan.known_items`. Open only unseen articles. Stage all new records before committing any; if an unseen article cannot be read, finish with an error and commit none so it remains retryable.
7. For each readable new article, capture its title, author, publication date, series, one-sentence Chinese summary, 1-3 concrete evidence points, any explicit forecast with horizon and verification signal, and caveats. Commit it through the script.
8. Finish only after the category window is fully checked. A failed check must not advance the separate watermark.

Pass JSON by file or stdin (`--input -`). Required non-baseline shape:

```json
{
  "url": "https://www.citadelsecurities.com/news-and-insights/.../article/",
  "title": "Article title",
  "published_at": "2026-08-11",
  "retrieved_at": "2026-08-16T07:00:00+08:00",
  "series": "Global Market Intelligence",
  "author": "Author name",
  "summary_zh": "一句话概括作者的核心判断",
  "evidence": [
    {"fact": "文中给出的具体数据或观察", "basis": "Citadel平台数据、外部数据汇编或作者判断"}
  ],
  "forecasts": [
    {"claim": "明确的方向性判断", "horizon": "时间范围", "verification": "以后用什么数据验证"}
  ],
  "caveats": ["来源边界、口径或反例"]
}
```

## Interpretation and output

Treat the article as primary evidence of what Citadel Securities and its named author said. Treat publisher platform-flow data as first-party observation, not independent confirmation. Treat Bloomberg or other compiled figures according to the named underlying source. Treat forward-looking language as a forecast, never as a fact.

Do not claim the publisher is accurate from reputation or one successful call. The stored forecasts form a prospective ledger for later evaluation against their stated horizon and verification signal.

Alert only for `new`:

```text
市场洞察提醒（Citadel Securities；机构观点，非官方数据）
- 标题 / 日期 / 系列 / 原文
- 核心判断
- 主要证据（1-3条，标明依据）
- 可验证预测与观察窗口（若有）
- 边界：非独立验证，不构成投资建议
```

For `unchanged` or a baseline, say nothing unless the user asks for monitoring details. Never merge this section into `今日判断` or create an official release card.
