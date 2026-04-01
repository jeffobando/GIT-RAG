from importlib import import_module
from typing import Any

from app.services.rag.generator.base import BaseGenerator


class LocalGeneratorService(BaseGenerator):
    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
        input_max_tokens: int = 3072,
        max_new_tokens: int = 320,
    ):
        try:
            self._torch = import_module("torch")
            transformers = import_module("transformers")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "LocalGeneratorService requires 'torch' and 'transformers'. "
                "Install dependencies to use local generation."
            ) from exc

        auto_tokenizer = getattr(transformers, "AutoTokenizer")
        auto_model_for_causal_lm = getattr(transformers, "AutoModelForCausalLM")

        self.tokenizer: Any = auto_tokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.input_max_tokens = max(512, int(input_max_tokens))
        self.max_new_tokens = max(64, int(max_new_tokens))

        self.device: Any = self._torch.device(
            "cuda" if self._torch.cuda.is_available() else "cpu"
        )
        dtype = (
            self._torch.float16 if self.device.type == "cuda" else self._torch.float32
        )

        self.model: Any = auto_model_for_causal_lm.from_pretrained(
            model_name,
            torch_dtype=dtype,
        )
        self.model.to(device=self.device)
        self.model.eval()

    def generate(self, prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente técnico experto en Git/GitHub. "
                    "Responde solo con el contexto proporcionado. "
                    "Si no hay información suficiente en el contexto, dilo claramente. "
                    "Sé conciso, evita repetir frases y termina la respuesta en una oración completa."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        if hasattr(self.tokenizer, "apply_chat_template"):
            rendered_prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            rendered_prompt = prompt

        inputs = self.tokenizer(
            rendered_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.input_max_tokens,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        prompt_length = int(inputs["input_ids"].shape[-1])

        with self._torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                repetition_penalty=1.10,
                no_repeat_ngram_size=4,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = outputs[0][prompt_length:]
        decoded = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        return decoded

