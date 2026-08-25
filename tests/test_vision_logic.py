from app.schemas.image_metadata import (
    ImageAnalysisResult,
    ImageMetadata,
)


def test_low_confidence_can_be_flagged():
    metadata = ImageMetadata(
        subject="unknown animal",
        category="animal",
        attributes=["fur"],
        caption="An animal standing outdoors",
        confidence=0.42,
    )

    result = ImageAnalysisResult(
        metadata=metadata,
        needs_review=True,
        review_reason="Vision confidence below threshold",
    )

    assert result.needs_review is True
    assert result.metadata.confidence == 0.42