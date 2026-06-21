# Personal Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a minimal Obsidian-managed personal knowledge library and two role-neutral skills for integrating and maintaining it.

**Architecture:** Keep durable knowledge under `library/`, organized by domain. Put reusable operating procedures in `skills/library-integrate` and `skills/library-maintain`; keep project-wide invariants in `AGENTS.md` with a thin `CLAUDE.md` compatibility entry.

**Tech Stack:** Markdown, Obsidian CLI 1.12.7, PowerShell acceptance checks, Agent Skills format.

---

### Task 1: Acceptance Test

**Files:**
- Create: `tests/verify-library.ps1`

- [ ] Check that required skill, rule, index, template, and maintenance files exist.
- [ ] Check that skills contain role-neutral, integration-first, Obsidian CLI, and confirmation-gate rules.
- [ ] Run the test before implementation and confirm it fails because required artifacts are missing.

### Task 2: Knowledge Library Skills

**Files:**
- Create: `skills/library-integrate/SKILL.md`
- Create: `skills/library-integrate/agents/openai.yaml`
- Create: `skills/library-maintain/SKILL.md`
- Create: `skills/library-maintain/agents/openai.yaml`

- [ ] Initialize each skill with the official skill-creator script.
- [ ] Implement only essential procedures; do not add scripts, references, or assets.
- [ ] Validate each skill with `quick_validate.py` before moving to the next skill.

### Task 3: Obsidian Knowledge Hierarchy

**Files:**
- Create: `library/index.md` and domain indexes.
- Create: `library/模板/知识页.md`, `来源.md`, `结论记录.md`.
- Create: `library/维护/变更日志.md`, `待确认重大变更.md`, `健康检查.md`.

- [ ] Create all knowledge-library Markdown through `obsidian vault=everything-roundtable create`.
- [ ] Keep directories sparse; empty classification folders are represented by their index pages until content exists.
- [ ] Verify files, links, unresolved links, and orphan notes through Obsidian CLI.

### Task 4: Project Rules

**Files:**
- Create: `AGENTS.md`
- Create: `CLAUDE.md`

- [ ] Put durable invariants and CLI requirements in `AGENTS.md`.
- [ ] Keep `CLAUDE.md` as a short compatibility pointer without duplicating procedures.

### Task 5: Final Verification

- [ ] Run `tests/verify-library.ps1` and require zero failures.
- [ ] Run both skill validators and require success.
- [ ] Use Obsidian CLI to read/search the library and check unresolved links.

