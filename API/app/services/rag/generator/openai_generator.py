from openai import OpenAI
from app.services.rag.generator.base import BaseGenerator

class OpenAIGeneratorService(BaseGenerator):
    def __init__(self, model_name: str, api_key: str | None = None):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model_name,
            instructions=(
                "Eres un asistente técnico experto en git/github. "
                "Responde solo con base en el contexto proporcionado. "
                "Si falta información, dilo claramente."
            ),
            input=prompt,
        )
        return response.output_text