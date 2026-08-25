from app.schemas.matching import MatchCandidate
from app.services.mismatch_guard import (
    evaluate_candidate,
)


def test_red_fox_candidate_is_accepted():
    candidate = MatchCandidate(
        image_id="fox.jpg",
        subject="Red fox",
        category="animal",
        caption="A red fox in a forest.",
        confidence=0.98,
        similarity_score=0.91,
    )

    decision = evaluate_candidate(
        candidate=candidate,
        expected_subject="red fox",
        expected_category="animal",
    )

    assert decision.accepted is True


def test_wolf_is_rejected_for_fox_post():
    candidate = MatchCandidate(
        image_id="wolf.jpg",
        subject="Gray wolf",
        category="animal",
        caption="A gray wolf in a forest.",
        confidence=0.99,
        similarity_score=0.89,
    )

    decision = evaluate_candidate(
        candidate=candidate,
        expected_subject="red fox",
        expected_category="animal",
    )

    assert decision.accepted is False
    assert "Subject mismatch" in decision.reason


def test_low_similarity_candidate_is_rejected():
    candidate = MatchCandidate(
        image_id="dog.jpg",
        subject="dog",
        category="animal",
        caption="A domestic dog outdoors.",
        confidence=0.99,
        similarity_score=0.30,
    )

    decision = evaluate_candidate(
        candidate=candidate,
        expected_subject="red fox",
        expected_category="animal",
    )

    assert decision.accepted is False
    assert "similarity" in decision.reason.lower()


def test_low_confidence_candidate_is_rejected():
    candidate = MatchCandidate(
        image_id="unclear.jpg",
        subject="unknown animal",
        category="animal",
        caption="An unclear animal.",
        confidence=0.41,
        similarity_score=0.90,
    )

    decision = evaluate_candidate(
        candidate=candidate,
        expected_subject="red fox",
        expected_category="animal",
    )

    assert decision.accepted is False
    assert "confidence" in decision.reason.lower()