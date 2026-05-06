"""Error types for Agent Tool Registry."""


class ToolNotFoundError(Exception):
    """Raised when a tool is not found."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Tool not found: {name}")


class ToolValidationError(Exception):
    """Raised when tool input validation fails."""

    def __init__(self, name: str, errors: list[str]) -> None:
        self.name = name
        self.errors = errors
        super().__init__(f"Validation failed for {name}: {errors}")


class ToolExecutionError(Exception):
    """Raised when tool execution fails."""

    def __init__(self, name: str, cause: Exception) -> None:
        self.name = name
        self.cause = cause
        super().__init__(f"Execution failed for {name}: {cause}")
