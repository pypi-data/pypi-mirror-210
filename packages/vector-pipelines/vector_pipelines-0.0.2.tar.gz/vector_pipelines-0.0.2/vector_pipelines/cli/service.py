from __future__ import annotations

import typer

from vector_pipelines.components.config import ComponentServiceConfig

app = typer.Typer()


@app.command()
def start() -> None:
    """Starts a service for serving a component."""
    component_service_config = ComponentServiceConfig()  # type: ignore
    component = component_service_config.instantiate_component()
    component.serve()
