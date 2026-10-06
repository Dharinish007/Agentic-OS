<#
Projects the Personal Agent OS (this folder) into each agent tool's native locations.
One-way: this folder is the source of truth. Edits made at a destination are never pulled back.

  .\sync.ps1                 # all tools
  .\sync.ps1 -Tool codex     # one tool: claude | codex | gemini | cursor
  .\sync.ps1 -DryRun         # show what would happen, change nothing
  .\sync.ps1 -Force          # replace conflicting files (original saved as <file>.agent-os-backup)

Safety: a destination file is overwritten only if it is missing, or it still matches exactly what this
script last wrote (hash recorded in .sync-state.json). Anything else is reported as CONFLICT and left alone.
Never touches MCP config, credentials, settings, or files it didn't create. Never deletes.
#>
param(
    [ValidateSet('all', 'claude', 'codex', 'gemini', 'cursor')][string]$Tool = 'all',
    [switch]$DryRun,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$StatePath = Join-Path $Root '.sync-state.json'
$Rules = Join-Path $Root 'AGENTS.md'
$Skills = Join-Path $Root 'skills'

# Personal overlay: personal/*.md (git-ignored) is appended after the public rules.
$Personal = @(Get-ChildItem -Path (Join-Path $Root 'personal') -Filter '*.md' -File -ErrorAction SilentlyContinue | Sort-Object Name)
if ($Personal.Count -gt 0) {
    $Built = Join-Path $Root '.build\rules.md'
    $parts = @((Get-Content -LiteralPath $Rules -Raw).TrimEnd())
    $parts += $Personal | ForEach-Object { (Get-Content -LiteralPath $_.FullName -Raw).TrimEnd() }
    # Built inside this repo (git-ignored) even on -DryRun, so the dry run compares real content.
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Built) | Out-Null
    Set-Content -LiteralPath $Built -Value (($parts -join "`n`n---`n`n") + "`n") -Encoding UTF8 -NoNewline
    $Rules = $Built
    Write-Host "Personal overlay: $($Personal.Name -join ', ')"
}

$state = @{}
if (Test-Path -LiteralPath $StatePath) {
    (Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value }
}
$counts = @{ written = 0; unchanged = 0; conflict = 0; failed = 0 }

function Get-Hash($path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash }

function Sync-File($src, $dst) {
    $srcHash = Get-Hash $src
    $exists = Test-Path -LiteralPath $dst
    $managed = $false
    if ($exists) {
        $dstHash = Get-Hash $dst
        if ($dstHash -eq $srcHash) {
            $state[$dst] = $srcHash
            Write-Host "  [=] $dst"
            $counts.unchanged++
            return
        }
        $managed = $state.ContainsKey($dst) -and $state[$dst] -eq $dstHash
        if (-not $managed -and -not $Force) {
            Write-Host "  [!] CONFLICT $dst - existing content was not written by agent-os or was edited since. Not overwritten." -ForegroundColor Yellow
            $counts.conflict++
            return
        }
    }
    if ($DryRun) {
        $why = if (-not $exists) { 'create' } elseif ($managed) { 'update' } else { 'replace (Force, with backup)' }
        Write-Host "  [~] would $why $dst"
        return
    }
    try {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
        if ($exists -and -not $managed) {
            Copy-Item -LiteralPath $dst -Destination "$dst.agent-os-backup" -Force
            Write-Host "  [b] backup $dst.agent-os-backup"
        }
        Copy-Item -LiteralPath $src -Destination $dst -Force
        if ((Get-Hash $dst) -ne $srcHash) { throw 'content mismatch after copy' }
        $state[$dst] = $srcHash
        Write-Host "  [+] $dst" -ForegroundColor Green
        $counts.written++
    }
    catch {
        Write-Host "  [x] FAILED $dst - $_" -ForegroundColor Red
        $counts.failed++
    }
}

function Sync-Skills($destRoot) {
    Get-ChildItem -LiteralPath $Skills -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Skills.Length).TrimStart('\', '/')
        Sync-File $_.FullName (Join-Path $destRoot $rel)
    }
}

$targets = [ordered]@{
    claude = @{ Name = 'Claude Code'; Dir = 'claude-code'; Rules = "$HOME\.claude\CLAUDE.md"; Skills = "$HOME\.claude\skills" }
    codex  = @{ Name = 'Codex'; Rules = "$HOME\.codex\AGENTS.md"; Skills = "$HOME\.agents\skills" }
    gemini = @{ Name = 'Gemini CLI'; Rules = "$HOME\.gemini\GEMINI.md"; Skills = "$HOME\.agents\skills" }
    cursor = @{ Name = 'Cursor'; Rules = $null; Skills = "$HOME\.agents\skills" }
}

Write-Host "Source: $Root$(if ($DryRun) { '  (dry run - nothing will change)' })"
foreach ($key in $targets.Keys) {
    if ($Tool -ne 'all' -and $Tool -ne $key) { continue }
    $t = $targets[$key]
    $notes = "adapters\$(if ($t.Dir) { $t.Dir } else { $key })\README.md"
    Write-Host "`n[$($t.Name)]"
    if ($t.Rules) { Sync-File $Rules $t.Rules }
    else { Write-Host "  [!] global rules: no file-based location - paste AGENTS.md manually (see $notes)" -ForegroundColor Yellow }
    Sync-Skills $t.Skills
    Write-Host "  [!] MCP config, auth, permissions unchanged - see $notes"
}

if (-not $DryRun) {
    $state | ConvertTo-Json | Set-Content -LiteralPath $StatePath -Encoding UTF8
}
Write-Host "`nwritten: $($counts.written)  unchanged: $($counts.unchanged)  conflicts: $($counts.conflict)  failed: $($counts.failed)"
if ($counts.failed -gt 0) { exit 1 }
