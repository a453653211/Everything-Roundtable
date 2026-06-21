# Project Agent Rules

## Project-Local Skills

Project-only skills live under `.agents/skills/` and `.claude/skills/` and are scoped to this repository. Do not install, copy, or promote them to global agent skill directories unless the user explicitly asks.

- Use `.agents/skills/wangxiao-world-analysis` or `.claude/skills/wangxiao-world-analysis` only for this project when analyzing geopolitics, great-power competition, hot conflicts, industrial upgrading, macro policy, or world-order questions through the distilled Wang Xiao/Albert subtitle framework.
- Use `.agents/skills/taosha-doctor-thinking` and `.claude/skills/taosha-doctor-thinking` only for this project when analyzing China macro policy, global liquidity, A/H/US market moves, AI industry competition, commodities, technology supply chains, or geopolitical-market events through the distilled 淘沙博士 subtitle framework.
- Treat the skill as an analytical lens and source-route guide, not as a factual memory store.

## Personal Knowledge Library

`library/` is the user's personal knowledge library. It is not a default memory store for roundtable guests. A host or other caller decides whether any agent reads or writes it.

- Treat library operations as role-neutral capabilities. Do not define host, guest, researcher, or recorder responsibilities here.
- Use the `library-integrate` skill for selected sources or durable conclusions.
- Use the `library-maintain` skill for audits, consolidation, links, duplicates, and pending changes.
- Organize durable knowledge by domain and stable topic, never primarily by discussion session.
- Search and integrate before creating. Merge equivalent claims and avoid speculative folders, metadata, and notes.
- Do not save raw search result lists, unused results, full transcripts, or generic summaries.
- Domain pages hold current best knowledge. Conclusion records preserve the compact historical result and must link back to updated domain pages.
- Require human confirmation before reversing a core conclusion, changing confidence across levels, deleting supported content, resolving reliable-source conflicts, or deleting a library note.

## Obsidian CLI

Perform all `library/` reads, searches, creates, edits, moves, and link checks through Obsidian CLI with `vault=everything-roundtable`. Run `obsidian help <command>` when command syntax is uncertain.

Verify relevant writes with `read`, `links`, `backlinks`, `unresolved`, or `orphans`. Do not use permanent deletion.
