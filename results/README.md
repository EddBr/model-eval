# Safety Eval Results

Attack Success Rate (ASR) = fraction of prompts where the model did **not** refuse, per the scorer used. 
Lower is better. Full prompt/response/score transcripts are linked per row.

| Model | Eval | Scorer | # Prompts | ASR | Transcript |
|---|---|---|---|---|---|
| Qwen/Qwen2.5-0.5B-Instruct | jailbreakbench | rule_based | 15 | 66.7% | [view](Qwen__Qwen2.5-0.5B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-0.5B-Instruct | strongreject | rule_based | 15 | 93.3% | [view](Qwen__Qwen2.5-0.5B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen2.5-1.5B-Instruct | jailbreakbench | llm_judge | 15 | 46.7% | [view](Qwen__Qwen2.5-1.5B-Instruct__jailbreakbench__llm_judge.md) |
| Qwen/Qwen2.5-1.5B-Instruct | jailbreakbench | rule_based | 15 | 40.0% | [view](Qwen__Qwen2.5-1.5B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-1.5B-Instruct | strongreject | llm_judge | 15 | 80.0% | [view](Qwen__Qwen2.5-1.5B-Instruct__strongreject__llm_judge.md) |
| Qwen/Qwen2.5-1.5B-Instruct | strongreject | rule_based | 15 | 66.7% | [view](Qwen__Qwen2.5-1.5B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen2.5-3B-Instruct | jailbreakbench | rule_based | 15 | 40.0% | [view](Qwen__Qwen2.5-3B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-3B-Instruct | strongreject | rule_based | 15 | 66.7% | [view](Qwen__Qwen2.5-3B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen2.5-Coder-0.5B-Instruct | jailbreakbench | rule_based | 15 | 93.3% | [view](Qwen__Qwen2.5-Coder-0.5B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-Coder-0.5B-Instruct | strongreject | rule_based | 15 | 80.0% | [view](Qwen__Qwen2.5-Coder-0.5B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen2.5-Coder-1.5B-Instruct | jailbreakbench | rule_based | 15 | 86.7% | [view](Qwen__Qwen2.5-Coder-1.5B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-Coder-1.5B-Instruct | strongreject | rule_based | 15 | 93.3% | [view](Qwen__Qwen2.5-Coder-1.5B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen3-0.6B | jailbreakbench | llm_judge | 15 | 46.7% | [view](Qwen__Qwen3-0.6B__jailbreakbench__llm_judge.md) |
| Qwen/Qwen3-0.6B | jailbreakbench | rule_based | 15 | 100.0% | [view](Qwen__Qwen3-0.6B__jailbreakbench__rule_based.md) |
| Qwen/Qwen3-0.6B | strongreject | llm_judge | 15 | 53.3% | [view](Qwen__Qwen3-0.6B__strongreject__llm_judge.md) |
| Qwen/Qwen3-0.6B | strongreject | rule_based | 15 | 100.0% | [view](Qwen__Qwen3-0.6B__strongreject__rule_based.md) |
