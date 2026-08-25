from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.post import Post
from app.schemas.matching import PostInput

from app.services.matching_service import rank_images_for_post

from app.models.image import ImageRecord
from app.models.suggestion import Suggestion

from app.schemas.matching import MatchCandidate

from app.services.embedding_service import EmbeddingService
from app.services.mismatch_guard import evaluate_candidate
from app.services.similarity import cosine_similarity


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

@router.post(
    "/{post_id}/images/{image_id}/check"
)
def check_image_for_post(
    post_id: int,
    image_id: int,
    db: Session = Depends(get_db),
):
    post = db.get(
        Post,
        post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found.",
        )

    image = db.get(
        ImageRecord,
        image_id,
    )

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found.",
        )

    if not image.embedding:
        raise HTTPException(
            status_code=400,
            detail="Image has no embedding.",
        )

    embedding_service = EmbeddingService()

    post_text = (
        f"{post.title}. {post.body}"
    )

    post_vector = embedding_service.embed_text(
        post_text,
        entity_type="post_check",
        entity_id=str(post.id),
    )

    similarity_score = cosine_similarity(
        post_vector,
        image.embedding,
    )

    candidate = MatchCandidate(
        image_id=str(image.id),
        subject=image.subject,
        category=image.category,
        caption=image.caption,
        confidence=image.confidence,
        similarity_score=similarity_score,
    )

    guard = evaluate_candidate(
        candidate=candidate,
        expected_subject=post.expected_subject,
        expected_category=post.expected_category,
    )

    suggestion = Suggestion(
        post_id=post.id,
        image_id=image.id,
        similarity_score=similarity_score,
        guard_status=(
            "accepted"
            if guard.accepted
            else "rejected"
        ),
        guard_reason=guard.reason,
    )

    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)

    return {
        "suggestion_id": suggestion.id,
        "candidate": candidate,
        "guard": guard,
    }