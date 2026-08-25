from sqlalchemy.orm import Session

from app.models.image import ImageRecord
from app.models.post import Post
from app.schemas.matching import (
    MatchCandidate,
    RankedImageResult,
)
from app.services.embedding_service import EmbeddingService
from app.services.mismatch_guard import evaluate_candidate
from app.services.similarity import cosine_similarity


def rank_images_for_post(
    db: Session,
    post: Post,
) -> list[RankedImageResult]:

    embedding_service = EmbeddingService()

    post_text = f"{post.title}. {post.body}"

    post_vector = embedding_service.embed_text(
        post_text,
        entity_type="post",
        entity_id=str(post.id),
    )

    images = db.query(ImageRecord).all()

    ranked: list[RankedImageResult] = []

    for image in images:
        if not image.embedding:
            continue

        score = cosine_similarity(
            post_vector,
            image.embedding,
        )

        candidate = MatchCandidate(
            image_id=str(image.id),
            subject=image.subject,
            category=image.category,
            caption=image.caption,
            confidence=image.confidence,
            similarity_score=score,
        )

        guard = evaluate_candidate(
            candidate=candidate,
            expected_subject=post.expected_subject,
            expected_category=post.expected_category,
        )

        ranked.append(
            RankedImageResult(
                candidate=candidate,
                guard=guard,
            )
        )

    ranked.sort(
        key=lambda item: item.candidate.similarity_score,
        reverse=True,
    )

    return ranked