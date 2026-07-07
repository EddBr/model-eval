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
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from result_paths import is_valid_result

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


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
        transcript_fname = f"{safe_model}__{run['eval']}__{run['scorer']}.md"
        lines.append(
            f"| {run['model_id']} | {run['eval']} | {run['scorer']} | "
            f"{run['n_prompts']} | {run['attack_success_rate']:.1%} | "
            f"[view]({transcript_fname}) |"
        )
    with open(os.path.join(RESULTS_DIR, "README.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def write_transcript(run):
    safe_model = run["model_id"].replace("/", "__")
    fname = f"{safe_model}__{run['eval']}__{run['scorer']}.md"
    lines = [
        f"# {run['model_id']} — {run['eval']} ({run['scorer']})\n",
        f"ASR: **{run['attack_success_rate']:.1%}** across {run['n_prompts']} prompts.\n",
        "---\n",
    ]
    for r in run["records"]:
        flag = "🔴 SUCCESS (complied)" if r["attack_success"] else "🟢 refused"
        lines.append(f"### {r['prompt_id']}  {flag}")
        lines.append(f"*category: {r['category']} | source: {r['source']}*\n")
        lines.append(f"**Prompt:**\n> {r['prompt']}\n")
        lines.append(f"**Response:**\n> {r['response']}\n")
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
        safe_model = run["model_id"].replace("/", "__")
        entries.append({
            "model_id": run["model_id"],
            "eval": run["eval"],
            "scorer": run["scorer"],
            "n_prompts": run["n_prompts"],
            "attack_success_rate": run["attack_success_rate"],
            "transcript_file": f"{safe_model}__{run['eval']}__{run['scorer']}.md",
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
