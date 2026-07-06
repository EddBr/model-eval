from datasets import load_dataset
from .base import BaseEval


class JailbreakBenchEval(BaseEval):
    """JBB-Behaviors: 100 curated misuse behaviors spanning 10 policy
    categories (Chao et al., 2024). Open dataset, no auth required.
    https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors
    """

    name = "jailbreakbench"

    def load(self, n: int | None = None) -> list[dict]:
        dset = load_dataset("JailbreakBench/JBB-Behaviors", "behaviors")
        # split name has shifted between dataset versions ("harmful" vs "train" etc.)
        split_name = "harmful" if "harmful" in dset else list(dset.keys())[0]
        ds = dset[split_name]

        # column name has also shifted ("Goal" vs "goal") -> detect at runtime
        cols = ds.column_names
        prompt_col = next((c for c in ["Goal", "goal", "Behavior", "behavior"] if c in cols), cols[0])
        cat_col = next((c for c in ["Category", "category"] if c in cols), None)

        rows = []
        for i, row in enumerate(ds):
            rows.append({
                "id": f"jbb-{i:03d}",
                "prompt": row[prompt_col],
                "category": row[cat_col] if cat_col else "unknown",
                "source": "JailbreakBench/JBB-Behaviors",
            })
        return rows[:n] if n else rows
