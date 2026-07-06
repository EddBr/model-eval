from datasets import load_dataset
from .base import BaseEval


class HarmBenchEval(BaseEval):
    """HarmBench: 400 standardized harmful behaviors across semantic
    categories (Mazeika et al., 2024).
    https://huggingface.co/datasets/walledai/HarmBench

    NOTE: this dataset is gated on HuggingFace. Before running you must:
      1. Visit the dataset page while logged in to HF and accept the terms.
      2. Set an HF_TOKEN env var (or `huggingface-cli login`) with read access.
    If that isn't set up yet, load() will raise a clear error rather than
    silently failing.
    """

    name = "harmbench"

    def load(self, n: int | None = None) -> list[dict]:
        try:
            dset = load_dataset("walledai/HarmBench", "standard")
        except Exception as e:
            raise RuntimeError(
                "Couldn't load walledai/HarmBench. This dataset is gated: "
                "accept its terms on huggingface.co while logged in, then set "
                "an HF_TOKEN with access. Original error: " + str(e)
            )

        split_name = "train" if "train" in dset else list(dset.keys())[0]
        ds = dset[split_name]
        cols = ds.column_names
        prompt_col = next((c for c in ["prompt", "Behavior", "behavior"] if c in cols), cols[0])
        cat_col = next((c for c in ["category", "SemanticCategory", "semantic_category"] if c in cols), None)

        rows = []
        for i, row in enumerate(ds):
            rows.append({
                "id": f"harmbench-{i:03d}",
                "prompt": row[prompt_col],
                "category": row[cat_col] if cat_col else "unknown",
                "source": "walledai/HarmBench",
            })
        return rows[:n] if n else rows
