# Yangboshi AI Experience Notes

Use this reference when the question needs deeper 杨博士说AI-style patterns: recurring first-principles conclusions, data-source habits, or reusable frameworks for AI companies, models, and products.

## Thinking Habits

### Mechanism Before Headline

Convert every headline into a chain:

`technical change -> product behavior -> user habit -> monetization -> cost/margin -> market structure`.

If any link is missing, state it. A model launch is not automatically a business improvement. A user spike is not automatically retention. A benchmark jump is not automatically real utility.

### Real Usage Beats Exams

Benchmarks matter when they predict real workflows. Discount rankings when:

- model vendors can privately test many variants before publishing;
- closed models receive more feedback data than open models;
- improvement appears on one leaderboard but not on other tasks;
- model removal, sampling, or ranking rules are opaque;
- real users "vote with their feet" differently from the leaderboard.

OpenRouter-style usage is valuable because it reflects task selection, price sensitivity, and user switching. It is still biased by the platform's user base, so do not overgeneralize.

### Cost Is a Product Feature

Treat token cost as a production input, like electricity or bandwidth. The cost stack is:

1. Avoid LLM calls where workflow, cache, retrieval, rules, or deterministic code can solve the task.
2. Reduce token volume through context compression, structured state, shorter plans, memory hygiene, and less conversational waste.
3. Route by task difficulty: cheap/open/small models for routine work, frontier models for high-uncertainty judgment.
4. Use advisor/executor patterns: small model executes; frontier model supplies short plans, corrections, stop signals, or expert review.
5. Fine-tune smaller models for well-defined repeated tasks.

Core formula:

`total cost = calls x input tokens x output tokens x retries x tool overhead x unit price`.

Optimization should reduce total useful outcome cost, not just unit token price.

### Market Segmentation Is the Analysis

The same model can be premium in one market and commodity in another:

- Coding, agentic engineering, enterprise automation, legal/research, and high-stakes professional work can pay for reliability and frontier ability.
- Roleplay, entertainment, companion, translation, casual Q&A, and high-frequency consumer usage are more price-sensitive.
- Open models can win where "good enough + cheap + customizable" matters more than frontier quality.
- Closed frontier models win where small quality differences create large economic value.

Always ask: "For this task, is the user paying for intelligence, latency, reliability, privacy, entertainment, integration, or convenience?"

### Distribution and Workflow Trump Demo Quality

AI products win when they sit inside the user's existing workflow or own a new workflow:

- IDE, terminal, browser, OS, chat surface, search, commerce, enterprise system, and mobile hardware are distribution choke points.
- Agent platforms threaten traditional SaaS because the user may ask an agent to complete a task without opening the SaaS UI.
- SaaS companies try to avoid becoming mere tools by exposing agents, workflows, data structures, and protocol endpoints.
- A product with a weaker model but stronger workflow integration can beat a stronger model without distribution.

### Timing, Capital, and Narrative Are Real Inputs

For AI company valuation, he repeatedly uses three variables:

- **Narrative timing**: whether the story arrives in a narrow window when the market wants that category.
- **Growth velocity**: whether the company can plausibly move from tiny revenue to category leadership quickly.
- **Capital momentum**: whether funding, valuation, and growth reinforce each other.

This explains why model companies can price far above SaaS-like multiples and why "model company with applications" can be valued very differently from "application company with model access." But this is also the bubble mechanism, so separate narrative value from realized margin.

### User Metrics Need AI-Native Interpretation

Traditional internet metrics can mislead:

- Early AI consumer products attract "AI tourists" who try once and leave. Day-1 or month-1 retention can understate durable users.
- For prosumer products with paywalls, lower retention can coexist with better business quality if non-paying users are filtered out.
- M3/M12-style cohort durability can be more useful than immediate retention for novelty-heavy products.
- Marketing spikes can still be useful if they create user memory and repeated touch points, but they do not prove habit.
- More usage can hurt if inference cost rises faster than monetization.

Key AI product metrics: useful outcomes per session, cost per useful outcome, paid conversion, task recurrence, durable cohort retention, user willingness to wait/pay, and margin after model cost.

