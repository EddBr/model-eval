"""
Iterate a list of HF models through run_eval.py, one subprocess per model.

Why subprocess-per-model instead of looping in-process: each subprocess gets
a clean exit, which reliably frees GPU memory between models. Manually
tearing down a shared transformers/accelerate model between iterations is a
common source of memory-fragmentation crashes partway through a long batch
on a free-tier GPU -- this sidesteps that entirely.

Usage:
  python src/run_batch.py --models-file models.txt --eval jailbreakbench,strongreject --n 15 --scorer rule_based --push

Resumability: before running a model, checks whether result files for all
requested (eval, scorer) combos already exist and skips if so -- safe to
re-run after a Colab disconnect without redoing finished work.

Fault isolation: a model that fails to load or errors mid-run is logged to
results/_failures.log and the batch continues to the next model.
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from result_paths import result_path

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
RESULTS_DIR = os.path.join(REPO_ROOT, "results")
FAILURES_LOG = os.path.join(RESULTS_DIR, "_failures.log")


def read_model_list(path: str) -> list[str]:
    models = []
    with open(path) as f:
        for line in f:
            line = line.split("#", 1)[0].strip()  # allow trailing/whole-line comments
            if line:
                models.append(line)
    return models


def already_done(model_id: str, eval_names: list[str], scorer: str) -> bool:
    return all(os.path.exists(result_path(model_id, e, scorer, RESULTS_DIR)) for e in eval_names)


def log_failure(model_id: str, error: str):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(FAILURES_LOG, "a") as f:
        f.write(f"{datetime.now(timezone.utc).isoformat()}  {model_id}  {error}\n")


def git_commit_and_push(model_id: str, git_author_name: str, git_author_email: str, auth_header: str):
    """Best-effort: regenerate the report and push. Failures here are logged
    but don't stop the batch -- the next model's push will pick up any
    changes this one missed."""
    try:
        subprocess.run([sys.executable, "src/report.py"], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "config", "user.email", git_author_email], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "config", "user.name", git_author_name], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "add", "results/"], cwd=REPO_ROOT, check=True)
        commit = subprocess.run(
            ["git", "commit", "-m", f"batch eval run: {model_id}"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        if commit.returncode != 0 and "nothing to commit" not in commit.stdout:
            print(f"[run_batch] commit warning for {model_id}: {commit.stdout} {commit.stderr}")
            return
        subprocess.run(
            ["git", "-c", f"http.extraheader={auth_header}", "push"],
            cwd=REPO_ROOT, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[run_batch] push failed for {model_id}: {e}")


def run(models: list[str], eval_names: list[str], n: int, scorer: str,
        push: bool, git_author_name: str, git_author_email: str, auth_header: str,
        dry_run: bool, force: bool = False):
    print(f"[run_batch] {len(models)} model(s) queued")
    for i, model_id in enumerate(models, 1):
        print(f"\n=== [{i}/{len(models)}] {model_id} ===")

        if not force and already_done(model_id, eval_names, scorer):
            print(f"[run_batch] already have all results for {model_id} -- skipping")
            continue

        if dry_run:
            print(f"[run_batch] (dry run) would run: {model_id}")
            continue

        cmd = [
            sys.executable, "src/run_eval.py",
            "--model", model_id,
            "--eval", ",".join(eval_names),
            "--n", str(n),
            "--scorer", scorer,
        ]
        if force:
            cmd.append("--force")
        result = subprocess.run(cmd, cwd=REPO_ROOT)

        if result.returncode != 0:
            log_failure(model_id, f"run_eval.py exited {result.returncode}")
            print(f"[run_batch] FAILED: {model_id} (see results/_failures.log) -- continuing")
            continue

        if push:
            git_commit_and_push(model_id, git_author_name, git_author_email, auth_header)

    print("\n[run_batch] done.")
    if os.path.exists(FAILURES_LOG):
        print(f"[run_batch] some models failed -- see {FAILURES_LOG}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--models-file", default=os.path.join(REPO_ROOT, "models.txt"))
    p.add_argument("--models", default=None, help="comma-separated model ids, overrides --models-file")
    p.add_argument("--eval", default="jailbreakbench,strongreject")
    p.add_argument("--n", type=int, default=15)
    p.add_argument("--scorer", default="rule_based")
    p.add_argument("--push", action="store_true", help="commit+push results after each model")
    p.add_argument("--dry-run", action="store_true", help="print what would run without running it")
    p.add_argument("--force", action="store_true", help="re-run models even if results already exist")
    args = p.parse_args()

    if args.models:
        model_list = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        model_list = read_model_list(args.models_file)

    eval_list = [e.strip() for e in args.eval.split(",") if e.strip()]

    run(
        models=model_list,
        eval_names=eval_list,
        n=args.n,
        scorer=args.scorer,
        push=args.push,
        git_author_name=os.environ.get("GIT_AUTHOR_NAME", ""),
        git_author_email=os.environ.get("GIT_AUTHOR_EMAIL", ""),
        auth_header=os.environ.get("AUTH_HEADER", ""),
        dry_run=args.dry_run,
        force=args.force,
    )
