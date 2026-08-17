# Analysis Protocol

Analyze only after a release is classified as new or revised.

For Shanghai municipal data or planning events, also read `shanghai-monitoring.md`.

## Order

1. **Fact**: State the official value, unit, period, basis, and publication date.
2. **Change**: Compare with the immediately comparable prior record. Distinguish month-on-month, year-on-year, cumulative, annualized, nominal, real, seasonally adjusted, and unadjusted values.
3. **Revision**: State any changed historical value before interpreting the current value.
4. **Structure**: Identify which official components explain the headline. Do not infer missing components.
5. **Behavior**: Translate a group of related indicators into a concrete choice people or firms appear to be making, such as postponing durable purchases, protecting essentials, switching price bands, reducing leverage, or increasing precautionary saving.
6. **Affected group**: Infer which balance sheet or income group is most exposed only when at least one additional official indicator supports it. Label this as inference, not fact.
7. **Implication**: Give only the shortest defensible mechanism, explicitly labeled as inference.
8. **Alternative**: Name the strongest competing explanation, such as price effects, subsidies, replacement cycles, base effects, supply constraints, or statistical reclassification.
9. **Verification**: Name the next official indicator that would strengthen or falsify the behavioral reading.
10. **Caveat**: Record base effects, methodology changes, absent denominators, non-comparable series, or missing official detail.

For an official event, replace the statistical change sequence with:

1. event and jurisdiction;
2. administrative stage;
3. spatial scope;
4. exact official change;
5. what the document does not yet authorize or fund;
6. next official checkpoint.

## Plain-Language Translation

Use this causal ladder:

```text
official data combination
  -> observed spending/production/financing choice
  -> likely household or business constraint
  -> potentially affected group
  -> broader consequence
  -> next official check
```

Prefer contrasts that expose choices:

- essentials versus discretionary consumption;
- services versus goods;
- small frequent purchases versus durable big-ticket purchases;
- volume versus price;
- current consumption versus saving or debt repayment;
- total growth versus the contribution of major components;
- aggregate stability versus distributional divergence.

Write the intuitive interpretation as: “The combination is more consistent with X than Y because A and B moved differently.” Avoid slogans such as “consumption downgrade” unless the registered official data show the relevant substitution or retrenchment pattern.

Inferring an affected social group requires corroboration. Useful official cross-checks include employment and wages, household loans and deposits, income bands where published, housing transactions, durable-goods purchases, and sector employment. If those data are absent, write “possible affected group” and lower confidence.

## Compact Output

Use this shape inside the record:

```text
headline: one sentence
changes: 1-3 factual bullets
behavioral_readout: one plain-language paragraph
affected_groups: 0-2 explicitly labeled inferences
implications: 0-2 bounded inference bullets
alternative_explanations: 1-3 bullets
verification_needed: 1-3 named official indicators
caveats: 0-3 bullets
confidence: high | medium | low
```

Use `high` only when the official source, metric definition, comparison basis, and prior-period comparison are all clear. Use `medium` when the data are official but interpretation is constrained by revisions, missing detail, or comparability. Use `low` only to preserve a verified official datum whose analytical meaning remains materially uncertain.

## Cross-Release Synthesis

After all commits, synthesize only `new` and `revision` items. Do not repeat every card. Add a decision layer that helps the reader choose what to investigate.

Use this order:

1. **Overall judgment**: one sentence naming the strongest combined signal or saying that the releases are mostly routine.
2. **Group**: use only scopes that improve understanding, normally `上海`, `全国`, or `全球`; keep 1-3 groups.
3. **Importance**: classify independently from implementation stage:
   - `routine`: scheduled release or procedural step with no material new directional or execution evidence;
   - `low`: narrow, early, weakly corroborated, or unlikely to change a current view;
   - `medium`: material enough to watch, but still single-domain, early-stage, or awaiting confirmation;
   - `high`: historically unusual, broad and corroborated, or late-stage evidence that materially changes the current view.
4. **Stage**:
   - statistics: observed result, while causal interpretation may remain unverified;
   - policy/project: meeting or mention -> research/catalogue -> draft consultation -> approved -> budgeted/procured -> executing/under construction -> completed/operating;
   - state the strongest stage directly evidenced, not the stage that seems likely next.
5. **Judgment**: explain the shortest combined meaning. Separate what has happened from what might follow.
6. **Next verification**: name the next official datum or process milestone that would strengthen, weaken, or close the judgment.
7. **Deep-dive candidates**: select at most three only when the likely information gain is high.

Do not infer importance from item count. Do not average unrelated indicators into a false common story. A strategically important draft can have high long-run relevance but low implementation maturity; report both dimensions separately.

Use this compact run-level shape:

```text
headline: one overall sentence
sections: 1-3 grouped judgments
  scope
  dataset_ids
  significance: high | medium | low | routine
  stage
  judgment
  watch_next
deep_dive_candidates: 0-3
confidence: high | medium | low
```

## Prohibitions

- Do not replace missing official detail with media summaries.
- Do not equate an index level with a growth rate.
- Do not mix release month with reference month.
- Do not mix stock and flow, current-period and cumulative values, or preliminary and final estimates.
- Do not call a one-period move a trend without comparable history.
- Do not claim causality from co-movement alone.
- Do not infer a social class or income group from one consumption category.
- Do not use a vivid behavioral story when price, policy, supply, or base effects explain the same pattern equally well.
- Do not provide investment advice.
- Do not treat a plan, budget, approval, construction notice, or completion as interchangeable stages.
- Do not turn several unrelated releases into one narrative merely to make the daily report sound coherent.
