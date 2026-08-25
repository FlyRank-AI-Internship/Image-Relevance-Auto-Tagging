from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.image import ImageRecord
from app.models.post import Post
from app.models.review import Review
from app.schemas.review import ReviewCreate


router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.post("")
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
):
    post = db.get(Post, payload.post_id)
    image = db.get(ImageRecord, payload.image_id)

    if post is None:
        raise HTTPException(404, "Post not found.")

    if image is None:
        raise HTTPException(404, "Image not found.")

    review = Review(
        post_id=payload.post_id,
        image_id=payload.image_id,
        decision=payload.decision,
        reason=payload.reason,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


@router.get("")
def list_reviews(
    db: Session = Depends(get_db),
):
    return (
        db.query(Review)
        .order_by(Review.id.desc())
        .all()
    )