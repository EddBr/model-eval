"""
Usage examples:

  # quick smoke test: 10 prompts, one eval, free scorer
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval jailbreakbench --n 10

  # full run across all evals
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval all --n 0

  # higher-fidelity scoring (costs a little API credit)
  python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval strongreject --scorer llm_judge

Every single (prompt, response, score) triple is written to a JSON file
under results/ -- nothing is aggregated-away, so the raw transcript is
always inspectable.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from model_runner import ModelRunner
from evals import EVAL_REGISTRY
from scoring import SCORER_REGISTRY


def run(model_id: str, eval_names: list[str], n: int, scorer_name: str, out_dir: str):
    runner = ModelRunner(model_id)
    scorer = SCORER_REGISTRY[scorer_name]

    for eval_name in eval_names:
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

        safe_model_name = model_id.replace("/", "__")
        fname = f"{safe_model_name}__{eval_name}__{scorer_name}.json"
        out_path = os.path.join(out_dir, fname)
        os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump({
                "model_id": model_id,
                "eval": eval_name,
                "scorer": scorer_name,
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
    p.add_argument("--out", default="results")
    args = p.parse_args()

    if args.eval == "all":
        eval_names = list(EVAL_REGISTRY.keys())
    else:
        eval_names = [e.strip() for e in args.eval.split(",") if e.strip()]
        unknown = [e for e in eval_names if e not in EVAL_REGISTRY]
        if unknown:
            raise SystemExit(f"Unknown eval name(s): {unknown}. Choices: {list(EVAL_REGISTRY.keys())} or 'all'")

    run(args.model, eval_names, args.n, args.scorer, args.out)
