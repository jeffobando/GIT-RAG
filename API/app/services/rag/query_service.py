from app.core.config import Settings
from app.services.rag.pipeline import build_generator, generator_signature
from app.state.rag_state import rag_state

_base_generator = None
_base_generator_signature: tuple[str, str, str | None] | None = None


def execute_rag_query(settings: Settings, question: str, top_k: int) -> dict:
    if rag_state.pipeline is None or not rag_state.ready:
        raise RuntimeError("RAG runtime is not ready. Run ingestion first.")

    signature = generator_signature(settings)
    if rag_state.generator_signature != signature:
        rag_state.pipeline.generator = build_generator(settings)
        rag_state.generator_signature = signature

    return rag_state.pipeline.ask(question, k=top_k)


def execute_base_query(settings: Settings, question: str) -> dict:
    global _base_generator
    global _base_generator_signature

    signature = generator_signature(settings)
    if _base_generator is None or _base_generator_signature != signature:
        _base_generator = build_generator(settings)
        _base_generator_signature = signature

    prompt = f"""
Responde la siguiente pregunta sin usar contexto recuperado.
Si no tienes información suficiente, dilo claramente.

PREGUNTA:
{question}
""".strip()

    answer = _base_generator.generate(prompt)
    return {
        "answer": str(answer).strip(),
        "sources": [],
        "retrieval_latency_ms": 0.0,
    }
