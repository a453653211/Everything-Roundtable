---
name: library-integrate
description: Use when a person, agent, or workflow provides a selected research source or a durable conclusion that may belong in the project's personal Obsidian knowledge library.
---

# Library Integrate

## Principle

Maintain the user's personal knowledge library as a role-neutral capability. Use **integration-first** editing: search, reuse, merge, and compress before creating files. Do not define roundtable roles or scheduling.

## Input

Accept `input_type: source | conclusion` plus:

- domain and topic;
- content or claims;
- date;
- source URL/citation when applicable;
- confidence and open questions when known.

Ask only for information required to avoid a misleading record. Reject raw search dumps, transcripts, and unsupported filler.

## Workflow

1. Run `obsidian vault=everything-roundtable search` and `read` to find equivalent sources, aliases, and the narrowest existing knowledge page.
2. Decide whether the input is reusable:
   - `source`: keep only evidence that supports/challenges an important claim, provides reusable data or verification, or is likely to be cited again.
   - `conclusion`: keep only a durable judgment, mechanism, decision rule, disagreement, or falsifiable open question.
3. Prefer updating one existing page. Create a page only when no current page can hold the content without mixing distinct topics.
4. For a source, create at most one source note per substantive source. Reuse the note on later citations.
5. For a conclusion, create one short conclusion record and integrate reusable claims into domain pages. Do not save the transcript.
6. Link source/conclusion notes to affected knowledge pages and update the nearest index only when navigation changes.
7. Use only Obsidian CLI commands for `library/` reads and mutations. Run `obsidian help <command>` when syntax is uncertain.
8. Verify changed notes with `read`, `links`, and `unresolved` as needed.

## Major-Change Gate

Treat these as **major-change** operations: reversing a core conclusion, changing confidence across levels, deleting still-supported content, or resolving conflict between reliable sources.

Do not overwrite the knowledge page. Append a compact proposal to `library/维护/待确认重大变更.md` containing current claim, proposed claim, evidence, affected pages, and recommended action. Continue only after explicit human approval.

## Minimal Writing

- Merge equivalent claims; do not append another version.
- Preserve only evidence, conditions, uncertainty, links, and actionable open questions.
- Do not create empty category pages, speculative metadata, or per-discussion topic folders.
- Rewrite stale prose when a shorter current synthesis preserves meaning.

## Result

Return only:

```yaml
status: integrated | pending_confirmation | skipped
created: []
updated: []
linked: []
skipped: []
confirmation_required: []
warnings: []
```
