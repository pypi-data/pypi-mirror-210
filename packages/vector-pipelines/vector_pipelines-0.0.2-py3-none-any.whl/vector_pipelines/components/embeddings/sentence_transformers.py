from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from vector_pipelines.components.embeddings.base import Embeddings
from vector_pipelines.components.init import initialized


class SentenceTransformersEmbeddingsConfig(BaseModel):
    """The configuration for the `SentenceTransformersEmbeddings` class.

    Attributes:
        model_name_or_path: The name of the model to use or the path to a directory
            containing a model.
        device: The device to use for the model. If `cpu`, the CPU will be used. If
            `cuda`, the GPU will be used. If `cuda:X`, the GPU with index `X` will be
            used. Defaults to `cpu`.
        normalize_embeddings: Whether to normalize the embeddings or not. Defaults to
            `False`.
    """

    component_name: Literal["sentence_transformers_embeddings"] = (
        "sentence_transformers_embeddings"
    )
    import_path = "vector_pipelines.components.embeddings.sentence_transformers.SentenceTransformersEmbeddings"

    model_name_or_path: str
    device: str = "cpu"
    normalize_embeddings: bool = False


class SentenceTransformersEmbeddings(Embeddings):
    """A wrapper for the `sentence-transformers` library to generate embeddings.

    Attributes:
        config: the configuration for the Sentence Transformers model.
        model: The Sentence Transformers model.
    """

    config: SentenceTransformersEmbeddingsConfig
    model: Union[SentenceTransformer, None] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.config = SentenceTransformersEmbeddingsConfig(**kwargs)

    def init(self) -> None:
        self.model = SentenceTransformer(
            model_name_or_path=self.config.model_name_or_path, device=self.config.device
        )
        super().init()

    @initialized
    def encode(self, data: str | list[str]) -> list[list[int | float]]:
        if isinstance(data, str):
            data = [data]
        embeddings: list[list[int | float]] = self.model.encode(sentences=data).tolist()  # type: ignore
        return embeddings

    @property
    @initialized
    def vector_size(self) -> int:
        embedding_size: int = self.model.get_sentence_embedding_dimension()  # type: ignore
        return embedding_size


if __name__ == "__main__":
    import sys

    module = sys.modules[__name__]
    package_name = module.__package__
    print(f"{package_name}.ServiceSettings")
