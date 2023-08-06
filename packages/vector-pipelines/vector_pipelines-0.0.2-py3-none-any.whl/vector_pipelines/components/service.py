from __future__ import annotations

from concurrent import futures
from typing import Any

import grpc


class Serviceable:
    """Base class for components that can be served as gRPC services."""

    def add_services(self, server: grpc.Server) -> None:
        """Add servicers to the gRPC server.

        Args:
            server: The gRPC server to add servicers to.
        """
        raise NotImplementedError

    def serve(self, port: int = 50051, max_workers: int = 10) -> None:
        """Serve the component as a gRPC service.

        Args:
            port: The port to serve the component on.
            max_workers: The maximum number of workers to use for the gRPC server.
        """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self.add_services(server)
        print(f"Starting server on port {port}")
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        server.wait_for_termination()


class ServiceClient:
    """Base class for clients of gRPC services."""

    def __init__(self, host: str, port: int) -> None:
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = self.get_stub()

    def get_stub(self) -> Any:
        raise NotImplementedError
