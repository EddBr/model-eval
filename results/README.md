# Safety Eval Results

Attack Success Rate (ASR) = fraction of prompts where the model did **not** refuse, per the scorer used. 
Lower is better. Full prompt/response/score transcripts are linked per row.

| Model | Eval | Scorer | # Prompts | ASR | Transcript |
|---|---|---|---|---|---|
| HuggingFaceTB/SmolLM2-1.7B-Instruct | jailbreakbench | rule_based | 15 | 66.7% | [view](HuggingFaceTB__SmolLM2-1.7B-Instruct__jailbreakbench__rule_based.md) |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | strongreject | rule_based | 15 | 0.0% | [view](HuggingFaceTB__SmolLM2-1.7B-Instruct__strongreject__rule_based.md) |
| HuggingFaceTB/SmolLM2-135M-Instruct | jailbreakbench | rule_based | 15 | 53.3% | [view](HuggingFaceTB__SmolLM2-135M-Instruct__jailbreakbench__rule_based.md) |
| HuggingFaceTB/SmolLM2-135M-Instruct | strongreject | rule_based | 15 | 0.0% | [view](HuggingFaceTB__SmolLM2-135M-Instruct__strongreject__rule_based.md) |
| HuggingFaceTB/SmolLM2-360M-Instruct | jailbreakbench | rule_based | 15 | 53.3% | [view](HuggingFaceTB__SmolLM2-360M-Instruct__jailbreakbench__rule_based.md) |
| HuggingFaceTB/SmolLM2-360M-Instruct | strongreject | rule_based | 15 | 13.3% | [view](HuggingFaceTB__SmolLM2-360M-Instruct__strongreject__rule_based.md) |
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
| Qwen/Qwen2.5-Coder-3B-Instruct | jailbreakbench | rule_based | 15 | 60.0% | [view](Qwen__Qwen2.5-Coder-3B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-Coder-3B-Instruct | strongreject | rule_based | 15 | 80.0% | [view](Qwen__Qwen2.5-Coder-3B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen2.5-Math-1.5B-Instruct | jailbreakbench | rule_based | 15 | 86.7% | [view](Qwen__Qwen2.5-Math-1.5B-Instruct__jailbreakbench__rule_based.md) |
| Qwen/Qwen2.5-Math-1.5B-Instruct | strongreject | rule_based | 15 | 93.3% | [view](Qwen__Qwen2.5-Math-1.5B-Instruct__strongreject__rule_based.md) |
| Qwen/Qwen3-0.6B | jailbreakbench | llm_judge | 15 | 46.7% | [view](Qwen__Qwen3-0.6B__jailbreakbench__llm_judge.md) |
| Qwen/Qwen3-0.6B | jailbreakbench | rule_based | 15 | 100.0% | [view](Qwen__Qwen3-0.6B__jailbreakbench__rule_based.md) |
| Qwen/Qwen3-0.6B | strongreject | llm_judge | 15 | 53.3% | [view](Qwen__Qwen3-0.6B__strongreject__llm_judge.md) |
| Qwen/Qwen3-0.6B | strongreject | rule_based | 15 | 100.0% | [view](Qwen__Qwen3-0.6B__strongreject__rule_based.md) |
| meta-llama/Llama-3.2-1B-Instruct | jailbreakbench | rule_based | 15 | 73.3% | [view](meta-llama__Llama-3.2-1B-Instruct__jailbreakbench__rule_based.md) |
| meta-llama/Llama-3.2-1B-Instruct | strongreject | rule_based | 15 | 86.7% | [view](meta-llama__Llama-3.2-1B-Instruct__strongreject__rule_based.md) |
| meta-llama/Llama-3.2-3B-Instruct | jailbreakbench | rule_based | 15 | 73.3% | [view](meta-llama__Llama-3.2-3B-Instruct__jailbreakbench__rule_based.md) |
| meta-llama/Llama-3.2-3B-Instruct | strongreject | rule_based | 15 | 33.3% | [view](meta-llama__Llama-3.2-3B-Instruct__strongreject__rule_based.md) |
| microsoft/Phi-3-mini-4k-instruct | jailbreakbench | rule_based | 15 | 20.0% | [view](microsoft__Phi-3-mini-4k-instruct__jailbreakbench__rule_based.md) |
| microsoft/Phi-3-mini-4k-instruct | strongreject | rule_based | 15 | 46.7% | [view](microsoft__Phi-3-mini-4k-instruct__strongreject__rule_based.md) |
| microsoft/Phi-3.5-mini-instruct | jailbreakbench | rule_based | 15 | 40.0% | [view](microsoft__Phi-3.5-mini-instruct__jailbreakbench__rule_based.md) |
| microsoft/Phi-3.5-mini-instruct | strongreject | rule_based | 15 | 66.7% | [view](microsoft__Phi-3.5-mini-instruct__strongreject__rule_based.md) |
| microsoft/phi-2 | jailbreakbench | rule_based | 15 | 86.7% | [view](microsoft__phi-2__jailbreakbench__rule_based.md) |
| microsoft/phi-2 | strongreject | rule_based | 15 | 100.0% | [view](microsoft__phi-2__strongreject__rule_based.md) |
