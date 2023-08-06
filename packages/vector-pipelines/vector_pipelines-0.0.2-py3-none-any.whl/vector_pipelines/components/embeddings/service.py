from __future__ import annotations

from typing import TYPE_CHECKING, Any

import dill as pickle
from pydantic import BaseModel

from vector_pipelines.components.service import ServiceClient
from vector_pipelines.grpc import embeddings_pb2, embeddings_pb2_grpc

if TYPE_CHECKING:
    from grpc import ServicerContext

    from vector_pipelines.components.embeddings.base import Embeddings


class EmbeddingsService(embeddings_pb2_grpc.EmbeddingServiceServicer):
    """Base class for serving a model for embedding generation.

    Attributes:
        embeddings: The embeddings model to serve.
    """

    embeddings: Embeddings

    def __init__(self, embeddings: Embeddings) -> None:
        self.embeddings = embeddings

    def GenerateEmbeddings(
        self, request: embeddings_pb2.EmbeddingRequest, context: ServicerContext
    ) -> embeddings_pb2.EmbeddingResponse:
        data = pickle.loads(request.data)
        embeddings = self.embeddings.encode(data=data)
        bytes_ = pickle.dumps(embeddings)
        return embeddings_pb2.EmbeddingResponse(embeddings=bytes_)

    def GetEmbeddingInfo(
        self, request: embeddings_pb2.EmbeddingInfoRequest, context: ServicerContext
    ) -> embeddings_pb2.EmbeddingInfoResponse:
        """Get information about the embeddings model."""
        return embeddings_pb2.EmbeddingInfoResponse(
            vector_size=self.embeddings.vector_size,
        )


class EmbeddingsInfo(BaseModel):
    vector_size: int


class EmbeddingsServiceClient(ServiceClient):
    """A client for the embeddings service."""

    def get_stub(self) -> embeddings_pb2_grpc.EmbeddingServiceStub:
        return embeddings_pb2_grpc.EmbeddingServiceStub(self.channel)  # type: ignore

    def generate_embeddings(self, data: Any | list[Any]) -> list[list[int | float]]:
        bytes_in = pickle.dumps(data)
        bytes_out = self.stub.GenerateEmbeddings(
            embeddings_pb2.EmbeddingRequest(data=bytes_in)
        )
        embeddings: list[list[int | float]] = pickle.loads(bytes_out.embeddings)
        return embeddings

    def get_embeddings_info(self) -> EmbeddingsInfo:
        response = self.stub.GetEmbeddingInfo(embeddings_pb2.EmbeddingInfoRequest())
        return EmbeddingsInfo(vector_size=response.vector_size)
