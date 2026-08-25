from pydantic import BaseModel, Field


class PostInput(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=300,
    )

    body: str = Field(
        min_length=1,
    )

    expected_subject: str = Field(
        min_length=1,
        max_length=200,
    )

    expected_category: str = Field(
        min_length=1,
        max_length=100,
    )   


class MatchCandidate(BaseModel):
    image_id: str
    subject: str
    category: str
    caption: str
    confidence: float
    similarity_score: float


class GuardDecision(BaseModel):
    accepted: bool
    reason: str


class RankedImageResult(BaseModel):
    candidate: MatchCandidate
    guard: GuardDecision


class MatchingResponse(BaseModel):
    post_title: str
    status: str
    selected: RankedImageResult | None = None
    candidates: list[RankedImageResult]
    message: str | None = None