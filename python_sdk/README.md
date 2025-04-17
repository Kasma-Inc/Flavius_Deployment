# Flavius Python SDK

The **Flavius Python SDK** provides a lightweight, intuitive interface for interacting with the Flavius graph platform. With support for Python 3.10–3.12, the SDK covers common administrative tasks such as namespace and graph management, schema definition, bulk data import/export, and Cypher query execution—all via a familiar Pythonic API.

## Installation

```bash
# Choose the package matching your Python version:
pip install -i https://test.pypi.org/simple/ flavius_py310   # Python 3.10
pip install -i https://test.pypi.org/simple/ flavius_py311   # Python 3.11
pip install -i https://test.pypi.org/simple/ flavius_py312   # Python 3.12
```

Optionally, install the MinIO client to upload CSV files:

```bash
pip install minio
```

## Quickstart

### 1. Connect to Flavius

```python
from flavius import GraphDatabase

# Point to your FE endpoint:
driver = GraphDatabase.driver("http://localhost:30000")
driver.verify_connectivity()
```

### 2. Create Namespace and Graph

```python
namespace = driver.create_namespace("my_ns")
graph = driver.create_graph("my_graph", namespace=namespace)
```

### 3. Define Schema

```python
# Create a vertex table "User":
driver.create_vertex_table(
    table_name="User",
    columns=[
        ("id", DataType.INTEGER, False),     # NOT NULL
        ("name", DataType.STRING, False),
        ("age", DataType.INTEGER, True)
    ],
    primary_key="id",
    namespace=namespace,
    graph=graph
)

# Create an edge table "knows":
driver.create_edge_table(
    table_name="knows",
    source_vertex="User",
    target_vertex="User",
    columns=[ ("since", DataType.DATE) ],
    directed=True,
    namespace=namespace,
    graph=graph
)
```

### 4. Upload CSV Data to MinIO

```python
from minio import Minio
import os

client = Minio(
    "localhost:30900",
    access_key="fvadmin",
    secret_key="fvadmin123",
    secure=False
)

# Path to CSV files in this SDK directory:
cur_dir = os.path.dirname(__file__)
client.fput_object("flavius", "users.csv", os.path.join(cur_dir, "data/users.csv"))
client.fput_object("flavius", "knows.csv", os.path.join(cur_dir, "data/knows.csv"))
```

### 5. Import Data

```python
# Import vertices from MinIO:
driver.execute_query(
    "BLOCKING IMPORT VERTEX User COLUMNS (\"id\"=$0, \"name\"=$1, \"age\"=$2) "
    "FROM 'oss://flavius/users.csv' WITH (region='cn-hongkong', access_key_id='fvadmin', secret_access_key='fvadmin123', endpoint='http://minio:9000') "
    "FORMAT AS CSV(has_header=false, delimiter=',')",
    namespace=namespace, graph=graph
)

# Import edges:
driver.execute_query(
    "BLOCKING IMPORT EDGE knows FROM (\"id\"=$1) TO (\"id\"=$2) COLUMNS(\"since\"=$0) "
    "FROM 'oss://flavius/knows.csv' WITH (region='cn-hongkong', access_key_id='fvadmin', secret_access_key='fvadmin123', endpoint='http://minio:9000') "
    "FORMAT AS CSV(has_header=false, delimiter=',')",
    namespace=namespace, graph=graph
)
```

### 6. Execute Cypher Queries

```python
# Simple MATCH:
records, keys = driver.execute_query(
    "MATCH (u:User)-[r:knows]->(v:User) RETURN u.name, v.name, r.since",
    namespace=namespace, graph=graph
)
for rec in records:
    print({k: rec[k] for k in keys})

# Parameterized query with list and timestamp parameters:
import dateutil
from flavius import TimeStamp

# Prepare parameters
ts = dateutil.parser.parse("2024-01-02 02:34:00Z")
flavius_ts = TimeStamp(ts)
params = {"ids": [1, 3], "timestamp": flavius_ts}

records, keys = driver.execute_query(
    "MATCH (n:User) WHERE n.integer IN $ids AND n.timestamp > $timestamp "
    "RETURN n.__vid__, n.__label__, n.integer, n.bool, n.string, n.float, n.date, n.time, n.datetime, n.timestamp",
    namespace=namespace,
    graph=graph,
    parameters=params
)
for record in records:
    for key in keys:
        print(f"{key}: {record[key]}, type: {type(record[key])}")
    print()
```

## Reference and Examples

- API definitions: [`python_sdk/client.py`](/python_sdk/client.py)
- Full example script: [`python_sdk/example.py`](/python_sdk/example.py)

## Next Steps

For detailed guidance on advanced scenarios—data type conversions, batch queries, transaction handling, and SDK configuration—please visit the **Flavius Documentation Portal**:

🔗 **https://flavius-docs.kasma.ai/**

## License

This SDK is released under the **Apache 2.0 License**. See [LICENSE](../LICENSE) for details.


