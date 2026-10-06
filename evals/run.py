"""Run eval tasks headlessly with Claude Code: baseline (A) vs Agent OS (B).

  python evals/run.py vague-idea what-next          # both conditions, 1 run each
  python evals/run.py --all --runs 3                # every task, 3 runs per condition
  python evals/run.py what-next --conditions B      # one condition

Each run gets a fresh scratch dir outside the repo. Condition B places AGENTS.md as .claude/CLAUDE.md and the
skills in .claude/skills inside that scratch dir only (git-excluded), so global tool config is never touched.
Transcripts land in evals/runs/ (git-ignored); one row per run is appended to results.csv with
pass="?" unless a hidden grader decides it. Grade the rest by reading the transcript against TASK.md.
"""
import argparse
import csv
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = ROOT / "evals" / "tasks"
RUNS = ROOT / "evals" / "runs"
RESULTS = ROOT / "evals" / "results.csv"
CLAUDE = shutil.which("claude") or "claude"
BASH = shutil.which("bash") or r"C:\Program Files\Git\bin\bash.exe"

ALLOWED_TOOLS = [
    "Read", "Glob", "Grep", "Edit", "Write", "Skill", "WebSearch", "WebFetch",
    "Bash(python:*)", "Bash(pytest:*)", "Bash(git:*)", "Bash(ls:*)", "Bash(cat:*)",
]


def section(text, heading):
    m = re.search(rf"^## {heading}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def prompt_of(task_md):
    lines = [l[2:] for l in section(task_md, "Prompt").splitlines() if l.startswith("> ")]
    if not lines:
        sys.exit("no '> ' prompt lines under ## Prompt")
    return "\n".join(lines)


def setup_script(task_md):
    m = re.search(r"```bash\n(.*?)```", section(task_md, "Setup"), re.S)
    return m.group(1) if m else None


def prepare(task, condition, work):
    task_md = (TASKS / task / "TASK.md").read_text(encoding="utf-8")
    fixture = TASKS / task / "fixture"
    if fixture.is_dir():
        shutil.copytree(fixture, work, dirs_exist_ok=True)
    script = setup_script(task_md)
    if script:
        subprocess.run([BASH, "-c", script], cwd=work, check=True)
    if condition == "B":
        # .claude/CLAUDE.md is also read as project memory and keeps the repo's own root CLAUDE.md free
        shutil.copytree(ROOT / "skills", work / ".claude" / "skills")
        shutil.copy(ROOT / "AGENTS.md", work / ".claude" / "CLAUDE.md")
        exclude = work / ".git" / "info" / "exclude"
        if exclude.parent.is_dir():
            with exclude.open("a") as f:
                f.write("\n.claude/\n")
    return prompt_of(task_md)


def run_agent(prompt, work, model):
    cmd = [CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--no-session-persistence",
           "--allowedTools", *ALLOWED_TOOLS]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, cwd=work, capture_output=True, text=True, encoding="utf-8",
                          timeout=1800)
    events = []
    for line in proc.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return events, proc.stderr


def grade(task, work):
    check = TASKS / task / "check" / "check.py"
    if not check.exists():
        return "?", ""
    r = subprocess.run([sys.executable, str(check), str(work)], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    return ("1" if r.returncode == 0 else "0"), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tasks", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--conditions", default="AB")
    ap.add_argument("--model", default="")
    ap.add_argument("--prepare", action="store_true",
                    help="only create scratch dirs and print them as JSON (for in-app subagent runs)")
    args = ap.parse_args()
    tasks = sorted(p.name for p in TASKS.iterdir() if p.is_dir()) if args.all else args.tasks
    if not tasks:
        ap.error("name tasks or pass --all")

    version = "" if args.prepare else subprocess.run([CLAUDE, "--version"], capture_output=True, text=True).stdout.strip()
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for task in tasks:
        for run in range(1, args.runs + 1):
            for cond in args.conditions:  # alternate A/B within each run
                work = Path(tempfile.mkdtemp(prefix=f"agent-os-eval-{task}-{cond}{run}-"))
                prompt = prepare(task, cond, work)
                if args.prepare:
                    print(json.dumps({"task": task, "condition": cond, "run": run, "dir": str(work), "prompt": prompt}))
                    continue
                print(f"[{task} {cond}{run}] {work}", flush=True)
                events, stderr = run_agent(prompt, work, args.model)
                passed, check_out = grade(task, work)

                log = RUNS / stamp / f"{task}-{cond}{run}"
                log.mkdir(parents=True, exist_ok=True)
                (log / "transcript.jsonl").write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
                final = next((e for e in reversed(events) if e.get("type") == "result"), {})
                (log / "final.md").write_text(final.get("result", f"(no result)\n{stderr}"), encoding="utf-8")
                if check_out:
                    (log / "check.txt").write_text(check_out, encoding="utf-8")

                usage = final.get("usage", {})
                tokens = sum(usage.get(k, 0) for k in ("input_tokens", "output_tokens",
                                                       "cache_creation_input_tokens", "cache_read_input_tokens"))
                tool_calls = sum(1 for e in events if e.get("type") == "assistant"
                                 for c in e.get("message", {}).get("content", []) if c.get("type") == "tool_use")
                model = next((e.get("model") for e in events if e.get("type") == "system"), args.model)
                with RESULTS.open("a", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow([
                        dt.date.today().isoformat(), task, "claude-code", f"{version} / {model}", cond, run,
                        passed, "", "", tool_calls, tokens, round(final.get("duration_ms", 0) / 60000, 1),
                        f"cost_usd={final.get('total_cost_usd', '?')}; denials={len(final.get('permission_denials', []))}; log={log.relative_to(ROOT)}",
                    ])
                print(f"   pass={passed} tools={tool_calls} tokens={tokens} cost={final.get('total_cost_usd')}", flush=True)


if __name__ == "__main__":
    main()
