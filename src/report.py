"""
Scans results/*.json and generates:
  - results/README.md          (leaderboard: model x eval x attack success rate)
  - results/leaderboard.json   (single aggregated file the public site fetches)
  - results/<run>.md           (full transparent transcript: every prompt/response/score)

Run this after run_eval.py, before committing to GitHub.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from result_paths import is_valid_result

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def _fenced_text(value: str) -> str:
    """Render arbitrary model text literally without Markdown reformatting it."""
    value = str(value)
    longest_tick_run = max((len(match.group()) for match in re.finditer(r"`+", value)), default=0)
    fence = "`" * max(3, longest_tick_run + 1)
    return f"{fence}text\n{value}\n{fence}\n"


def judge_info(run):
    """Return recorded judge provenance, including legacy Claude run files."""
    provider = run.get("judge_provider")
    model = run.get("judge_model")
    if provider and model:
        return provider, model

    # Before judge provenance was a top-level field, the scorer name in each
    # record was ``llm_judge_<model>``. Preserve that useful information in
    # regenerated leaderboards instead of displaying a vague generic label.
    records = run.get("records", [])
    if run.get("scorer") == "llm_judge" and records:
        legacy_scorer = records[0].get("scorer", "")
        prefix = "llm_judge_"
        if legacy_scorer.startswith(prefix):
            return "anthropic", legacy_scorer[len(prefix):]
    return None, None


def load_all_runs():
    # Match only "<model>__<eval>__<scorer>.json" files that run_eval.py produces.
    # A plain "*.json" glob would also match this script's own output
    # (leaderboard.json), which has a different shape and no "model_id" key --
    # that self-contamination is what causes a KeyError on the second run.
    #
    # Any file that is corrupt or incomplete (partial write, broken upload) is
    # skipped and logged rather than aborting the whole report: one bad file
    # must never take down the leaderboard for every other model. The skipped
    # run will simply be redone the next time that model is evaluated.
    pattern = os.path.join(RESULTS_DIR, "*__*__*.json")
    runs = []
    skipped = []
    for path in sorted(glob.glob(pattern)):
        if not is_valid_result(path):
            skipped.append(path)
            continue
        with open(path) as f:
            runs.append(json.load(f))
    if skipped:
        print(f"[report] skipped {len(skipped)} incomplete/corrupt result file(s):")
        for path in skipped:
            print(f"          - {os.path.basename(path)}")
    return runs


def write_leaderboard(runs):
    lines = [
        "# Safety Eval Results\n",
        "Attack Success Rate (ASR) = fraction of prompts where the model did **not** refuse, per the scorer used. ",
        "Lower is better. Full prompt/response/score transcripts are linked per row.\n",
        "| Model | Eval | Scorer | # Prompts | ASR | Transcript |",
        "|---|---|---|---|---|---|",
    ]
    for run in runs:
        safe_model = run["model_id"].replace("/", "__")
        transcript_fname = transcript_filename(run)
        lines.append(
            f"| {run['model_id']} | {run['eval']} | {run['scorer']} | "
            f"{run['n_prompts']} | {run['attack_success_rate']:.1%} | "
            f"[view]({transcript_fname}) |"
        )
    with open(os.path.join(RESULTS_DIR, "README.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def transcript_filename(run):
    safe_model = run["model_id"].replace("/", "__")
    judge_suffix = ""
    # Legacy files predate top-level judge provenance and already have public
    # transcript URLs without this suffix. Only new-format runs get it.
    if run["scorer"] == "llm_judge" and run.get("judge_provider") and run.get("judge_model"):
        judge_suffix = f"__{run['judge_provider']}__{run['judge_model'].replace('/', '__')}"
    return f"{safe_model}__{run['eval']}__{run['scorer']}{judge_suffix}.md"


def write_transcript(run):
    fname = transcript_filename(run)
    judge_provider, judge_model = judge_info(run)
    judge_description = f"Judge: **{judge_provider} / {judge_model}**.\n" if judge_model else ""
    lines = [
        f"# {run['model_id']} — {run['eval']} ({run['scorer']})\n",
        f"ASR: **{run['attack_success_rate']:.1%}** across {run['n_prompts']} prompts.\n",
        judge_description,
        "---\n",
    ]
    for r in run["records"]:
        flag = "🔴 SUCCESS (complied)" if r["attack_success"] else "🟢 refused"
        lines.append(f"### {r['prompt_id']}  {flag}")
        lines.append(f"*category: {r['category']} | source: {r['source']}*\n")
        lines.append(f"**Prompt:**\n{_fenced_text(r['prompt'])}")
        lines.append(f"**Response:**\n{_fenced_text(r['response'])}")
        lines.append(f"**Score details:** `{json.dumps({k: v for k, v in r.items() if k not in ('prompt','response')})}`\n")
        lines.append("---\n")
    with open(os.path.join(RESULTS_DIR, fname), "w") as f:
        f.write("\n".join(lines))


def write_leaderboard_json(runs):
    """Small, single-file summary (no full transcripts) for the public
    site to fetch in one request -- keeps it fast and avoids GitHub API
    rate limits even with many visitors."""
    entries = []
    for run in runs:
        judge_provider, judge_model = judge_info(run)
        entries.append({
            "model_id": run["model_id"],
            "eval": run["eval"],
            "scorer": run["scorer"],
            "n_prompts": run["n_prompts"],
            "attack_success_rate": run["attack_success_rate"],
            "judge_provider": judge_provider,
            "judge_model": judge_model,
            "transcript_file": transcript_filename(run),
        })
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runs": entries,
    }
    with open(os.path.join(RESULTS_DIR, "leaderboard.json"), "w") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    runs = load_all_runs()
    if not runs:
        print("[report] no results/*.json found yet -- run run_eval.py first.")
    else:
        write_leaderboard(runs)
        write_leaderboard_json(runs)
        for run in runs:
            write_transcript(run)
        print(f"[report] wrote results/README.md, results/leaderboard.json + {len(runs)} transcript file(s).")
