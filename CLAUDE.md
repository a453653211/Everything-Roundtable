# Claude Code Entry

Read and follow [AGENTS.md](AGENTS.md). Skills live in `.claude/skills/` (canonical, maintained here; manually mirror to `.codex/skills/` for Codex). Knowledge-library procedures are provided by the `library-integrate` and `library-maintain` skills; roundtable orchestration lives in the `roundtable` skill and consumes those library skills as a capability rather than embedding them. Reference sibling skills by name, not by hardcoded path, so both mirrors resolve.
