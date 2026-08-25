from pydantic import BaseModel, Field, field_validator


class ImageMetadata(BaseModel):
    subject: str = Field(
        min_length=1,
        max_length=200,
        description="Main subject visible in the image",
    )

    category: str = Field(
        min_length=1,
        max_length=100,
        description="Broad semantic category such as animal, food, person, place",
    )

    attributes: list[str] = Field(
        default_factory=list,
        description="Important visible attributes of the subject",
    )

    caption: str = Field(
        min_length=1,
        max_length=1000,
        description="A factual description of the image",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the classification is correct",
    )

    @field_validator("subject", "category", "caption")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("value cannot be empty")

        return value

    @field_validator("attributes")
    @classmethod
    def clean_attributes(cls, values: list[str]) -> list[str]:
        return [
            value.strip()
            for value in values
            if value and value.strip()
        ]


class ImageAnalysisResult(BaseModel):
    metadata: ImageMetadata
    needs_review: bool
    review_reason: str | None = None