from google import genai
from google.genai import types

from app.core.config import settings
from app.services.cost_tracker import log_ai_call


class EmbeddingProcessingError(Exception):
    pass


class EmbeddingService:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise EmbeddingProcessingError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def embed_text(
        self,
        text: str,
        *,
        entity_type: str,
        entity_id: str,
    ) -> list[float]:
        cleaned_text = text.strip()

        if not cleaned_text:
            raise EmbeddingProcessingError(
                "Cannot embed empty text."
            )

        try:
            response = self.client.models.embed_content(
                model=settings.embedding_model,
                contents=cleaned_text,
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY",
                ),
            )

            if not response.embeddings:
                raise EmbeddingProcessingError(
                    "Embedding model returned no vector."
                )

            vector = response.embeddings[0].values

            if not vector:
                raise EmbeddingProcessingError(
                    "Embedding vector was empty."
                )

            usage = getattr(
                response,
                "usage_metadata",
                None,
            )

            input_units = (
                getattr(
                    usage,
                    "prompt_token_count",
                    None,
                )
                if usage
                else None
            )

            log_ai_call(
                call_type="embedding",
                provider="gemini",
                model=settings.embedding_model,
                entity_type=entity_type,
                entity_id=entity_id,
                input_units=input_units,
                output_units=None,
                estimated_cost=0.0,
            )

            return list(vector)

        except EmbeddingProcessingError:
            raise

        except Exception as exc:
            raise EmbeddingProcessingError(
                f"Embedding request failed: {exc}"
            ) from exc