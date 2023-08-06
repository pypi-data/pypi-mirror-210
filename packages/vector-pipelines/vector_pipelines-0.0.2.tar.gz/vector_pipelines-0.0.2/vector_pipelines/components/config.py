from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, BaseSettings, Field, PyObject, validator
from typing_extensions import Annotated

from vector_pipelines.components.embeddings.sentence_transformers import (
    SentenceTransformersEmbeddingsConfig,
)


class Dummy(BaseModel):
    component_name: Literal["dummy"]


ComponentConfig = Annotated[
    Union[SentenceTransformersEmbeddingsConfig, Dummy],
    Field(discriminator="component_name"),
]


class ComponentServiceConfig(BaseSettings):
    """Configuration for a service that serves a component.

    Attributes:
        component_config: The configuration for the component.
        component: The component to serve.
        component_port: The port to serve the component on.
    """

    component_config: ComponentConfig
    component: Union[PyObject, None] = None
    component_port: int = Field(50051, gt=0, le=65535)

    class Config:
        env_prefix = "VECTOR_PIPELINES_"
        case_sensitive = False

    @validator("component", pre=True)
    def build_component(cls, v: PyObject | None, values: dict[str, Any]) -> str:
        import_path: str = values["component_config"].import_path
        return import_path

    def instantiate_component(self) -> Any:
        return self.component(**self.component_config.dict())  # type: ignore
