from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.review import Review
from app.models.suggestion import Suggestion


router = APIRouter(
    prefix="/suggestions",
    tags=["suggestions"],
)


@router.get("/{suggestion_id}")
def get_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
):
    suggestion = db.get(
        Suggestion,
        suggestion_id,
    )

    if suggestion is None:
        raise HTTPException(
            status_code=404,
            detail="Suggestion not found.",
        )

    return suggestion


@router.post("/{suggestion_id}/approve")
def approve_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
):
    suggestion = db.get(
        Suggestion,
        suggestion_id,
    )

    if suggestion is None:
        raise HTTPException(
            status_code=404,
            detail="Suggestion not found.",
        )

    suggestion.review_status = "approved"

    review = Review(
        post_id=suggestion.post_id,
        image_id=suggestion.image_id,
        decision="approved",
        reason="Suggestion approved by reviewer.",
    )

    db.add(review)
    db.commit()
    db.refresh(suggestion)

    return {
        "suggestion_id": suggestion.id,
        "review_status": suggestion.review_status,
        "message": "Suggestion approved.",
    }


@router.post("/{suggestion_id}/reject")
def reject_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
):
    suggestion = db.get(
        Suggestion,
        suggestion_id,
    )

    if suggestion is None:
        raise HTTPException(
            status_code=404,
            detail="Suggestion not found.",
        )

    suggestion.review_status = "rejected"

    review = Review(
        post_id=suggestion.post_id,
        image_id=suggestion.image_id,
        decision="rejected",
        reason="Suggestion rejected by reviewer.",
    )

    db.add(review)
    db.commit()
    db.refresh(suggestion)

    return {
        "suggestion_id": suggestion.id,
        "review_status": suggestion.review_status,
        "message": "Suggestion rejected.",
    }