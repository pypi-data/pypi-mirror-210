from __future__ import annotations

import pytest

from vector_pipelines.components.embeddings.sentence_transformers import (
    SentenceTransformersEmbeddings,
)


@pytest.fixture(name="sentence_transformers_embeddings", scope="module")
def sentence_transformers_embeddings_fixture() -> SentenceTransformersEmbeddings:
    embeddings = SentenceTransformersEmbeddings(
        model_name_or_path="all-MiniLM-L6-v2", device="cpu"
    )
    embeddings.init()
    return embeddings


def test_sentence_transformers_embeddings_vector_size(
    sentence_transformers_embeddings: SentenceTransformersEmbeddings,
) -> None:
    """Test that the `vector_size` method returns the correct value."""
    assert sentence_transformers_embeddings.vector_size == 384


@pytest.mark.parametrize(
    "data, expected_list_len",
    [
        (["This is a sample text for testing purposes."], 1),
        (
            [
                "This is a sample text for testing purposes.",
                "This is another sample text for testing purposes.",
            ],
            2,
        ),
    ],
)
def test_sentence_transformers_embeddings_encode(
    data: list[str],
    expected_list_len: int,
    sentence_transformers_embeddings: SentenceTransformersEmbeddings,
) -> None:
    """Test that the `encode` method returns a vector when given a single text."""
    vectors = sentence_transformers_embeddings.encode(data)
    assert isinstance(vectors, list)
    assert len(vectors) == expected_list_len
    assert isinstance(vectors[0], list)
    assert len(vectors[0]) == 384
