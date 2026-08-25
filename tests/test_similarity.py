import pytest

from app.services.similarity import cosine_similarity


def test_identical_vectors_have_similarity_one():
    result = cosine_similarity(
        [1.0, 2.0, 3.0],
        [1.0, 2.0, 3.0],
    )

    assert result == pytest.approx(1.0)


def test_opposite_vectors_have_negative_similarity():
    result = cosine_similarity(
        [1.0, 0.0],
        [-1.0, 0.0],
    )

    assert result == pytest.approx(-1.0)


def test_zero_vector_returns_zero():
    result = cosine_similarity(
        [0.0, 0.0],
        [1.0, 2.0],
    )

    assert result == 0.0