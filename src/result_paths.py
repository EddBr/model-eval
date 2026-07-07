"""Tiny, dependency-free helpers shared by run_eval.py and run_batch.py.

Kept separate from run_eval.py on purpose: run_eval.py imports model_runner.py,
which imports torch. run_batch.py needs the filename convention below but
should NOT have to pay for a torch import just to list/skip models -- that
would make --dry-run and the resumability check unnecessarily heavy.
"""
import json
import os

# Keys every completed run file must carry. Missing any of these means the
# file was written by an older/different code path or is otherwise unusable.
REQUIRED_KEYS = ("model_id", "eval", "scorer", "n_prompts", "attack_success_rate", "records")


def result_path(model_id: str, eval_name: str, scorer_name: str, out_dir: str) -> str:
    safe_model_name = model_id.replace("/", "__")
    fname = f"{safe_model_name}__{eval_name}__{scorer_name}.json"
    return os.path.join(out_dir, fname)


def is_valid_result(path: str) -> bool:
    """True only if `path` is a *complete, parseable* run file.

    A result file is written in one shot at the end of an eval, so in practice
    it's either fully there or not there at all -- but a killed process or a
    broken/partial upload can leave a truncated or corrupt file on disk. Such a
    file must NOT count as "done": it would (a) make the resume logic skip a run
    that never really finished, and (b) crash report.py's json.load, taking the
    whole leaderboard down with it. Treating an invalid file as "not done" means
    the next run simply redoes that (model, eval, scorer) and overwrites it.

    Deliberately dependency-free (no torch/transformers) so run_batch.py's
    resume check and --dry-run stay cheap.
    """
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict) or any(k not in data for k in REQUIRED_KEYS):
        return False
    records = data.get("records")
    # An eval with zero prompts scored is not a real result; and the record
    # count must match the reported n_prompts, which catches truncated writes.
    if not isinstance(records, list) or len(records) == 0:
        return False
    if data.get("n_prompts") != len(records):
        return False
    return True
