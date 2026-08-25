from pathlib import Path

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.image_metadata import (
    ImageAnalysisResult,
    ImageMetadata,
)


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

        except ValidationError as exc:
            raise VisionProcessingError(
                f"Vision model returned invalid structured output: {exc}"
            ) from exc

        except Exception as exc:
            raise VisionProcessingError(
                f"Vision request failed: {exc}"
            ) from exc

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