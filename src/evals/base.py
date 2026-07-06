from abc import ABC, abstractmethod


class BaseEval(ABC):
    """Every eval loader returns a flat list of dicts with at least:
    {"id": str, "prompt": str, "category": str, "source": str}
    so run_eval.py can treat all evals identically."""

    name: str = "base"

    @abstractmethod
    def load(self, n: int | None = None) -> list[dict]:
        ...
