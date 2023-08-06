from __future__ import annotations

import typer

from vector_pipelines.cli import service

app = typer.Typer(name="Vector Pipelines CLI")
app.add_typer(service.app, name="service", help="Commands for serving components.")
