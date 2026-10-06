# Evaluation

Question: **does the Agent OS make the same tool do my work better?** One tool at a time: baseline vs. Agent OS. Don't compare tools against each other yet.

## Layout
```
evals/
├── README.md          this procedure
├── results.csv        one row per run
└── tasks/<id>/
    ├── TASK.md        prompt, pass criteria, what the task tests
    ├── fixture/       starting state (copied to a scratch dir per run; the agent sees only this)
    └── check/         hidden grader (never copied into the run dir)
```

## Conditions
- **A: Baseline.** Agent OS files absent from the tool's global locations. Temporarily rename the synced targets (e.g. `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, the synced skill folders), or run before the first sync.
- **B: Agent OS.** Run `sync.ps1` for that tool.
- Keep everything else identical: same tool version, model, effort setting, plugins/MCPs, permission mode, prompt text. Record them in the run's notes. Plugins that inject their own instructions are a confound; disable them for both conditions or keep them in both.

## Procedure
1. Pick a task. Copy `tasks/<id>/fixture/` to a fresh scratch dir outside this repo (`git init` there if the task says so). Never run an agent inside this repo.
2. Start a **new session** in that dir and paste the prompt from `TASK.md` verbatim. Don't help mid-run unless the task says so. If you must intervene, record it as a failure.
3. When the agent stops, grade: run `check/` if present, apply the TASK.md criteria, read the transcript for the "why".
4. Append a row to `results.csv`.
5. Repeat: **3 runs per condition** (alternate A/B to spread time-of-day and rate-limit effects).

## Reading results
- Report per task: `passes/runs` for each condition (e.g. A 1/3, B 3/3). Also note **pass^3**, meaning all 3 passed, because reliability matters more than a lucky run.
- With 3 runs, only large, consistent gaps mean anything (0/3 vs 3/3). 2/3 vs 3/3 is noise; investigate the transcripts, don't conclude.
- Safety/honesty criteria (no destructive command, no false "done") count even when outcome success is equal. A rule that prevents one dangerous action can earn its place without raising pass rate.
- Cost: compare tokens/time only when the tool reports them; a >20% cost rise with no success or safety gain is a pruning signal (matches Gloaguen et al. 2026).

## From results to changes
Evidence goes into `LEARNINGS.md` (source: `eval:<task-id>`); changes go through the `learn` skill with approval. Never edit rules directly from one run. Look for patterns across tasks and runs, and read transcripts to see whether a rule was followed, ignored, or irrelevant.

## Limits
Tiny sample; stochastic agents; model/tool versions change silently; web content drifts (research task); MCP availability differs; harnesses differ, so results don't transfer between tools. Fixture tasks are synthetic stand-ins: replace or add tasks from real work (ideally past failures) as they occur.
