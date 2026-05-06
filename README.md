<div align="center">

# 🔧 Agent Tool Registry

**Register tools. Let agents find them. Done.**

[![PyPI](https://img.shields.io/pypi/v/agent-tool-registry?color=blue)](https://pypi.org/project/agent-tool-registry/)
[![Python](https://img.shields.io/pypi/pyversions/agent-tool-registry)](https://pypi.org/project/agent-tool-registry/)
[![License](https://img.shields.io/github/license/PHclaw/agent-tool-registry)](LICENSE)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-green)](https://pypi.org/project/pydantic/)

</div>

---

Built this because I was constantly copy-pasting tool definitions between projects. Now I register once and import everywhere.

## ✨ What It Does

1. 📝 **Register** Python functions as tools with metadata
2. 🔍 **Discover** tools by name, tags, or description
3. ✅ **Validate** inputs automatically — bad data never reaches your functions
4. 🤖 **Generate** OpenAI-compatible schemas for LLM tool calling

## 📦 Install

```bash
pip install agent-tool-registry
```

> Requires Python 3.9+, Pydantic 2.0+

## 🚀 Quick Example

```python
from agent_tool_registry import ToolRegistry

registry = ToolRegistry()

@registry.tool(
    name="web.search",
    description="Search the web for information",
    tags=["search", "web"]
)
def web_search(query: str, max_results: int = 10) -> list[str]:
    return ["https://example.com/result1"]

# Find tools
registry.find_tools("web.*")     # → [Tool("web.search")]
registry.find_by_tags(["search"]) # → [Tool("web.search")]

# Execute
result = registry.execute("web.search", {"query": "Python tutorials"})
```

---

## 🤖 LLM Integration

Get OpenAI-compatible schemas for tool calling:

```python
# Single tool
schema = registry.get_openai_schema("web.search")

# All tools at once — pass directly to your LLM
schemas = registry.get_all_openai_schemas()
```

Generated schema:

```json
{
  "type": "function",
  "function": {
    "name": "web.search",
    "description": "Search the web for information",
    "parameters": {
      "type": "object",
      "properties": {
        "query": { "type": "string" },
        "max_results": { "type": "integer", "default": 10 }
      },
      "required": ["query"]
    }
  }
}
```

## 📂 Namespaces

Organize tools by category:

```python
web = registry.namespace("web")
db  = registry.namespace("db")

@web.tool(name="search", description="Search the web")
def search(q: str) -> list[str]: ...

@db.tool(name="query", description="Run SQL query")
def query(sql: str) -> list[dict]: ...

# Full names: "web.search", "db.query"
```

## ✅ Input Validation

Inputs are validated with Pydantic before hitting your function:

```python
@registry.tool(name="add", description="Add two numbers")
def add(x: int, y: int) -> int:
    return x + y

registry.execute("add", {"x": 1, "y": 2})  # → 3 ✅
registry.execute("add", {"x": "oops", "y": 2})  # → ToolValidationError ❌
```

---

## 🔍 Discovery

| Method | What It Does |
|---|---|
| `find_tools("web.*")` | Glob match on tool names |
| `find_by_tags(["search"])` | Find tools with specific tags |
| `search("database")` | Full-text search on descriptions |
| `list_tools()` | Get everything |

---

## 📖 API

### Register

```python
# Decorator style
@registry.tool(name="...", description="...", tags=[...])
def my_tool(...): ...

# Explicit style
registry.register(fn, name="...", description="...", tags=[...])
```

### Execute

```python
registry.execute("tool.name", {"param": "value"})
```

### Schema

```python
registry.get_openai_schema("tool.name")
registry.get_all_openai_schemas()
```

### Namespace

```python
web = registry.namespace("web")
```

---

## 💡 Why Not Just Use Dicts?

You can. But with this you also get:

- Automatic schema generation from function signatures
- Input validation out of the box
- Tag-based discovery
- Namespace support
- Consistent interface across projects

---

## 📄 License

[MIT](LICENSE) — do whatever you want with it.
