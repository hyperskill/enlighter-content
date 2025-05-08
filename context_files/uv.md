# UV package manager 

### Initializing

Initialize the Project with uv: In your project folder, initialize the project with `uv init`
This command creates a default project and sets up the necessary structure to manage your Python dependencies, it includes:

my_project/
│
├── pyproject.toml      # Main config file for dependencies and settings
├── README.md           # Project description and documentation 
└── src/                # Main source code directory
    └── __init__.py     # Initializes src as a Python package


### Add Your First Package

With your project initialized, you can now add packages. Add mcp package:

`uv add mcp`

### Installing from an existing .toml file

If you have an existing project with a .toml file you can install dependencies by running:

`uv sync`

This command installs or updates all dependencies specified in the pyproject.toml and uv.lock files into the project's virtual environment, ensuring your environment matches the declared dependencies.

### Run MCP Server

`uvx --from path_to_package your_package_name` where `your_package_name` is defined in pyproject.toml

### Setup MCP Server

Add to your MCP config file (i.e. `mcp.json`) following configuration: 

```json
{
  "mcpServers": {
    "mcp-memory-bank": {
      "command": "uvx",
      "args": [
        "--from",
        "path_to_package",
        "your_package_name"
      ]
    }
  }
}
```
