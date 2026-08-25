from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.schemas.matching import PostInput

from app.services.matching_service import rank_images_for_post


router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)


@router.post("")
def create_post(
    payload: PostInput,
    db: Session = Depends(get_db),
):
    post = Post(
        title=payload.title,
        body=payload.body,
        expected_subject=payload.expected_subject,
        expected_category=payload.expected_category,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@router.get("/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found.",
        )

    return post

@router.get("/{post_id}/images")
def get_post_images(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found.",
        )

    ranked = rank_images_for_post(
        db,
        post,
    )

    accepted = [
        item
        for item in ranked
        if item.guard.accepted
    ]

    if not accepted:
        return {
            "post_id": post.id,
            "status": "no_confident_match",
            "message": (
                "No confident match found. "
                "Candidates failed similarity, "
                "confidence, category, or subject checks."
            ),
            "selected": None,
            "candidates": ranked,
        }

    return {
        "post_id": post.id,
        "status": "matched",
        "selected": accepted[0],
        "candidates": ranked,
    }