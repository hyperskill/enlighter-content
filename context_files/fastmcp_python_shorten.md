# Building an MCP Server with Python & UV

---

## 1. What Is MCP?

Model Context Protocol (MCP) is a **client‑server protocol** that lets host applications (IDEs, chats, desktop assistants) stream **context, prompts, tools, and resources** to language models.
**Goal:** decouple “where the user works” (host) from “where the AI context lives” (server).

| Term       | Role                                                 |
| ---------- | ---------------------------------------------------- |
| **Host**   | End‑user app (e.g. Claude Desktop, VS Code)          |
| **Client** | 1‑per‑connection wrapper inside the host             |
| **Server** | Python process you write; supplies prompts/resources |

## 2. High‑Level Architecture

```text
┌───────────── Host App ─────────────┐
│  ┌─ Client #1 ─┐   ┌─ Client #2 ─┐ │
│  │ stdio / SSE │   │ stdio / SSE │ │
│  └─────────────┘   └─────────────┘ │
└──────────┬──────────────────┬──────┘
           ▼                  ▼
     Your MCP Server A   Your MCP Server B
```

*Transport layer* carries **JSON‑RPC 2.0** messages over **stdio** (local) or **HTTP + SSE** (remote).

## 3. Message & Error Basics

Every request/response is JSON‑RPC 2.0.  Standard error codes:

```ts
ParseError      = -32700
InvalidRequest  = -32600
MethodNotFound  = -32601
InvalidParams   = -32602
InternalError   = -32603
```

## 4. Project Setup with UV/UVX

```bash
mkdir my‑mcp‑srv && cd $_
uv init                 # pyproject.toml + venv
uv add mcp              # install python‑mcp package
```

> **Tip:** `uv` is a blazing‑fast package manager and runner. `uvx` launches console‑scripts from virtual envs.

## 5. Skeleton Server (copy‑paste)

Create `src/server.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("example-server")

@mcp.tool(
    annotations={
        "title": "Calculate Sum",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def calculate_sum(a: float, b: float) -> str:
    """Add two numbers together.
    
    Args:
        a: First number to add
        b: Second number to add
    """
    result = a + b
    return str(result)

@mcp.resource("test://{parameter}")
async def test_resource(parameter: str) -> tuple[str, str]:
    """Provides example resource
    
    Args:
        parameter: example parameter
    """
    return "Test resource"

def main():
    """Entry point for the application when run with uvx."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

Add an entry‑point in `pyproject.toml` so `uvx` can find it:

```toml
[project.scripts]
server = "server:main"
```

Run it:

```bash
uvx --from . server
```

## 6. Prompts 101

*Prompts* are **reusable templates** exposed by the server and surfaced by the client (slash commands, buttons, etc.).

```python
PROMPTS = {
    "git‑commit": t.Prompt(
        name="git‑commit",
        description="Generate a Git commit message",
        arguments=[t.PromptArgument(name="changes", required=True)]
    )
}

@app.list_prompts()
async def list_prompts():
    return list(PROMPTS.values())
```

A client calls `prompts/get` with arguments; you return a list of `PromptMessage` objects (role+content) that will feed the LLM.

## 7. Resources 101

Resources expose **files, logs, API data** to the model.

```python
@app.read_resource()
async def read_resource(uri: str):
    if uri == "demo://hello":
        return "Hello from MCP!"
    raise ValueError("Resource not found")
```

* URI scheme is arbitrary; just keep it stable.
* Use `resources/subscribe` + `notifications/resources/updated` for live data.

## 8. Transport Choice Cheat‑Sheet

| Scenario                                 | Transport               |
| ---------------------------------------- | ----------------------- |
| Same machine, quick dev                  | **stdio** (zero‑config) |
| Need HTTP compatibility or cross‑network | **HTTP + SSE**          |

Switch transports by swapping `stdio_server()` for `http_server(host, port)`.

## 9. Debugging & Inspector

```bash
npx @modelcontextprotocol/inspector uvx --directory . server
```

Opens a web UI showing every JSON‑RPC exchange, live logs, and lets you call endpoints manually.

## 10. Hooking Up to a Client

Create `mcp.json` next to the host app config:

```json
{
  "mcpServers": {
    "demo": {
      "command": "uvx",
      "args": ["--from", "/abs/path/to/my‑mcp‑srv", "server"]
    }
  }
}
```

Restart the host; the new server appears in its UI.

## 11. Best Practices

1. **Name things clearly** – prompts, URIs, errors.
2. **Validate params**; return `InvalidParams` if missing.
3. **Cache** expensive resource reads.
4. **Version** prompt templates when you change wording.
5. **Log** every request/response at `debug`; redact secrets.
6. **Unit‑test** endpoints with `asyncio` & `pytest`.

## 12. One‑Shot Prompt for LLM

> *“Read the attached MCP guide. Generate a complete Python package named `my_mcp_srv` that: (1) exposes a prompt `explain-code` taking `language` + `code`, (2) exposes a live log resource at `file:///tmp/app.log`, (3) runs over stdio.  Include `pyproject.toml`, `src/server.py`, and an entry‑point `server`.  Use uv for deps.”*

Copy the generated files into your project, run `uv sync && uvx --from . server`, and you have a working MCP server in seconds.

---

### Full Docs

* MCP Spec & examples: https://modelcontextprotocol.io/llms.txt
* Inspector: https://modelcontextprotocol.io/docs/tools/inspector.md
* UV package manager: https://context7.com/astral-sh/uv/llms.txt
