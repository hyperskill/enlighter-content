# Building an MCP Server with Python & UV

## What Is MCP?

Model Context Protocol (MCP) is a **client-server protocol** that lets host applications (IDEs, chats, desktop assistants) stream **context, prompts, tools, and resources** to language models.

| Term       | Role                                                 |
| ---------- | ---------------------------------------------------- |
| **Host**   | End-user app (e.g. Claude Desktop, VS Code)          |
| **Client** | 1-per-connection wrapper inside the host             |
| **Server** | Python process you write; supplies prompts/resources |

## Message & Error Basics

Every request/response is JSON-RPC 2.0. Standard error codes:

| Error Code      | Value   |
| --------------- | ------- |
| ParseError      | -32700  |
| InvalidRequest  | -32600  |
| MethodNotFound  | -32601  |
| InvalidParams   | -32602  |
| InternalError   | -32603  |

## Project Setup with UV/UVX

```bash
mkdir my-mcp-srv && cd $_
uv init                 # pyproject.toml + venv
uv add mcp              # install python-mcp package
```

`uv init` command creates a default project and sets up the necessary structure to manage your Python dependencies, it includes:

my_project/
│
├── pyproject.toml      # Main config file for dependencies and settings
├── README.md           # Project description and documentation 
└── src/                # Main source code directory
    └── __init__.py     # Initializes src as a Python package

## Server Example

Create `src/server.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo")


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"


@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"


@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"


def main():
    """Entry point for the application when run with uvx."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
```

Add an entry-point in `pyproject.toml` so `uvx` can find it:

```toml
[project.scripts]
server = "server:main"
```

Run it:

```bash
uvx --from . server
```

## Prompts

Prompts are **reusable templates** exposed by the server and surfaced by the client (slash commands, buttons, etc.).

```python
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
```

A client calls `prompts/get` with arguments; you return a list of `PromptMessage` objects (role+content) that will feed the LLM.

## Resources

Resources expose **files, logs, API data** to the model.

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Dynamic user data"""
    return f"Profile data for user {user_id}"
```

* URI scheme is arbitrary; just keep it stable.
* Use `resources/subscribe` + `notifications/resources/updated` for live data.

### Run MCP Server with UV

Use `--from` option to run from alternative sources:

`uvx --from path_to_package your_package_name` where `your_package_name` is defined in pyproject.toml

## Run MCP Server from GitHub with uv

`uvx --from git+https://github.com/username/you_repo_name your_package_name`

## Debugging & Inspector

```bash
npx @modelcontextprotocol/inspector uvx --directory . server
```

## Set Up to a Client

Create `mcp.json` next to the host app config:

```json
{
  "mcpServers": {
    "demo": {
      "command": "uvx",
      "args": ["--from", "/abs/path/to/my-mcp-srv", "server"]
    }
  }
}
```

## Full Docs

* MCP Spec & examples: https://modelcontextprotocol.io/llms.txt
* Inspector: https://modelcontextprotocol.io/docs/tools/inspector.md
* UV package manager: https://context7.com/astral-sh/uv/llms.txt
