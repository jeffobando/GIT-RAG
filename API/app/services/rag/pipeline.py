from time import perf_counter

from app.core.config import Settings
from app.services.rag.generator.base import BaseGenerator
from app.services.rag.generator.local_generator import LocalGeneratorService
from app.services.rag.generator.openai_generator import OpenAIGeneratorService


class RAGPipeline:
    def __init__(self, retriever, generator: BaseGenerator):
        self.retriever = retriever
        self.generator = generator

    def build_prompt(self, query: str, docs: list[dict]) -> str:
        context = "\n\n".join(d["text"] for d in docs)

        return f"""
Eres un asistente tecnico experto.

Responde usando unicamente el contexto recuperado.
Si el contexto no contiene suficiente informacion, dilo claramente.
Solo estas autorizado para responder preguntas que tengan que ver con git/github y politicas de la empresa.

CONTEXTO:
{context}

PREGUNTA:
{query}

RESPUESTA:
""".strip()

    def ask(self, query: str, k: int = 5) -> dict:
        retrieval_start = perf_counter()
        docs = self.retriever.retrieve(query, k=k)
        retrieval_latency_ms = (perf_counter() - retrieval_start) * 1000

        prompt = self.build_prompt(query, docs)
        generation_start = perf_counter()
        answer = self.generator.generate(prompt)
        generation_latency_ms = (perf_counter() - generation_start) * 1000

        return {
            "answer": answer,
            "sources": docs,
            "retrieval_latency_ms": retrieval_latency_ms,
            "generation_latency_ms": generation_latency_ms,
            "total_latency_ms": retrieval_latency_ms + generation_latency_ms,
        }


def generator_signature(settings: Settings) -> tuple[str, str, str | None]:
    provider = settings.llm_provider.strip().lower()
    return provider, settings.llm_model, settings.openai_api_key


def build_generator(settings: Settings) -> BaseGenerator:
    provider = settings.llm_provider.strip().lower()
    if provider == "openai":
        return OpenAIGeneratorService(
            model_name=settings.llm_model,
            api_key=settings.openai_api_key,
        )
    if provider == "local":
        return LocalGeneratorService(
            model_name=settings.llm_model,
            input_max_tokens=settings.generation_input_max_tokens,
            max_new_tokens=settings.generation_max_new_tokens,
        )
    raise ValueError(
        f"Unsupported llm_provider '{settings.llm_provider}'. Expected 'openai' or 'local'."
    )