## Common Data-Source Habits

### Primary and Official Sources

Use official company material for what changed:

- OpenAI, Anthropic, Google DeepMind, Meta, xAI, Microsoft, Apple, NVIDIA, Tesla, Waymo, DeepSeek, Alibaba, ByteDance, MiniMax, Moonshot/Kimi, Zhipu, and similar company blogs, docs, release notes, pricing pages, model cards, system cards, and product announcements.
- API pricing and product terms when judging cost, routing, or monetization.
- Financial disclosures, investor letters, IPO/filing material, funding announcements, enterprise-contract news, and ARR/revenue/gross-margin claims when judging valuation.

### Papers, Reports, and Benchmarks

Common source types in the corpus:

- arXiv and conference papers for new methods, datasets, RL, agents, memory, context engineering, model routing, formal proof, robotics, and scientific discovery.
- Benchmark reports such as SWE-bench, Terminal-Bench, HumanEval-style coding tests, Chatbot Arena/LMSYS, Humanity's Last Exam, and domain-specific evaluation sets.
- Independent critique papers when evaluating leaderboard incentives and "gaming."
- University/company joint reports on usage behavior, such as ChatGPT usage reports with demographic, task, and work/non-work segmentation.

Use benchmark data only after checking methodology and real-workflow relevance.

### Usage, Traffic, and Product Behavior

Useful behavior sources:

- OpenRouter token usage and model/task share for real market segmentation.
- App/web traffic, download rankings, public DAU/MAU claims, retention cohorts, usage frequency, session length, user geography, and paid conversion.
- GitHub, developer communities, issue/PR activity, extension adoption, IDE/plugin usage, and tool-call traces for coding products.
- User reviews, Reddit, HN, X/Twitter, and Discord/community chatter as leads to behavior, not final proof.

### Investor, Founder, and Ecosystem Sources

Recurring ecosystem sources:

- a16z reports and roundtables for AI-native product patterns, consumer AI, developer tools, and infrastructure shifts.
- Sequoia/红杉 AI summit material for market structure and startup strategy.
- YC talks/interviews, especially Karpathy, Altman, and AI startup founder material.
- BOND/Mary Meeker-style internet trend reports for macro adoption and usage.
- Reuters NEXT, founder podcasts, keynote interviews, and public talks by Hassabis, Jensen Huang, Nadella, Musk, Altman, Karpathy, Andrew Ng, Reid Hoffman, and similar figures.
- RAND/think-tank reports for risk, safety, and policy scenarios.

Treat investor materials as sharp maps of what the market wants to believe. Verify with usage, cost, and product data.

## Reusable Macro Conclusions

### AI Is Moving From Benchmark Competition to Real-Utility Competition

The old question "which model scores highest?" is less useful than:

- Does it improve a real human-in-the-loop workflow?
- Does it accumulate memory or context across tasks?
- Does it lower useful outcome cost?
- Can users verify, correct, and steer it?

Future evaluation should include long-horizon tasks, memory, feedback loops, tool use, and human interaction rather than isolated one-shot tasks.

### Token Is a New Production Material

In AI-native companies, token consumption becomes an operating resource. A team can substitute token spend for human labor in coding, review, security scanning, regression testing, support, research, and content generation. The strategic question is not "is token expensive?" but "is the token spend cheaper than the labor or opportunity cost it replaces?"

### The Biggest Real AI Use Case Is Coding, But App Margins Are Fragile

Coding is one of the strongest real paid use cases because users pay for productivity and tolerate premium models. But coding-app companies that rely entirely on third-party frontier models can have weak or negative gross margin. Model providers launching their own coding products can both capture demand and compress downstream app companies.

### Model Companies With Applications Have More Optionality Than Application Companies With Models

An application company can be squeezed by model providers, platforms, or cheaper open models unless it owns workflow, data, distribution, or strong user habit. A model company with applications has a stronger story because it can internalize capability, distribution experiments, and data loops. This does not make every model company good; it explains why markets price optionality differently.

