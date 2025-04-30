# 🔍⁉️ Flavius MCP Server

## 🌟 Overview

A Model Context Protocol (MCP) server implementation that provides database interaction and allows graph exploration capabilities through Flavius. This server enables running Cypher graph queries, analyzing complex domain data, and automatically generating business insights that can be enhanced with Claude's analysis.

## 🧩 Components

### 🛠️ Tools

The server offers these core tools:

#### 📊 Query Tools

* `read-flavius-cypher`  
   * Execute Cypher read queries to read data from the database  
   * Input:  
         * `query` (string): The Cypher query to execute  
         * `namespace` (string): The namespace  
         * `graph` (string): The graph name  
         * `params` (dictionary, optional): Parameters to pass to the Cypher query  
   * Returns: Query results as JSON serialized array of objects
* `write-flavius-cypher`  
   * Execute updating Cypher queries  
   * Input:  
         * `query` (string): The Cypher update query  
         * `namespace` (string): The namespace  
         * `graph` (string): The graph name  
         * `params` (dictionary, optional): Parameters to pass to the Cypher query  
   * Returns: A JSON serialized result with status and result information

#### 🕸️ Schema Tools

* `get-flavius-schema`  
   * Get a list of all namespaces, graphs, vertices and edges in the database  
   * No input required  
   * Returns: JSON serialized schema information

## 🔧 Usage with Claude Desktop

Add the server to your local `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flavius": {
      "command": "uvx",
      "args": ["mcp-flavius-cypher@0.1.0"],
      "env": {
        "FLAVIUS_HOST": "localhost",
        "FLAVIUS_PORT": "30000"
      }
    }
  }
}
```

## 🚀 Development

### 📦 Prerequisites

1. Install `uv` (Universal Virtualenv):

```bash
# Using pip
pip install uv
```

2. Set up development environment:

```bash
# Create and activate virtual environment using uv
uv venv
source .venv/bin/activate  # On Unix/macOS

# Install dependencies including dev dependencies
uv pip install -e ".[dev]"

# Generate uv.lock file (optional, but recommended for production)
uv pip compile pyproject.toml -o uv.lock
```

3. Run Integration Tests

```bash
./test.sh
```

### 📦 Dependencies

The project uses `pyproject.toml` for dependency management. Main dependencies include:

- `flavius>=0.1.0`: The Flavius graph database client
- `mcp>=0.1.0`: The Model Context Protocol implementation
- `pydantic>=2.0.0`: For data validation and settings management

Development dependencies (installed with `[dev]` extra):
- `pytest>=7.0.0`: For running tests
- `pytest-asyncio>=0.21.0`: For async test support

## 📄 License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository. 