# Agent Tool Registry

> Register tools. Let agents find them. Done.

Built this because I was constantly copy-pasting tool definitions between projects. Now I just register once and import everywhere.

## Install

```bash
pip install agent-tool-registry
```

Requires Python 3.9+, Pydantic 2.0+.

## What It Does

1. Register Python functions as tools with metadata
2. Let agents discover tools by name, tags, or description
3. Auto-generate OpenAI-compatible schemas for LLM tool calling
4. Validate inputs so bad data never reaches your functions

## Register a Tool

```python
from agent_tool_registry import ToolRegistry

registry = ToolRegistry()

@registry.tool(
    name="web.search",
    description="Search the web for information",
    tags=["search", "web"]
)
def web_search(query: str, max_results: int = 10) -> list[str]:
    # Your implementation here
    return ["https://example.com/result1"]
```

## Use It

```python
# Find tools
results = registry.find_tools("web.*")
results = registry.find_by_tags(["search"])
results = registry.search("internet")

# Execute
result = registry.execute("web.search", {"query": "Python tutorials"})
```

## Get LLM Schemas

```python
# Single tool
schema = registry.get_openai_schema("web.search")

# All tools
schemas = registry.get_all_openai_schemas()
# Returns list of OpenAI function-calling compatible schemas
```

The schema looks like:

```json
{
  "type": "function",
  "function": {
    "name": "web.search",
    "description": "Search the web for information",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string"},
        "max_results": {"type": "integer", "default": 10}
      },
      "required": ["query"]
    }
  }
}
```

## Namespaces

Organize tools by category:

```python
web = registry.namespace("web")
db = registry.namespace("db")

@web.tool(name="search", ...)
def web_search(...): ...

@db.tool(name="query", ...)
def db_query(...): ...

# Full names: "web.search", "db.query"
```

## Validation

Inputs are validated with Pydantic before hitting your function:

```python
@registry.tool(name="add", description="Add two numbers")
def add(x: int, y: int) -> int:
    return x + y

# This works
registry.execute("add", {"x": 1, "y": 2})

# This raises ToolValidationError
registry.execute("add", {"x": "oops", "y": 2})
```

## Real-World Example

```python
from agent_tool_registry import ToolRegistry

registry = ToolRegistry()

@registry.tool(
    name="file.read",
    description="Read contents of a file",
    tags=["file", "io"]
)
def read_file(path: str, encoding: str = "utf-8") -> str:
    with open(path, "r", encoding=encoding) as f:
        return f.read()

@registry.tool(
    name="file.write",
    description="Write content to a file"
)
def write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)

# Use with OpenAI
schemas = registry.get_all_openai_schemas()
# Pass to your LLM
```

## Why Not Just Use Dictionaries?

You can. But:

- Automatic schema generation from function signatures
- Input validation out of the box
- Tag-based discovery
- Namespace support
- Consistent interface across projects

## API

```python
registry = ToolRegistry()

# Register
@registry.tool(name="...", description="...", tags=[...])
def my_tool(...): ...

registry.register(fn, name="...", description="...", tags=[...])

# Discover
registry.find_tools("pattern")     # glob match
registry.find_by_tags(["tag1"])   # tools with these tags
registry.search("description")     # search descriptions

# Execute
registry.execute("tool.name", {"param": "value"})

# Schema
registry.get_openai_schema("tool.name")
registry.get_all_openai_schemas()

# Sub-registry
web = registry.namespace("web")
```

## License

MIT
