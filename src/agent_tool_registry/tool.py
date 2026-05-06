"""Tool definition and metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from inspect import signature, Parameter
from pydantic import BaseModel, create_model


@dataclass
class ToolMetadata:
    """Metadata for a tool."""

    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)
    rate_limit: Optional[int] = None  # calls per minute
    timeout: Optional[int] = None  # seconds
    requires_auth: bool = False
    namespace: Optional[str] = None


class Tool:
    """A registered tool."""

    def __init__(
        self,
        fn: Callable[..., Any],
        metadata: ToolMetadata,
    ) -> None:
        self.fn = fn
        self.metadata = metadata
        self._input_model = self._create_input_model()

    def _create_input_model(self) -> type[BaseModel]:
        """Create a Pydantic model for input validation."""
        sig = signature(self.fn)
        fields: dict[str, tuple[type, Any]] = {}

        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue

            # Get type annotation
            param_type = param.annotation
            if param_type is Parameter.empty:
                param_type = Any

            # Get default value
            if param.default is Parameter.empty:
                fields[param_name] = (param_type, ...)
            else:
                fields[param_name] = (param_type, param.default)

        return create_model(f"{self.metadata.name}_input", **fields)

    def validate_input(self, params: dict[str, Any]) -> dict[str, Any]:
        """Validate input parameters."""
        validated = self._input_model(**params)
        return validated.model_dump()

    def execute(self, params: dict[str, Any]) -> Any:
        """Execute the tool with validated parameters."""
        validated = self.validate_input(params)
        return self.fn(**validated)

    def get_openai_schema(self) -> dict[str, Any]:
        """Get OpenAI-compatible function schema."""
        schema = self._input_model.model_json_schema()
        # Remove title from schema
        if "title" in schema:
            del schema["title"]
        if "properties" in schema:
            for prop in schema["properties"].values():
                if "title" in prop:
                    del prop["title"]

        return {
            "type": "function",
            "function": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "parameters": schema,
            },
        }
