from pydantic import BaseModel

from app.schemas.image_metadata import ImageAnalysisResult


class BatchImageResult(BaseModel):
    filename: str
    success: bool
    result: ImageAnalysisResult | None = None
    error: str | None = None


class BatchProcessingResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: list[BatchImageResult]