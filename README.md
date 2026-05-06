# Agent Tool Registry

A lightweight tool registry and discovery system for AI agents. Features:

- **Tool Registration**: Register Python functions as agent tools with automatic schema inference
- **Discovery**: Search and discover tools by name, tags, or capabilities
- **Validation**: Automatic input validation using Pydantic
- **Namespacing**: Organize tools by namespace (e.g., `web.search`, `file.read`)
- **Metadata**: Rich metadata including descriptions, examples, and rate limits

## Installation

```bash
pip install agent-tool-registry
```

## Quick Start

```python
from agent_tool_registry import ToolRegistry

# Create a registry
registry = ToolRegistry()

# Register a tool
@registry.tool(
    name="web.search",
    description="Search the web for information",
    tags=["web", "search", "internet"]
)
def web_search(query: str, max_results: int = 10) -> list[str]:
    """Search the web and return URLs."""
    # Implementation here
    return ["https://example.com/result1", "https://example.com/result2"]

# Discover tools
tools = registry.find_tools("search")
print(tools)
# [Tool(name="web.search", ...)]

# Execute a tool
result = registry.execute("web.search", {"query": "Python tutorials"})
print(result)
# ["https://example.com/result1", ...]
```

## Tool Registration

### Decorator Style

```python
@registry.tool(
    name="file.read",
    description="Read a file from disk",
    tags=["file", "io"],
    rate_limit=100,  # calls per minute
)
def read_file(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read()
```

### Explicit Registration

```python
def my_function(x: int, y: int) -> int:
    return x + y

registry.register(
    fn=my_function,
    name="math.add",
    description="Add two numbers",
    tags=["math", "arithmetic"],
)
```

## Tool Discovery

```python
# Find by name pattern
tools = registry.find_tools("web.*")

# Find by tags
tools = registry.find_by_tags(["search", "web"])

# Find by description keywords
tools = registry.search("read file")

# List all tools
all_tools = registry.list_tools()
```

## Tool Schemas

Get JSON schemas for LLM tool calling:

```python
# Get OpenAI-compatible schema
schema = registry.get_openai_schema("web.search")
print(schema)
# {
#   "type": "function",
#   "function": {
#     "name": "web.search",
#     "description": "Search the web for information",
#     "parameters": {...}
#   }
# }

# Get all tool schemas for an LLM
schemas = registry.get_all_openai_schemas()
```

## Namespaces

```python
# Create namespaced registries
web_registry = registry.namespace("web")
file_registry = registry.namespace("file")

# Register in namespace
@web_registry.tool(name="search", ...)
def search(...): ...

# Full name becomes "web.search"
```

## Validation

Tools are automatically validated using Pydantic:

```python
@registry.tool(name="calculate")
def calculate(x: int, y: int, operation: str = "add") -> int:
    ...

# This will raise ValidationError
registry.execute("calculate", {"x": "not a number", "y": 5})
```

## Tool Metadata

```python
@registry.tool(
    name="api.call",
    description="Call an external API",
    tags=["api", "http"],
    examples=[
        {"input": {"url": "https://api.example.com"}, "output": {"status": 200}}
    ],
    rate_limit=60,
    timeout=30,
    requires_auth=True,
)
def call_api(url: str, method: str = "GET") -> dict:
    ...
```

## API Reference

### ToolRegistry

- `tool(name, description, tags=None, ...)` - Decorator to register a tool
- `register(fn, name, description, ...)` - Explicit registration
- `execute(name, params)` - Execute a tool by name
- `find_tools(pattern)` - Find tools by name pattern
- `find_by_tags(tags)` - Find tools by tags
- `search(query)` - Search by description
- `list_tools()` - List all tools
- `get_tool(name)` - Get a specific tool
- `get_openai_schema(name)` - Get OpenAI-compatible schema
- `get_all_openai_schemas()` - Get all schemas
- `namespace(name)` - Create a namespaced sub-registry

## License

MIT
