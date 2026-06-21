---
name: library-maintain
description: Use when the project's personal Obsidian knowledge library needs a health check, consolidation pass, link audit, duplicate review, or pending-change review.
---

# Library Maintain

## Principle

Keep the library small, connected, and current. Audit it as a role-neutral capability; do not define who requested maintenance or how a roundtable is orchestrated.

## Workflow

1. Use `obsidian vault=everything-roundtable files folder=library`, `search`, `orphans`, `deadends`, `unresolved`, `links`, and `backlinks` to inspect the vault. Run `obsidian help <command>` when needed.
2. Review only actionable issues:
   - duplicate or near-duplicate knowledge/source pages;
   - fragmented claims that belong on one stable topic page;
   - orphan notes that should be linked, merged, or removed;
   - unresolved or misleading links;
   - stale claims contradicted by newer reliable evidence;
   - completed or blocked entries in the pending-change list.
3. Fix ordinary links, indexes, wording duplication, and safe merges through Obsidian CLI.
4. For deletion, core-claim reversal, confidence-level change, or reliable-source conflict, add a **major-change** proposal to `library/维护/待确认重大变更.md` instead of applying it.
5. Update `library/维护/健康检查.md` with the date, commands run, issues fixed, proposals created, and remaining gaps. Keep only the latest compact report unless history is materially useful.
6. Re-run the relevant CLI checks and report the evidence.

## Restraint

- Do not create pages merely to eliminate an orphan count.
- Prefer merging and rewriting over adding cross-links everywhere.
- Do not introduce new folders, metadata, plugins, scripts, or taxonomies without demonstrated retrieval pain.
- Do not duplicate `library-integrate`; maintenance starts from the existing library, not new source/conclusion input.

## Result

Return only:

```yaml
status: maintained | pending_confirmation | no_action
fixed: []
merged: []
confirmation_required: []
remaining: []
verification: []
```