### Free Consumer AI Users Are Not Automatically Valuable

Most consumer users may be free, geographically mixed, and low ARPU. The monetization problem is:

- increase paid conversion;
- add advertising, shopping, transaction, media, marketplace, IP, or hardware-driven subscription revenue;
- increase usage frequency without blowing up inference cost;
- focus on high-ARPU regions and high-value user segments.

If free users increase compute losses faster than monetization, scale is negative leverage.

### AI-Native Business Models Are Broader Than Subscription

Recurring categories:

- subscription for prosumer or professional tools;
- enterprise agents that aggregate data and execute workflows;
- ecommerce/instant checkout embedded in AI conversations;
- media/search aggregation personalized by user intent;
- transaction matching and service recommendation;
- IP-driven creation in multimodal communities;
- hardware-driven subscription that creates a physical habit anchor.

Judge each by margin, frequency, distribution, and whether AI is essential or decorative.

### Consumer AI Winners Need Habit, Not Just Novelty

AI tourists produce misleading spikes. Durable products either:

- solve recurring high-value tasks;
- become an always-on assistant with memory;
- own entertainment/social identity loops;
- attach to physical hardware;
- create repeated campaigns/touch points;
- or sit inside a daily workflow already used by the user.

### Agent Value Is Workflow Ownership

Agent products are not just chatbots. The important shift is from "answering" to "doing":

- understand intent;
- choose tools;
- call APIs/databases/software;
- maintain context and memory;
- complete an end-to-end workflow;
- report progress and ask for help at bottlenecks.

The company that owns the agentic workflow can reroute traffic away from old SaaS interfaces.

### AI Capital Markets Reward Speed, But Speed Creates Fragility

AI markets can reward companies before full proof because the option value is large. But valuation can detach from revenue and margin. Analyze:

- Are growth and funding reinforcing real product learning, or only narrative?
- Is the company buying distribution without retention?
- Does revenue scale with gross margin, or with model-cost losses?
- Is the company still relevant after the next model release?

## Analysis Templates

### Model Launch

1. What task class improved?
2. Is the improvement benchmark-only or workflow-visible?
3. What is the cost/latency/reliability tradeoff?
4. Which users will switch, and why now?
5. Does it change distribution, pricing, or application margins?
6. What behavior data would prove adoption?

### AI Product

1. What recurring job does it own?
2. Is AI essential to the experience?
3. Who pays: consumer, prosumer, enterprise, advertiser, marketplace, or platform?
4. What is cost per useful outcome?
5. What data or workflow improves with usage?
6. What can a model provider or platform copy?

### AI Company Valuation

1. Is it a model company, app company, infrastructure company, or platform?
2. What is current revenue, ARR, margin, usage, and growth velocity?
3. What story is the market paying for?
4. Does capital improve product/distribution, or just extend burn?
5. Who captures value if the category succeeds?
6. What current data would falsify the valuation story?

### Benchmark or Ranking

1. Who designed the test and who benefits?
2. Can models privately test, tune, withdraw, or overfit?
3. Are closed/open models treated symmetrically?
4. Does the task represent real human workflows?
5. Do usage data and practitioner reports agree?
6. What alternative evaluation would be harder to game?

## Reverse Checklist

Be skeptical when the claim depends on:

- "best model" without task, price, latency, and workflow context;
- usage growth without retention, paid conversion, or inference cost;
- valuation without revenue quality or margin;
- consumer traffic without high-ARPU geography or monetization path;
- benchmark leadership without real-user switching;
- app wrappers without owned distribution, workflow, data, or model advantage;
- open-source enthusiasm without deployment cost, quality, and support reality;
- enterprise AI claims without integration, security, procurement, and measurable ROI.

## Answer Style

Use a compact, mechanism-led answer:

1. Lead with the conclusion and confidence.
2. Explain the mechanism chain.
3. Name the hard data and missing data.
4. Separate short-term narrative from long-term economics.
5. End with the next observable signal.

Avoid vague optimism. Prefer falsifiable claims and explicit conditions.
