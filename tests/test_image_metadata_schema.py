import pytest
from pydantic import ValidationError

from app.schemas.image_metadata import ImageMetadata


def test_valid_image_metadata() -> None:
    metadata = ImageMetadata(
        subject="red fox",
        category="animal",
        attributes=["orange fur", "wild", "forest"],
        caption="A red fox standing in a forest",
        confidence=0.94,
    )

    assert metadata.subject == "red fox"
    assert metadata.confidence == 0.94


def test_confidence_above_one_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ImageMetadata(
            subject="red fox",
            category="animal",
            attributes=[],
            caption="A fox",
            confidence=1.5,
        )
