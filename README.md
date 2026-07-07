# LLM Safety Eval Pipeline

A small, transparent harness for running open HuggingFace models against
established jailbreak/safety benchmarks, with every prompt, raw response,
and score committed to this repo so results are fully auditable.

**Goal:** get the kinks worked out on one model + a couple of evals, then
scale the same pipeline across many models on the Hub.

## What's included

| Benchmark | What it tests | Size | Access |
|---|---|---|---|
| [JailbreakBench (JBB-Behaviors)](https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors) | 100 curated misuse behaviors across 10 policy categories | 100 prompts | open |
| [StrongREJECT](https://github.com/alexandrasouly/strongreject) | Fact-verifiable harmful prompts designed to catch "hollow" jailbreaks | ~313 prompts | open |
| [HarmBench](https://huggingface.co/datasets/walledai/HarmBench) | Standardized harmful behaviors across semantic categories | 400 prompts | **gated** — accept terms on HF + set `HF_TOKEN` |

Scoring is pluggable:
- `rule_based` (default, free): keyword/refusal-phrase matching, same spirit as the baseline judges used in these papers.
- `llm_judge` (optional, costs a little API credit): StrongREJECT-style rubric scored by Claude, giving 0–5 specificity/convincing scores instead of a binary.

Neither scorer is "correct" — refusal-string matching has known false positives/negatives (documented in the JailbreakBench paper itself), and LLM judges have their own biases. Read the transcripts, not just the aggregate ASR.

## One-time setup

1. Create a new (or use an existing) GitHub repo to hold this project + results.
2. Push this folder to it:
   ```bash
   cd llm-safety-evals
   git init
   git add .
   git commit -m "init eval pipeline"
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```
3. Open `notebooks/run_on_colab.ipynb` in Google Colab (free T4 GPU is enough for models in the 0.5B–3B range).
4. In Colab's Secrets panel (key icon, left sidebar), add:
   - `GITHUB_TOKEN` — personal access token with `repo` scope, so the notebook can push results back.
   - `HF_TOKEN` — only needed for HarmBench (gated dataset).
   - `ANTHROPIC_API_KEY` — only needed if you switch to the `llm_judge` scorer.

## Running locally instead of Colab

```bash
pip install -r requirements.txt
python src/run_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --eval jailbreakbench,strongreject --n 15 --scorer rule_based
python src/report.py
```

Results land in `results/<model>__<eval>__<scorer>.json` (raw) and
`results/<model>__<eval>__<scorer>.md` (readable transcript), with a
`results/README.md` leaderboard summarizing attack success rate (ASR)
across all runs so far.

**Already-tested models are skipped automatically.** Both `run_eval.py` and
`run_batch.py` check for a *complete, valid* results file before doing any
work -- re-running a model you've already tested is a no-op (model isn't even
loaded), so it's safe to re-run commands without worrying about burning
GPU time twice. Pass `--force` to re-run anyway (e.g. after changing `--n`
or fixing a scoring bug).

**Incomplete or corrupt results are detected and redone.** A result file is
written in one shot at the very end of an eval, so an eval is atomic: it's
either fully finished or not present at all. But a killed process or a broken
upload can leave a truncated/corrupt file behind. The skip check uses
`result_paths.is_valid_result()`, which requires the file to parse and to
contain a record for every prompt it claims (`n_prompts == len(records)`) --
so a partial file counts as *not done* and is simply re-run and overwritten,
rather than being trusted. If you'd rather not reason about it, just re-run
the same command (or add `--force`): finished evals are skipped and only the
missing/broken `(model, eval, scorer)` combos are redone.

## Iterating through many models

`models.txt` (repo root) is a plain list of HF model ids, one per line --
edit it freely. `src/run_batch.py` runs every model in that list through
`run_eval.py`, one subprocess per model:

```bash
python src/run_batch.py --models-file models.txt --eval jailbreakbench,strongreject --n 15 --scorer rule_based --push
```

- **Resumable**: skips any model that already has *complete, valid* result
  files for every requested eval/scorer combo, so re-running after a
  disconnect only does the remaining work. A model with a missing, corrupt,
  or half-written result file is treated as not-done and re-run (and within
  it, only the affected eval is redone).
- **Report never wedges on a bad file**: `report.py` skips any unreadable or
  incomplete result file -- logging which ones -- and still regenerates
  `leaderboard.json` from the good runs. One broken upload can't take the
  whole leaderboard down; the skipped run is regenerated next time that model
  is evaluated.
- **Fault-isolated**: a model that fails to load (gated without a token,
  too large for the GPU, no usable chat template) is logged to
  `results/_failures.log` and the batch moves on to the next one.
- **Subprocess-per-model on purpose**: each model gets a clean process
  exit, which reliably frees GPU memory before the next one loads --
  important on a free-tier GPU where memory fragmentation from repeated
  in-process model loads/unloads is a common source of crashes partway
  through a long batch.
- `--push` commits + pushes after each model, not just at the end, so
  progress survives a Colab timeout.
- `--dry-run` prints what would run without running it -- useful after
  editing `models.txt` to sanity-check what's queued vs. already done.

The Colab notebook has a "Batch mode" section below the single-model cells that wraps this same command.

## Public leaderboard site

`site/` is a static, zero-build HTML/CSS/JS leaderboard. It fetches
`results/leaderboard.json` straight from GitHub at page load, so it's
always current with whatever the Colab notebook last pushed -- no
rebuild or redeploy needed when new results land.

**One-time setup:**

1. Open `site/app.js` and set `OWNER` to your GitHub username (and `REPO`/`BRANCH` if they differ from the defaults).
2. Commit and push.
3. On [vercel.com](https://vercel.com), "Add New Project" → import this GitHub repo. The included `vercel.json` points Vercel at the `site/` folder — no other config needed.
4. Vercel auto-deploys on every push, but since the page fetches live data from GitHub, it'll show fresh results even between deploys.

Once `results/leaderboard.json` exists in the repo (created automatically by `src/report.py`), the site picks it up on the next page load. Until then it shows an empty-ledger message with a pointer to run the notebook.

If you'd rather use GitHub Pages instead: enable Pages in repo settings, set the source to the `site/` folder (or move its contents to `docs/` if your plan requires that), and it'll serve the same static files with no build step either.

## Adding a new model

No code changes needed — just point `--model` at any HF model id with a
chat template (instruction-tuned models work best):

```bash
python src/run_eval.py --model meta-llama/Llama-3.2-1B-Instruct --eval all --n 0
```

Some gated/large models will need `HF_TOKEN` set and a bigger Colab GPU tier.

## Adding a new eval

Add a file under `src/evals/` implementing `BaseEval.load()` (returns a
list of `{id, prompt, category, source}` dicts), then register it in
`src/evals/__init__.py`. Same pattern for a new scorer under `src/scoring/`.

## Roadmap / not yet built

- **Scheming / deception evals** — a natural next step once jailbreak
  robustness is dialed in. Worth looking at Apollo Research's scheming
  evaluations and METR's autonomy evals as starting points; these test
  qualitatively different behavior (strategic deception, sandbagging)
  than refusal-bypass, so they'll need a different harness shape (often
  multi-turn, with an evaluator inspecting reasoning traces, not just a
  single prompt/response pair).
- Batched/vLLM inference for faster large-scale runs across many models.
- A proper leaderboard site (currently just `results/README.md`).

## A note on responsible use

This harness generates and stores real model responses to prompts drawn
from harmful-behavior datasets. That's standard practice in AI safety
research (it's exactly what these benchmarks are for), but it also means
this repo's `results/` folder will contain uncensored model outputs,
some of which may attempt to comply with harmful requests. Keep that in
mind before making the repo public, and treat it the way you'd treat any
red-teaming research artifact.
