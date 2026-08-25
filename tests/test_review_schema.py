import pytest
from pydantic import ValidationError

from app.schemas.review import ReviewCreate


def test_review_accepts_approval():
    review = ReviewCreate(
        post_id=1,
        image_id=5,
        decision="approved",
    )

    assert review.decision == "approved"


def test_review_rejects_invalid_decision():
    with pytest.raises(ValidationError):
        ReviewCreate(
            post_id=1,
            image_id=5,
            decision="maybe",
        )