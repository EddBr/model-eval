"""Tiny, dependency-free helpers shared by run_eval.py and run_batch.py.

Kept separate from run_eval.py on purpose: run_eval.py imports model_runner.py,
which imports torch. run_batch.py needs the filename convention below but
should NOT have to pay for a torch import just to list/skip models -- that
would make --dry-run and the resumability check unnecessarily heavy.
"""
import os


def result_path(model_id: str, eval_name: str, scorer_name: str, out_dir: str) -> str:
    safe_model_name = model_id.replace("/", "__")
    fname = f"{safe_model_name}__{eval_name}__{scorer_name}.json"
    return os.path.join(out_dir, fname)
