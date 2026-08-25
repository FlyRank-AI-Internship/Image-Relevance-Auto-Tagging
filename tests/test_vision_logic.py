from app.schemas.image_metadata import ImageMetadata
from app.services.vision_service import build_analysis_result


def test_high_confidence_image_is_accepted():
    metadata = ImageMetadata(
        subject="red fox",
        category="animal",
        attributes=["orange fur"],
        caption="A red fox standing outdoors.",
        confidence=0.98,
    )

    result = build_analysis_result(metadata)

    assert result.needs_review is False
    assert result.review_reason is None


def test_low_confidence_image_is_flagged():
    metadata = ImageMetadata(
        subject="unknown animal",
        category="animal",
        attributes=["fur"],
        caption="A distant animal in vegetation.",
        confidence=0.42,
    )

    result = build_analysis_result(metadata)

    assert result.needs_review is True
    assert result.review_reason == (
        "Vision confidence below threshold: "
        "0.42 < 0.70"
    )