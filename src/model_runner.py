"""
Thin wrapper around any HuggingFace `transformers` chat model.

Goal: swapping the model under test should be a one-line change
(just a different `model_id`), so the same harness can eventually
run across many/most instruction-tuned models on the Hub.
"""
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class ModelRunner:
    def __init__(self, model_id: str, max_new_tokens: int = 256, dtype: str = "auto"):
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.bfloat16 if self.device == "cuda" else torch.float32

        print(f"[model_runner] loading {model_id} on {self.device} ...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            device_map="auto" if self.device == "cuda" else None,
        )
        if self.device == "cpu":
            self.model.to(self.device)
        self.model.eval()

    def generate(self, prompt: str, system_prompt: str | None = None) -> dict:
        """Runs one prompt through the model's chat template and returns
        the raw response plus basic timing/metadata for transparency."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            input_ids = self.tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, return_tensors="pt"
            ).to(self.model.device)
        except Exception:
            # Fallback for models without a chat template configured
            try:
                text = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
                input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(self.model.device)
            except Exception:
                # Suggested by Gemini
                text = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
                input_ids = self.tokenizer(text, return_tensors="pt").["input_ids"].to(self.model.device)

        start = time.time()
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,  # deterministic by default -> reproducible eval runs
                pad_token_id=self.tokenizer.eos_token_id,
            )
        elapsed = time.time() - start

        new_tokens = output_ids[0][input_ids.shape[-1]:]
        response_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        return {
            "model_id": self.model_id,
            "prompt": prompt,
            "response": response_text.strip(),
            "elapsed_sec": round(elapsed, 2),
        }
