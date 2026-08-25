from app.core.config import settings
from app.schemas.matching import (
    GuardDecision,
    MatchCandidate,
)


def normalize_subject(value: str) -> str:
    return value.strip().lower()


def subject_matches(
    expected_subject: str,
    detected_subject: str,
) -> bool:
    expected = normalize_subject(expected_subject)
    detected = normalize_subject(detected_subject)

    if expected in detected:
        return True

    if detected in expected:
        return True

    aliases = {
    "red fox": {
        "fox",
        "red fox",
        "vulpes vulpes",
    },
    "wolf": {
        "wolf",
        "gray wolf",
        "grey wolf",
        "canis lupus",
    },
    "dog": {
        "dog",
        "domestic dog",
        "golden retriever",
        "retriever",
        "canis familiaris",
        "canis lupus familiaris",
    },
    "cattle": {
        "cattle",
        "cow",
        "cows",
        "calf",
        "cattle on a hillside",
        "cattle on a grassy hillside",
    },
    "lion": {
        "lion",
        "male lion",
        "african lion",
        "panthera leo",
    },
}
    for canonical, values in aliases.items():
        all_values = values | {canonical}

        if (
            expected in all_values
            and detected in all_values
        ):
            return True

    return False


def evaluate_candidate(
    *,
    candidate: MatchCandidate,
    expected_subject: str,
    expected_category: str,
) -> GuardDecision:

    if (
        candidate.confidence
        < settings.vision_confidence_threshold
    ):
        return GuardDecision(
            accepted=False,
            reason=(
                "Image classification confidence "
                "is below the required threshold."
            ),
        )

    if (
        candidate.similarity_score
        < settings.similarity_threshold
    ):
        return GuardDecision(
            accepted=False,
            reason=(
                "Semantic similarity is below "
                "the required threshold."
            ),
        )

    if (
        candidate.category.strip().lower()
        != expected_category.strip().lower()
    ):
        return GuardDecision(
            accepted=False,
            reason=(
                "Category mismatch: "
                f"expected {expected_category}, "
                f"detected {candidate.category}."
            ),
        )

    if not subject_matches(
        expected_subject,
        candidate.subject,
    ):
        return GuardDecision(
            accepted=False,
            reason=(
                "Subject mismatch: "
                f"expected {expected_subject}, "
                f"detected {candidate.subject}."
            ),
        )

    return GuardDecision(
        accepted=True,
        reason="Candidate passed mismatch guard.",
    )