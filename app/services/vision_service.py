from pathlib import Path

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.image_metadata import (
    ImageAnalysisResult,
    ImageMetadata,
)
from app.services.cost_tracker import log_ai_call


VISION_PROMPT = """
Analyze this image carefully.

Return structured metadata describing ONLY what is visibly present.

Requirements:
- subject: the main subject
- category: a broad category
- attributes: important visible characteristics
- caption: concise factual description
- confidence: confidence from 0.0 to 1.0

Do not invent details.
If the subject is uncertain, lower the confidence score.
"""


class VisionProcessingError(Exception):
    pass


def build_analysis_result(
    metadata: ImageMetadata,
) -> ImageAnalysisResult:
    needs_review = (
        metadata.confidence
        < settings.vision_confidence_threshold
    )

    review_reason = None

    if needs_review:
        review_reason = (
            "Vision confidence below threshold: "
            f"{metadata.confidence:.2f} < "
            f"{settings.vision_confidence_threshold:.2f}"
        )

    return ImageAnalysisResult(
        metadata=metadata,
        needs_review=needs_review,
        review_reason=review_reason,
    )


class VisionService:
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise VisionProcessingError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

    def analyze_image(
        self,
        image_path: str | Path,
    ) -> ImageAnalysisResult:
        path = Path(image_path)

        if not path.exists():
            raise VisionProcessingError(
                f"Image does not exist: {path}"
            )

        image_bytes = path.read_bytes()
        mime_type = self._get_mime_type(path)

        try:
            response = self.client.models.generate_content(
                model=settings.vision_model,
                contents=[
                    VISION_PROMPT,
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ImageMetadata,
                    temperature=0,
                ),
            )

            metadata = ImageMetadata.model_validate_json(
                response.text
            )

            usage = response.usage_metadata

            input_units = (
                getattr(
                    usage,
                    "prompt_token_count",
                    None,
                )
                if usage
                else None
            )

            output_units = (
                getattr(
                    usage,
                    "candidates_token_count",
                    None,
                )
                if usage
                else None
            )

            log_ai_call(
                call_type="vision",
                provider="gemini",
                model=settings.vision_model,
                entity_type="image",
                entity_id=path.name,
                input_units=input_units,
                output_units=output_units,
                estimated_cost=0.0,
            )

        except ValidationError as exc:
            raise VisionProcessingError(
                "Vision model returned invalid "
                f"structured output: {exc}"
            ) from exc

        except Exception as exc:
            raise VisionProcessingError(
                f"Vision request failed: {exc}"
            ) from exc

        return build_analysis_result(metadata)

    @staticmethod
    def _get_mime_type(path: Path) -> str:
        suffix = path.suffix.lower()

        supported = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }

        mime_type = supported.get(suffix)

        if not mime_type:
            raise VisionProcessingError(
                f"Unsupported image format: {suffix}"
            )

        return mime_type