import csv
import io
import requests
from .base import BaseEval

STRONGREJECT_CSV_URL = (
    "https://raw.githubusercontent.com/alexandrasouly/strongreject/"
    "main/strongreject_dataset/strongreject_dataset.csv"
)


class StrongRejectEval(BaseEval):
    """StrongREJECT: ~313 fact-verifiable harmful prompts with a
    willingness/ability rubric (Souly et al., 2024). Open (MIT), pulled
    directly from the authors' GitHub repo -- no auth required.
    """

    name = "strongreject"

    def load(self, n: int | None = None) -> list[dict]:
        resp = requests.get(STRONGREJECT_CSV_URL, timeout=30)
        resp.raise_for_status()
        reader = csv.DictReader(io.StringIO(resp.text))

        rows = []
        for i, row in enumerate(reader):
            prompt_col = next((c for c in row if c.lower() in ("forbidden_prompt", "prompt")), None)
            cat_col = next((c for c in row if c.lower() == "category"), None)
            rows.append({
                "id": f"strongreject-{i:03d}",
                "prompt": row[prompt_col] if prompt_col else list(row.values())[0],
                "category": row[cat_col] if cat_col else "unknown",
                "source": "alexandrasouly/strongreject",
            })
        return rows[:n] if n else rows
