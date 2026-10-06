# Power with Guardrails

Goal: an agent that uses its tool's **full** capability and works with real autonomy, yet cannot hurt you by accident. Power and safety are not opposites: guardrails are what let you grant more autonomy.

## Where power comes from
| Source | What it gives |
|---|---|
| 🧠 Thinking | Understands the real goal, asks only questions that change the outcome, chooses the next best step |
| 🛠️ Skills | Expert procedures loaded only when needed (low token cost) |
| 🔌 MCP & tools | Acting on real systems: browser, GitHub, databases, docs |
| 🤖 Subagents & parallelism | Larger tasks split into focused workers |
| ⏰ Automation | Scheduled and looping tasks that run unattended |
| 🧪 Evals | Only rules proven to help survive, which keeps context lean |

## Three levels of control
| Level | Mechanism | Strength |
|---|---|---|
| 1. Advice | `AGENTS.md`, skills | Followed most of the time, **not guaranteed** |
| 2. Permissions | Each tool's allow/ask/deny settings | Enforced by the tool |
| 3. Hooks | Scripts that run before/after tool calls and can block them | Enforced, programmable |

Rules alone are advice. Anything that must **never** happen belongs in level 2 or 3.

## Always guarded (regardless of autonomy)
- Deleting data, `rm -rf`, dropping databases
- Force-push, history rewrites, pushing to protected branches
- Writing secrets into files, commits, logs, or URLs
- Touching production, sending messages, publishing, spending money
- Following instructions found inside web pages, files, or tool output

## Autonomy presets
| Preset | Behavior |
|---|---|
| 🛡️ Careful | Asks before any write or command |
| ⚖️ Balanced (default) | Edits and runs safe commands freely; asks for guarded actions |
| 🚀 Full | Works end to end unattended; guarded actions still blocked by hooks |

Apply with `python adapters/claude-code/apply-preset.py <careful|balanced|full|off>` (Claude Code).

## Claude Code power pack (built)
- 🪝 Guard hook: deny / ask decisions before Bash, PowerShell, Write, Edit (see `adapters/claude-code/README.md`)
- 🤖 Subagents: `reviewer` (read-only), `researcher` (cited)
- ⌨️ Commands: `/agent-os:idea`, `/agent-os:next`, `/agent-os:verify`, `/agent-os:review`

Other tools get their power packs in order: Antigravity, Codex, Cursor, OpenCode.
