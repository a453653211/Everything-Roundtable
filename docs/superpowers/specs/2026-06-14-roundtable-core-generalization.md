# 圆桌内核通用化设计

## 1. 背景与第一性判断

项目原本按业务类别拆成两个圆桌 Skill（`roundtable-current-affairs`、`shanghai-real-estate-roundtable`），各自绑定固定话题与固定嘉宾。深入使用后发现：两者约 90% 的内容是**与话题无关的编排机制**——探讨求真而非辩论、席位即身份而非题域、子代理独立思考、统一事实底座、每轮挖一条最深裂缝、立场移动追踪、终局核查、倒金字塔呈现、无损存档。

按业务分类是错误切法：很多议题并不会分门别类得这么清晰，用户往往想要**更多视角**而非单一领域的封闭讨论。

正确切法（与 `library/` 的"能力解耦"哲学一脉相承）：

- **编排层（机制）** → 抽象为唯一通用主持内核 `.claude/skills/roundtable`，话题/材料/阵容全部作为运行时可配项。
- **嘉宾层（视角）** → 各 lens/up 主 Skill 是纯方法论世界观，**不知道自己在圆桌里**，由主持人运行时赋予角色。
- **工具层（能力）** → `library-integrate` / `library-maintain` 是角色中立能力，"材料收集者""会议纪要"是主持人赋予的角色，而非这些 Skill 自身的业务含义。

## 2. 已锁定的关键决策

| 决策 | 选择 |
|---|---|
| 旧两个 roundtable Skill | **一个通用 host 完全替代，删除旧两个**（不留领域预设） |
| 选角机制 | **纯动态**：主持人每场现扫可用 lens、现场提议阵容、用户拍板；无注册表、无预设 |
| 内核语言 | **中文**（与更成熟的 current-affairs 一致，圆桌话术表达最细腻） |
| 知识库默认程度 | **默认每场启用**材料收集者 + 会议纪要（走 `library-integrate`），最大化 AI 复利 |
| 本轮范围 | **只重构编排层**；lens Skill 与 library Skill 基本不动，仅必要规范化 |

## 3. 目标架构

> **位置约定**：Skill 以 `.claude/skills/` 为唯一维护源（Claude Code 项目级自动识别）。
> 供 Codex 使用时**手动镜像**到 `.codex/skills/`。因此 Skill 与规则文件内部**一律按名字引用兄弟 Skill**
> （或相对"本 skills 目录"），不硬编码 `.claude/` 路径，保证两份镜像都成立。

```text
.claude/skills/
  roundtable/                  ← 唯一通用主持内核（机制 + 选角协议 + 流水线，话题无关）
  geofinance-jiangzhiqishui/   ┐
  investing-chaonengmaomao/    │  嘉宾池：纯视角 lens，主持人运行时动态选角
  shanghai-real-estate-laoxie/ │  （本轮不改）
  shanghai-real-estate-liuwa/  │
  shanghai-renewal-310/        ┘
  library-integrate/           ┐  工具能力：主持人按需赋予"收集者/纪要"角色
  library-maintain/            ┘  （本轮不改）
```

- 圆桌不再按业务分类；主持人按**议题**动态提议阵容，**跨域同桌合法**（如姜汁汽水 + 老谢同桌）。
- 新增 up 主 = 往 `.claude/skills/` 丢一个 lens Skill 即可（并手动镜像到 `.codex/skills/`），主持内核无需改动。
- 知识库读写一律由主持人赋予的"库录入席"经 Obsidian CLI 完成；嘉宾席不直接触库（守住解耦，符合 `AGENTS.md`）。

## 4. 通用内核保留 / 吸收的要素

继承 `current-affairs` 的深度骨架；并入 `real-estate` 的优点：

- 继承：探讨非辩论、席位=身份、子代理独立思考、三层搜索、轮次循环（并行发言→主持综述[一条最深裂缝+ASCII 结构图+下一层问题]→指令菜单）、不指派立场红线、立场移动追踪、终局核查轮、倒金字塔呈现规范、无损存档、自检清单。
- 并入：证据硬度分级（hard/medium/soft）、决策对象/压力框定（把"buyer fit"泛化为"这件事真正要判断的对象是什么"）、collector/recorder 与讨论本身的职责分离。
- 修正（用户拍板）：**事实底座采集范围由嘉宾驱动**——事实席只建"中立骨架"（客观共识）+ 按各嘉宾申报的【数据需求】集中补采；主持人/事实席都不替嘉宾预判该看什么数据。明确区分"事实席（本场底座→存档）"与"库录入席（可复用精华→library/）"两类收集职能。

## 5. 变更清单

- 新增 `.claude/skills/roundtable/SKILL.md` 与 `.claude/skills/roundtable/agents/openai.yaml`。
- 删除旧 `roundtable-current-affairs/`、`shanghai-real-estate-roundtable/`（含其 `references/research-memory.md`；其"什么值得沉淀"的通用精华折叠进新内核的"沉淀知识库"小节，领域味去除）。
- 将整个 `skills/` 迁入 `.claude/skills/`（Claude Code 项目级自动识别），跨 skill 引用改为按名字/相对，供 `.codex/skills/` 手动镜像。
- 轻量更新 `CLAUDE.md`：标注 skill 位置约定，圆桌编排由 `roundtable` skill 承担。
- `AGENTS.md` 不变：库非默认共享、由 host/调用方决定、读写走 Obsidian CLI 的约束依然成立（host 默认启用，不违反）。

## 6. 暂不实现

不引入嘉宾注册表、领域预设、自动选角打分、嘉宾知识库同步、复杂脚本。新增 lens 靠主持人现扫描描述识别即可；待规模与反馈证明必要时再加。
