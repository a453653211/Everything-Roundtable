$ErrorActionPreference = 'Stop'

$requiredFiles = @(
    'AGENTS.md',
    'CLAUDE.md',
    '.claude/skills/library-integrate/SKILL.md',
    '.claude/skills/library-integrate/agents/openai.yaml',
    '.claude/skills/library-maintain/SKILL.md',
    '.claude/skills/library-maintain/agents/openai.yaml',
    'library/index.md'
)

$missing = @($requiredFiles | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($missing.Count -gt 0) {
    throw "Missing required files:`n$($missing -join "`n")"
}

$integrate = Get-Content -Raw -LiteralPath '.claude/skills/library-integrate/SKILL.md'
$maintain = Get-Content -Raw -LiteralPath '.claude/skills/library-maintain/SKILL.md'
$agents = Get-Content -Raw -LiteralPath 'AGENTS.md'

$checks = @(
    @{ Name = 'integration-first'; Text = $integrate; Pattern = 'integration-first' },
    @{ Name = 'source-or-conclusion'; Text = $integrate; Pattern = 'source.*conclusion' },
    @{ Name = 'role-neutral'; Text = $integrate; Pattern = 'role-neutral' },
    @{ Name = 'confirmation-gate'; Text = $integrate; Pattern = 'major-change' },
    @{ Name = 'obsidian-cli-integrate'; Text = $integrate; Pattern = 'obsidian' },
    @{ Name = 'maintenance-scope'; Text = $maintain; Pattern = 'orphans' },
    @{ Name = 'obsidian-cli-maintain'; Text = $maintain; Pattern = 'obsidian' },
    @{ Name = 'project-cli-rule'; Text = $agents; Pattern = 'Obsidian CLI' },
    @{ Name = 'personal-library-boundary'; Text = $agents; Pattern = 'personal knowledge library' }
)

$failed = @($checks | Where-Object { $_.Text -notmatch $_.Pattern } | ForEach-Object { $_.Name })
if ($failed.Count -gt 0) {
    throw "Content checks failed: $($failed -join ', ')"
}

$libraryFiles = @(Get-ChildItem -LiteralPath 'library' -Recurse -File -Filter '*.md')
$domainIndexes = @(Get-ChildItem -LiteralPath 'library' -Recurse -File -Filter 'index.md' | Where-Object {
    (Get-Content -Raw -LiteralPath $_.FullName) -match 'library-kind: domain-index'
})
if ($libraryFiles.Count -lt 10) {
    throw "Expected at least 10 library Markdown files, found $($libraryFiles.Count)."
}
if ($domainIndexes.Count -ne 3) {
    throw "Expected 3 domain index files, found $($domainIndexes.Count)."
}

Write-Output "Library acceptance checks passed: $($libraryFiles.Count) notes, $($checks.Count) content rules."
