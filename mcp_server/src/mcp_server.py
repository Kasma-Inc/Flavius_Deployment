import json
import logging
import re
import sys
import time
from typing import Any, Optional

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from flavius import Client, GraphDatabase
from pydantic import Field

logger = logging.getLogger("mcp_flavius_cypher")


def healthcheck(host: str, port: int) -> None:
    """
    Verify that the Flavius server is running
    """
    print("Verifying Flavius server is running...", file=sys.stderr)
    attempts = 0
    success = False
    print("\nWaiting for Flavius server to start...\n", file=sys.stderr)
    time.sleep(3)
    ex = Exception()
    
    while not success and attempts < 3:
        try:
            driver = GraphDatabase.driver(f"http://{host}:{port}")
            driver.verify_connectivity()
            driver.close()
            success = True
        except Exception as e:
            ex = e
            attempts += 1
            print(
                f"Connection failed {attempts} | Waiting {(1 + attempts) * 2} seconds...",
                file=sys.stderr,
            )
            print(f"Error: {e}", file=sys.stderr)
            time.sleep((1 + attempts) * 2)
    
    if not success:
        raise ex


def create_mcp_server(host: str, port: int) -> FastMCP:
    mcp: FastMCP = FastMCP("mcp-flavius-cypher", dependencies=["flavius", "pydantic"])

    async def get_flavius_schema() -> list[types.TextContent]:
        """Get the schema information of the Flavius database"""
        try:
            driver = GraphDatabase.driver(f"http://{host}:{port}")
            schema = {}
            
            # Get all namespaces
            for namespace in driver.list_namespace():
                schema[namespace] = {}
                
                # Get graphs under each namespace
                for graph in driver.list_graph(namespace):
                    schema[namespace][graph] = {
                        "vertices": driver.list_vertex(namespace, graph),
                        "edges": driver.list_edge(namespace, graph)
                    }
            
            driver.close()
            return [types.TextContent(type="text", text=json.dumps(schema, indent=2))]

        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return [types.TextContent(type="text", text=f"Error: {e}")]

    async def read_flavius_cypher(
        query: str = Field(..., description="The Cypher query to execute"),
        namespace: str = Field(..., description="The namespace"),
        graph: str = Field(..., description="The graph name"),
        params: Optional[dict[str, Any]] = Field(
            None, description="Parameters to pass to the Cypher query"
        ),
    ) -> list[types.TextContent]:
        """Execute a read Cypher query on the Flavius database"""
        if _is_write_query(query):
            raise ValueError("Only MATCH queries are allowed for read operations")

        try:
            driver = GraphDatabase.driver(f"http://{host}:{port}")
            records, keys = driver.execute_query(query, namespace=namespace, graph=graph, parameters=params)
            
            # Convert results to JSON format
            results = []
            for record in records:
                result = {}
                for key in keys:
                    result[key] = record[key]
                results.append(result)
            
            driver.close()
            return [types.TextContent(type="text", text=json.dumps(results, default=str))]

        except Exception as e:
            logger.error(f"Error executing query: {e}\n{query}\n{params}")
            return [types.TextContent(type="text", text=f"Error: {e}\n{query}\n{params}")]

    async def write_flavius_cypher(
        query: str = Field(..., description="The Cypher query to execute"),
        namespace: str = Field(..., description="The namespace"),
        graph: str = Field(..., description="The graph name"),
        params: Optional[dict[str, Any]] = Field(
            None, description="Parameters to pass to the Cypher query"
        ),
    ) -> list[types.TextContent]:
        """Execute a write Cypher query on the Flavius database"""
        if not _is_write_query(query):
            raise ValueError("Only write queries are allowed for write operations")

        try:
            driver = GraphDatabase.driver(f"http://{host}:{port}")
            result = driver.execute_query(query, namespace=namespace, graph=graph, parameters=params)
            driver.close()
            
            return [types.TextContent(type="text", text=json.dumps({"status": "success", "result": result}, default=str))]

        except Exception as e:
            logger.error(f"Error executing query: {e}\n{query}\n{params}")
            return [types.TextContent(type="text", text=f"Error: {e}\n{query}\n{params}")]

    mcp.add_tool(get_flavius_schema)
    mcp.add_tool(read_flavius_cypher)
    mcp.add_tool(write_flavius_cypher)

    return mcp


def _is_write_query(query: str) -> bool:
    """Check if the query is a write query"""
    return (
        re.search(r"\b(CREATE|SET|DELETE|REMOVE|MERGE|DROP)\b", query, re.IGNORECASE)
        is not None
    )


def main(host: str = "localhost", port: int = 30000) -> None:
    logger.info("Starting Flavius MCP server")

    mcp = create_mcp_server(host, port)

    healthcheck(host, port)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main() 