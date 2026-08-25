from typing import Literal

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    post_id: int
    image_id: int
    decision: Literal["approved", "rejected"]
    reason: str | None = None