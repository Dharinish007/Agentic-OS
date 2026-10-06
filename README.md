# Agent OS

**Write your agent standards once. Run them in every AI coding tool. Prove they work.**

Agent OS is a portable, evidence-backed operating layer for AI coding agents: universal rules, on-demand skills, a tool registry, a safe sync installer, and an eval harness that measures whether any of it helps.

## Mission
Make any AI agent work at its full potential: it thinks before it acts, understands who the work is for, verifies before it says "done", and never takes a dangerous action silently.

## Vision
One open standard that makes a single agent, or a fleet of them, behave like a senior engineering partner, where every rule earns its place through evidence rather than vibes.

## Philosophy
- 🧠 **Think, then act.** Understand the real goal, ask only questions that change the outcome, pick the next best step, explain briefly.
- ⚡ **Power with guardrails.** Maximum capability and autonomy, with hard limits on destructive, irreversible, and secret-touching actions. See [docs/POWER.md](docs/POWER.md).
- 🧪 **Evidence over vibes.** Rules are tested with evals (baseline vs. Agent OS). Rules that don't help get cut.
- 🪶 **Lean context.** Rules stay short; skills load only when a task needs them.
- 🔁 **Learns under your control.** Agents record lessons; only you promote them into rules.

## What's inside
| Path | Purpose |
|---|---|
| `AGENTS.md` | Universal rules, synced as each tool's global rules file |
| `skills/` | Procedures in the Agent Skills format (`SKILL.md`), loaded on demand |
| `adapters/` | Tool-specific notes: where each tool reads rules, skills, MCP config |
| `mcp/registry.md` | Catalog of MCP servers: purpose, risks, auth method (never secrets) |
| `evals/` | A/B evaluation tasks, results, and the generated [SCORECARD.md](evals/SCORECARD.md) |
| `LEARNINGS.md` | Lesson inbox; promoted only through the `learn` skill |
| `sync.ps1` | One-way installer into each tool's native locations |
| `personal/` | *Git-ignored.* Your private rules (`*.md`), appended after `AGENTS.md` on sync |

## Supported tools
| Tool | Rules | Skills | Power pack |
|---|---|---|---|
| Claude Code | ✅ | ✅ | ✅ plugin: guard hook, subagents, commands, autonomy presets |
| Antigravity | ✅ | ✅ | ✅ guard hook |
| Codex | ✅ | ✅ | planned |
| Gemini CLI | ✅ | ✅ | – |
| Cursor | manual paste | ✅ | planned |
| OpenCode | planned | planned | planned |

## Quick start (Windows / PowerShell)
```powershell
git clone https://github.com/Dharinish007/Agentic-OS.git
cd Agentic-OS
.\sync.ps1 -DryRun          # preview
.\sync.ps1                  # all tools
.\sync.ps1 -Tool claude     # one tool: claude | antigravity | codex | gemini | cursor
```
Sync never deletes, never touches MCP config or credentials, and never overwrites a file you edited (it reports a conflict instead; `-Force` keeps a backup).

## Personalize
Put private rules in `personal/*.md`. They are appended after the public rules on your machine and never committed.

## Evidence
Every skill has a status in [evals/SCORECARD.md](evals/SCORECARD.md): ✅ proven · 🟡 promising · ➖ neutral · ⚠️ regressed · ⬜ untested. Regenerate with `python evals/scorecard.py`.

## Status
Early. Built: core rules, 16 skills (incl. thinking layer and `init-project`), Claude Code power pack (guard hook, subagents, commands, autonomy presets), Antigravity power pack (guard hook), eval runner + scorecard. Next: wider eval coverage → more tool power packs (Codex, Cursor, OpenCode) → memory → publishing.
