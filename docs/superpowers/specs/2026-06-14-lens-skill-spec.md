# Lens（嘉宾方法论）Skill 轻量规范

## 目的

让任意分析方法论以"可被圆桌 host 动态选角、可被子代理独立加载"的统一契约存在。
**lens 只描述"我如何分析世界"，不知道自己在圆桌里**——圆桌角色由 host 每场赋予（见 `skills/roundtable`）。

## 必须（4 条硬契约）

1. **角色中立 / 立场不预设**：纯世界观。不假设自己在圆桌、不预设结论或立场；可被加载后"按事实自行推导"。
   不写"作为圆桌嘉宾……"之类的角色台词。
2. **`description` 适配选角**：frontmatter `description` 一段话说清——(a) 是什么方法论/世界观；
   (b) `Use when …` 列出能撬动的典型问题/领域（供 host 判相关性）；(c) 收尾免责"仅为分析框架，非投资/决策建议"。
   `name` 必须 = 目录名。
3. **暴露可加载锚点**：正文显式给出该方法论的 **公理/第一性模型 + 核心方法/框架 + 应用检查清单** 三类锚点
   （小标题措辞可不同，但这三类要在）。host 子代理会要求"按其公理/框架/清单思考"，锚点缺失会让加载落空。
4. **不耦合**：lens 不读写 `library/`、不调用 host、不依赖其它 lens 才能工作（可"建议改用某 lens"，但不强依赖）。

## 建议（一致性，非强制）

- 配 `应用检查清单`（逐条自问）与 `数据使用/常用数据源`（带出处口径）。
- 事实纪律：关键数据带来源、区分硬/中/软证据、推演与事实分离——与 host 的事实底座口径对齐。
- 语言：优先**中文**（与 host 一致）。存量英文正文为**非阻塞债**，可后续统一。
- 风格：保留"推理习惯"，不模仿 up 主的表演/玩梗。

## 可选

- `agents/openai.yaml`：要可被**单独直接调用**就加（见模板），统一带 `policy.allow_implicit_invocation: true`。
  不加也不影响 host——host 直接读 `SKILL.md` 调度。
- `references/*.md`：更深的经验/案例沉淀，host 子代理可按需加载。

## 目录结构

```
<lens-name>/
  SKILL.md            # 必须
  agents/openai.yaml  # 可选（要直接调用就加）
  references/*.md      # 可选（深度经验）
```

## SKILL.md 骨架模板

```markdown
---
name: <lens-name>
description: >-
  <一句话：是什么方法论/世界观>。Use when <典型问题/领域，逗号分隔>。
  核心是"<2–4 个招式关键词>"。仅为分析框架，非投资/决策建议。
---

# <显示名> · <方法论副标题>

<一句话操作总纲：分析顺序 / 总原则>

## 一、公理（地基）
1. …
2. …

## 二、核心方法（按使用顺序）
### 1. …
### 2. …

## 三、数据使用 / 常用数据源（带出处口径）
…

## 四、一次分析的展开骨架
1. … 2. … 3. …

## 五、应用检查清单（逐条自问）
- [ ] …
- [ ] …

> 免责：本 skill 是可复用的分析思维框架，不构成投资/决策建议。
```

## agents/openai.yaml 模板

```yaml
interface:
  display_name: "<显示名>"
  short_description: "<一句话定位>"
  default_prompt: "Use $<lens-name> to <一句话用途>."
policy:
  allow_implicit_invocation: true
```

## 与圆桌（host）的关系

- host 动态选角扫各 lens 的 `description`，**排除** `library-*`（能力型）与 host 自身，其余即候选。
- host 子代理加载 lens 的 `SKILL.md`，要求"按其公理/框架/清单思考"——故契约 3 必须满足。
- lens 不承担圆桌角色；"嘉宾席 / 材料收集者 / 会议纪要"等角色由 host 在每场赋予。

## 现状与债务（截至本次）

| lens | 语言 | 锚点齐全 | yaml | 本次动作 |
|---|---|---|---|---|
| geofinance-jiangzhiqishui | 中文 | ✔（公理/方法/清单） | 缺 | 补 yaml |
| investing-chaonengmaomao | 中文 | ✔（公理/方法/清单） | 缺 | 补 yaml |
| shanghai-real-estate-laoxie | 英文 | ✔（Model/Workflow/Output/Guardrails 等价） | 有 | 不动；语言列为非阻塞债 |
| shanghai-real-estate-liuwa | 英文 | ✔（同上） | 有（缺 policy 块） | 补 policy 块；语言列为非阻塞债 |
| shanghai-renewal-310 | 英文 | ✔（同上） | 有 | 不动；语言列为非阻塞债 |

> 非阻塞债：3 个上海系 lens 的英文正文与中文两个不统一，但结构锚点齐全、不影响 host 调度；
> 是否统一中文化留待后续单独决策（重活、耗 token）。
