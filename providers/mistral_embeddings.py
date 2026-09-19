from mistralai.client import Mistral
from config import get_settings

MODEL = "mistral-embed"


class MistralEmbeddingProvider:
    def __init__(self):
        settings = get_settings()
        self.client = Mistral(api_key=settings.mistral_api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("No text provided for embedding.")

        response = self.client.embeddings.create(
            model=MODEL,
            inputs=texts,
        )

        return [item.embedding for item in response.data]
