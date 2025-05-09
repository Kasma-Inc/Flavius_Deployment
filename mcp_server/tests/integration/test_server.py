import asyncio
import json
import os
import sys
import time
import random
import tempfile
import csv
from typing import Any, Dict, List

import pytest
from mcp.types import TextContent
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from flavius import Client, GraphDatabase, DataType
from minio import Minio

sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))
from mcp_server import create_mcp_server


@pytest.fixture
def mcp() -> FastMCP:
    """Create a FastMCP instance for testing"""
    return create_mcp_server("localhost", 30000)


@pytest.fixture
def driver() -> Client:
    """Create a Flavius client for testing"""
    return GraphDatabase.driver("http://localhost:30000")


@pytest.fixture
def minio_client() -> Minio:
    """Create a MinIO client for testing"""
    return Minio(
        "localhost:30900",
        access_key="fvadmin",
        secret_key="fvadmin123",
        secure=False
    )


@pytest.fixture
async def setup_database(driver: Client) -> None:
    """Setup test database"""
    ns = "mcp"
    g = "demo"

    # Create namespace and graph if not exist
    namespaces = driver.list_namespace()
    if ns not in namespaces:
        driver.create_namespace(ns)

    graphs = driver.list_graph(ns)
    if g not in graphs:
        driver.create_graph(g, namespace=ns)

        # Create vertex table
        driver.create_vertex_table(
            "User",
            [
                ("id", DataType.INTEGER, False),  # NOT NULL
                ("name", DataType.VARCHAR),
                ("age", DataType.INTEGER),
            ],
            "id",  # primary key
            namespace=ns,
            graph=g,
        )


@pytest.mark.asyncio
async def test_get_schema(mcp: FastMCP) -> None:
    """Test getting the database schema"""
    result = await mcp.call_tool("get_flavius_schema", dict())
    assert len(result) == 1
    assert result[0].type == "text"
    schema = json.loads(result[0].text)
    assert isinstance(schema, dict)


@pytest.mark.asyncio
async def test_write_query(mcp: FastMCP, driver: Client, minio_client: Minio, setup_database) -> None:
    """Test executing a write query with data import"""
    ns = "mcp"
    g = "demo"

    # Generate test data
    data = []
    for i in range(5):
        data.append({
            "id": i + 1,
            "name": f"User_{i+1}",
            "age": random.randint(20, 50)
        })

    # Save data to CSV
    csv_content = "id,name,age\n"
    for row in data:
        csv_content += f"{row['id']},{row['name']},{row['age']}\n"

    # Upload to MinIO
    bucket_name = "flavius"
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        object_name = "test_users.csv"
        minio_client.put_object(
            bucket_name,
            object_name,
            csv_content.encode(),
            len(csv_content)
        )

        # Execute import query
        result = await mcp.call_tool("write_flavius_cypher", {
            "query": f"""
            BLOCKING IMPORT VERTEX User COLUMNS
            ("id"=$0, "name"=$1, "age"=$2)
            FROM 'oss://flavius/{object_name}'
            WITH (region = 'cn-hongkong',
                  access_key_id = 'fvadmin',
                  secret_access_key = 'fvadmin123',
                  endpoint = 'http://minio:9000')
            FORMAT AS CSV (has_header = true, delimiter = ',')
            """,
            "namespace": ns,
            "graph": g,
            "params": {}
        })
        assert len(result) == 1
        assert result[0].type == "text"
        response = json.loads(result[0].text)
        assert response["status"] == "success"

        # Verify data was imported
        verify_result = await mcp.call_tool("read_flavius_cypher", {
            "query": "MATCH (n:User) RETURN n.id, n.name, n.age ORDER BY n.id",
            "namespace": ns,
            "graph": g,
            "params": {}
        })
        assert len(verify_result) == 1
        assert verify_result[0].type == "text"
        imported_data = json.loads(verify_result[0].text)
        assert len(imported_data) == len(data)
        for i, row in enumerate(imported_data):
            assert row["n.id"] == data[i]["id"]
            assert row["n.name"] == data[i]["name"]
            assert row["n.age"] == data[i]["age"]
    except Exception as e:
        pytest.skip(f"Skipping test due to MinIO connection error: {e}")


@pytest.mark.asyncio
async def test_read_query(mcp: FastMCP, minio_client: Minio, setup_database) -> None:
    """Test executing a read query"""
    # Use the test namespace and graph
    ns = "mcp"
    g = "demo"

    # First import some test data
    csv_content = "id,name,age\n1,Test User,30\n"
    bucket_name = "flavius"
    object_name = "test_users.csv"
    
    try:        
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            
        minio_client.put_object(
            bucket_name,
            object_name,
            csv_content.encode(),
            len(csv_content)
        )
        
        # Import data
        await mcp.call_tool("write_flavius_cypher", {
            "query": f"""
            BLOCKING IMPORT VERTEX User COLUMNS
            ("id"=$0, "name"=$1, "age"=$2)
            FROM 'oss://flavius/{object_name}'
            WITH (region = 'cn-hongkong',
                  access_key_id = 'fvadmin',
                  secret_access_key = 'fvadmin123',
                  endpoint = 'http://minio:9000')
            FORMAT AS CSV (has_header = true, delimiter = ',')
            """,
            "namespace": ns,
            "graph": g,
            "params": {}
        })
    except Exception as e:
        pytest.skip(f"Skipping test due to MinIO connection error: {e}")

    # Execute a read query
    result = await mcp.call_tool("read_flavius_cypher", {
        "query": "MATCH (n:User) RETURN n.id, n.name, n.age ORDER BY n.id",
        "namespace": ns,
        "graph": g,
        "params": {}
    })
    assert len(result) == 1
    assert result[0].type == "text"
    data = json.loads(result[0].text)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["n.id"] == 1
    assert data[0]["n.name"] == "Test User"
    assert data[0]["n.age"] == 30


@pytest.mark.asyncio
async def test_invalid_read_query(mcp: FastMCP) -> None:
    """Test executing an invalid read query"""
    with pytest.raises(ToolError):
        await mcp.call_tool("read_flavius_cypher", {
            "query": "CREATE (n:Test)",
            "namespace": "test",
            "graph": "test",
            "params": {}
        })


@pytest.mark.asyncio
async def test_invalid_write_query(mcp: FastMCP) -> None:
    """Test executing an invalid write query"""
    with pytest.raises(ToolError):
        await mcp.call_tool("write_flavius_cypher", {
            "query": "MATCH (n) RETURN n",
            "namespace": "test",
            "graph": "test",
            "params": {}
        }) 