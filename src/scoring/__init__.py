from . import rule_based, llm_judge

SCORER_REGISTRY = {
    "rule_based": rule_based.score,
    "llm_judge": llm_judge.score,
}
