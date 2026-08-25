import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.image import ImageRecord
from app.models.post import Post
from app.services.embedding_service import EmbeddingService
from app.services.similarity import cosine_similarity
from app.services.mismatch_guard import subject_matches


EVAL_FILE = Path("data/eval_set.json")


def run_evaluation(db: Session) -> dict:
    if not EVAL_FILE.exists():
        return {
            "total": 0,
            "correct": 0,
            "top_1_precision": 0.0,
            "results": [],
        }

    cases = json.loads(
        EVAL_FILE.read_text(encoding="utf-8")
    )

    embedding_service = EmbeddingService()
    images = db.query(ImageRecord).all()

    results = []
    correct = 0

    for case in cases:
        post_vector = embedding_service.embed_text(
            case["post"],
            entity_type="eval_post",
            entity_id=case["expected_subject"],
        )

        ranked = []

        for image in images:
            if not image.embedding:
                continue

            score = cosine_similarity(
                post_vector,
                image.embedding,
            )

            ranked.append(
                {
                    "image_id": image.id,
                    "subject": image.subject,
                    "score": score,
                }
            )

        ranked.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        top = ranked[0] if ranked else None

        is_correct = bool(
            top
            and subject_matches(
                case["expected_subject"],
                top["subject"],
            )
        )

        if is_correct:
            correct += 1

        results.append(
            {
                "post": case["post"],
                "expected_subject": case["expected_subject"],
                "top_result": top,
                "correct": is_correct,
            }
        )

    total = len(cases)

    precision = (
        correct / total
        if total
        else 0.0
    )

    return {
        "total": total,
        "correct": correct,
        "top_1_precision": round(
            precision,
            4,
        ),
        "results": results,
    }