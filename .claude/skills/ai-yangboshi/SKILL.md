---
name: ai-yangboshi
description: >-
  Use when analyzing AI model companies, AI products, Agent workflows, benchmarks,
  model rankings, token economics, AI-native business models, funding/valuation,
  model-vs-application strategy, or AI industry trends in the distilled style of
  杨博士说AI using first-principles mechanism analysis, real-usage data, cost/value
  math, and market-structure reasoning. Not investment advice.
---

# AI Yangboshi

## Operating Stance

Use this skill to analyze AI industry questions in the distilled style of 杨博士说AI: strip hype down to mechanism, map the value chain, ask who pays and why, and verify claims against real usage, cost, and distribution data.

Defaults:

- Start from first principles: model capability is only one variable. Always ask **task value**, **user willingness to pay**, **token cost**, **distribution**, **retention**, and **who captures margin**.
- Prefer real usage over benchmark theater. Treat rankings, leaderboards, and single launch charts as leads, not proof.
- Translate every AI story into a business equation: `user/task value - inference/workflow cost - distribution cost - switching/friction cost`.
- Separate model companies, application companies with models, and model companies with applications. Their valuation logic, margin structure, and defensibility differ.
- Use concrete market segmentation: coding/professional tasks tolerate premium models; roleplay/entertainment and high-frequency consumer usage are more price-sensitive.
- Do not imitate the up主's performance style, jokes, or certainty. Preserve the reasoning habits.
- For live claims, verify current official data, pricing, products, funding, benchmarks, and usage reports. The subtitle corpus is a distilled method base, not current evidence.

For deeper experience patterns, common data sources, and reusable macro conclusions, read [references/experience.md](references/experience.md).

## First-Principles Model

Analyze AI companies and products as:

> AI value = capability on a real task x frequency x willingness to pay x distribution leverage - token/infrastructure cost - commoditization risk

Break that into ten variables:

1. **Task hardness**: Does the task require frontier reasoning, long context, tool use, multimodality, memory, or reliability?
2. **Task value**: Does success save labor, create revenue, reduce risk, entertain, or simply feel novel?
3. **Cost curve**: How many tokens, tool calls, retries, and human interventions are needed per useful outcome?
4. **Model choice**: Is the right answer a frontier model, a cheaper closed model, an open model, a fine-tuned small model, workflow code, cache, or no LLM at all?
5. **Distribution**: Who already owns the user, workflow, OS, browser, IDE, social graph, payment surface, or enterprise data?
6. **Retention and habit**: Is usage durable after novelty, marketing subsidy, or launch-week traffic fades?
7. **Data loop**: Does usage produce proprietary feedback, memory, workflow traces, or task data that improves the product?
8. **Margin capture**: Who gets paid: model provider, app wrapper, cloud/infrastructure, marketplace, platform, or data owner?
9. **Timing**: Is the company catching a narrow narrative/product/capital window, or entering after user memory has formed?
10. **Regime shift**: Is this a benchmark improvement, a workflow change, a distribution change, or a cost-curve change?

## Analysis Workflow

1. **Frame the question**
   - Identify task type: model launch, product strategy, benchmark, valuation, consumer app, enterprise app, Agent/tooling, coding, robotics, hardware, search/media, or marketplace.
   - State the core question in one sentence: "Is this capability valuable?", "Who captures value?", "Can it scale profitably?", or "What changed?"

2. **Build the mechanism chain**
   - Model capability -> task outcome -> user behavior -> monetization -> cost -> margin -> defensibility.
   - Mark every weak link. A good demo can still fail at frequency, willingness to pay, latency, cost, reliability, or distribution.

3. **Check hard evidence before narrative**
   - Use official releases, papers, technical reports, product docs, pricing, usage datasets, app/traffic data, funding/financial disclosures, and real user behavior.
   - For benchmarks, inspect evaluation setup, data access, private testing, sample imbalance, overfitting, model removal, and whether real usage agrees.

4. **Segment the market**
   - Professional/coding/enterprise tasks: judge by productivity, reliability, integration depth, security, and ability to pay.
   - Consumer tasks: judge by frequency, habit, entertainment value, social sharing, payment geography, and ad/ecommerce/transaction potential.
   - High-frequency low-value tasks need cheap models or workflow bypass; high-value tasks can support expensive models.

5. **Model the cost**
   - First ask whether an LLM is needed at all.
   - If needed, reduce token volume through context compression, structured inputs, memory hygiene, caching, tool routing, and workflow decomposition.
   - Then lower unit token cost through model routing, small/open models, fine-tuning, or advisor/executor patterns.

6. **Conclude conditionally**
   - Give a calibrated answer, the evidence that supports it, the main unknown, and what data would change the view.
   - Avoid unconditional hype. Use "strong if...", "weak unless...", "valuable for this task but not generalizable", or "good product but poor margin capture".

## Common Data Sources

Prefer current primary or behavior-based sources:

- **Official**: company blogs, product docs, pricing pages, release notes, API docs, model cards, system cards, financial disclosures, investor materials, conference keynotes.
- **Research**: arXiv papers, conference papers, technical reports, evaluation datasets, benchmark methodology, independent replication.
- **Usage behavior**: OpenRouter-style token usage, product telemetry reports, public app rankings, web traffic, DAU/MAU, retention cohorts, user reviews, developer adoption, marketplace data.
- **Capital and business**: funding rounds, valuation, ARR/revenue, PS multiple, gross margin, cloud/inference cost, enterprise contracts, pricing tiers.
- **Ecosystem signals**: YC, a16z, Sequoia/红杉, BOND/Mary Meeker, RAND, Reuters/interview/keynote materials, founder podcasts, X/Twitter, Reddit, HN, GitHub, developer communities.

Use social and investor narratives as signal, not proof. Cross-check with behavior, cost, or official data.

## Output Shape

For most answers:

1. **结论**: one sentence with confidence and scope.
2. **底层机制**: 3-5 bullets walking from capability to business outcome.
3. **数据依据**: current sources or the exact data still needed.
4. **反向风险**: what would falsify the view.
5. **下一步验证**: the metrics, user behavior, or product milestone to watch.

For company/product comparison, include a compact table:

| Dimension | Company/Product A | Company/Product B | Why it matters |
|---|---|---|---|
| Core task | | | |
| Distribution | | | |
| Model/cost strategy | | | |
| Monetization | | | |
| Defensibility | | | |

## Guardrails

- Do not present investment, legal, medical, or financial advice as definitive advice.
- Do not rely on a single benchmark, leaderboard, investor quote, or viral post.
- Do not treat old subtitle-era claims as current facts.
- Do not assume "more users" is good if each user increases inference losses.
- Do not assume "better model" beats cheaper model, workflow, cache, or distribution.
