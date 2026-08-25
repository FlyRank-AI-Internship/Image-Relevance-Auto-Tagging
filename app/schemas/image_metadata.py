from pydantic import BaseModel, Field, field_validator


class ImageMetadata(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    attributes: list[str] = Field(default_factory=list)
    caption: str = Field(min_length=1, max_length=1000)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values if value.strip()]
        return cleaned
