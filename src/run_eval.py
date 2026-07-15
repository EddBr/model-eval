"""
Usage examples:

  # quick smoke test: 10 prompts, one eval, free scorer
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval jailbreakbench --n 10

  # full run across all evals
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval all --n 0

  # higher-fidelity scoring (costs a little API credit)
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval strongreject --scorer llm_judge

  # re-run even if results already exist (normally skipped to save compute)
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval jailbreakbench --force

Every single (prompt, response, score) triple is written to a JSON file
under results/ -- nothing is aggregated-away, so the raw transcript is
always inspectable.

By default, any (model, eval, scorer) combo that already has a results
file is skipped rather than re-run -- re-testing an already-tested model
just burns GPU time for an identical result. Pass --force to override.
"""
import argparse
from functools import partial
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from model_runner import ModelRunner
from evals import EVAL_REGISTRY
from scoring import SCORER_REGISTRY
from scoring.llm_judge import DEFAULT_MODEL, DEFAULT_PROVIDER
from result_paths import result_path, is_valid_result


def run(model_id: str, eval_names: list[str], n: int, scorer_name: str, out_dir: str,
        judge_provider: str = DEFAULT_PROVIDER, judge_model: str = DEFAULT_MODEL,
        force: bool = False):
    # Figure out up front which evals actually need running, so we can skip
    # loading the model entirely if there's nothing left to do -- that's
    # where the real compute cost is, not the dataset loading or scoring.
    pending = []
    for eval_name in eval_names:
        existing = result_path(model_id, eval_name, scorer_name, out_dir, judge_provider, judge_model)
        if force:
            pending.append(eval_name)
        elif is_valid_result(existing):
            print(f"[run_eval] {model_id} / {eval_name} / {scorer_name} already tested -- skipping ({existing})")
        elif os.path.exists(existing):
            # File is there but corrupt/incomplete (partial write, broken upload).
            # Re-run it from scratch rather than trusting a half-finished result.
            print(f"[run_eval] {model_id} / {eval_name} / {scorer_name} has an incomplete/corrupt result -- re-running ({existing})")
            pending.append(eval_name)
        else:
            pending.append(eval_name)

    if not pending:
        print(f"[run_eval] nothing to do for {model_id} (all requested evals already tested; use --force to re-run)")
        return

    scorer = SCORER_REGISTRY[scorer_name]
    if scorer_name == "llm_judge":
        scorer = partial(scorer, provider=judge_provider, model=judge_model)
    runner = ModelRunner(model_id)

    for eval_name in pending:
        eval_loader = EVAL_REGISTRY[eval_name]()
        items = eval_loader.load(n=n or None)
        print(f"[run_eval] {eval_name}: {len(items)} prompts")

        records = []
        for item in items:
            gen = runner.generate(item["prompt"])
            result = scorer(item["prompt"], gen["response"])

            records.append({
                "eval": eval_name,
                "model_id": model_id,
                "prompt_id": item["id"],
                "category": item["category"],
                "source": item["source"],
                "prompt": item["prompt"],
                "response": gen["response"],
                "elapsed_sec": gen["elapsed_sec"],
                **result,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            })
            success_flag = "SUCCESS" if result["attack_success"] else "refused"
            print(f"  [{item['id']}] {success_flag}")

        asr = sum(r["attack_success"] for r in records) / len(records) if records else 0.0

        out_path = result_path(model_id, eval_name, scorer_name, out_dir, judge_provider, judge_model)
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump({
                "model_id": model_id,
                "eval": eval_name,
                "scorer": scorer_name,
                **({"judge_provider": judge_provider, "judge_model": judge_model}
                   if scorer_name == "llm_judge" else {}),
                "n_prompts": len(records),
                "attack_success_rate": round(asr, 4),
                "records": records,
            }, f, indent=2)
        print(f"[run_eval] wrote {out_path}  (ASR={asr:.1%})")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="HF model id, e.g. Qwen/Qwen2.5-1.5B-Instruct")
    p.add_argument("--eval", default="all", help="jailbreakbench | harmbench | strongreject | all")
    p.add_argument("--n", type=int, default=10, help="prompts per eval (0 = all)")
    p.add_argument("--scorer", default="rule_based", choices=list(SCORER_REGISTRY.keys()))
    p.add_argument("--judge-provider", default=DEFAULT_PROVIDER, choices=("anthropic", "openai"),
                   help="LLM-judge API provider (only used with --scorer llm_judge)")
    p.add_argument("--judge-model", default=DEFAULT_MODEL,
                   help="LLM-judge model ID (only used with --scorer llm_judge)")
    p.add_argument("--out", default="results")
    p.add_argument("--force", action="store_true", help="re-run even if results already exist for this model/eval/scorer")
    args = p.parse_args()

    if args.eval == "all":
        eval_names = list(EVAL_REGISTRY.keys())
    else:
        eval_names = [e.strip() for e in args.eval.split(",") if e.strip()]
        unknown = [e for e in eval_names if e not in EVAL_REGISTRY]
        if unknown:
            raise SystemExit(f"Unknown eval name(s): {unknown}. Choices: {list(EVAL_REGISTRY.keys())} or 'all'")

    run(args.model, eval_names, args.n, args.scorer, args.out,
        judge_provider=args.judge_provider, judge_model=args.judge_model, force=args.force)
