import time
from pathlib import Path

from app.schemas.batch import (
    BatchImageResult,
    BatchProcessingResponse,
)
from app.schemas.image_metadata import ImageAnalysisResult
from app.services.vision_service import (
    VisionProcessingError,
    VisionService,
)


def process_image_with_retry(
    image_path: str | Path,
    max_attempts: int = 3,
) -> ImageAnalysisResult:

    service = VisionService()
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return service.analyze_image(image_path)

        except VisionProcessingError as exc:
            last_error = exc

            if attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))

    raise VisionProcessingError(
        f"Image processing failed after "
        f"{max_attempts} attempts: {last_error}"
    )


def process_batch(
    image_paths: list[Path],
) -> BatchProcessingResponse:

    results: list[BatchImageResult] = []

    for path in image_paths:
        try:
            analysis = process_image_with_retry(path)

            results.append(
                BatchImageResult(
                    filename=path.name,
                    success=True,
                    result=analysis,
                )
            )

        except VisionProcessingError as exc:
            results.append(
                BatchImageResult(
                    filename=path.name,
                    success=False,
                    error=str(exc),
                )
            )

    succeeded = sum(
        1 for item in results if item.success
    )

    return BatchProcessingResponse(
        total=len(results),
        succeeded=succeeded,
        failed=len(results) - succeeded,
        results=results,
    )