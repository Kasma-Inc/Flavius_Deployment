# Frontend

## Deployment

Dependencies of Frontend:

- protobuf
- rust

#### Setup build environment

1. Install protobuf according to your os.
2. Install rust, [follow this link](https://rustup.rs/)

#### Build

```bash
cd Flavius/
git submodule update --init
./deps2/clone_fe_deps.sh
cd frontend/
cargo build --release
```

Then the executable file will be in `./target/release/frontend`.

#### Start the service

Copy the executable to some location, e.g. `/bin/frontend`.

Configure the frontend config file, the template is in
`Flavius/frontend/config/fe_config.toml`

```toml
[deploy_mode]
deploy_mode = "Cluster"

## The HTTP service configuration.
[http_service_config]
host = "0.0.0.0"
port = 30000

## Bootstrap meta client from etcd
[meta_config.etcd_client]
etcd_endpoints = "16.162.167.0:30020"
catalog_name = "flavius_default_catalog"

## Tracing options
[tracing_config]
## Enable OTLP tracing.
enable_otlp_tracing = true

## The OTLP tracing endpoint.
otlp_endpoint = "http://alloy:4317"
```

Put this config file to some location, e.g. `/etc/flavius/fe_config.toml`

Start the service:

```bash
fe_bin=/bin/frontend
fe_config=/etc/flavius/fe_config.toml
fe_log=/tmp/log/fe.log

${fe_bin} -c ${fe_config} -l ${fe_log} 2>&1 &
```

Then you'll see the log

```text
  2024-04-10T09:28:51.776282Z  INFO frontend:
   ______          _
  / __/ /__ __  __(_)_ _____
 / _// / _ `/ |/ / / // (_-<
/_/ /_/\_,_/|___/_/\_,_/___/

version: 0.1.0
branch: pgao/job_manager
commit_hash: 57e4884868576931266099958aa8de1823c7cf32
commit_date: 2024-04-10 07:33:24 +00:00
build_time: 2024-04-10 15:37:21 +08:00
build_os: macos-aarch64
build_target: aarch64-apple-darwin
rust_version: rustc 1.78.0-nightly (878c8a2a6 2024-02-29)
rust_channel: nightly-2024-03-01-aarch64-apple-darwin
build_mode: release

    at cmd/bin/frontend.rs:61 on ThreadId(1)

  2024-04-10T09:28:51.776470Z  INFO frontend: using config file: /Users/gaopin/code/Flavius/frontend/target/release/fe_config.toml
    at cmd/bin/frontend.rs:87 on ThreadId(1)

  2024-04-10T09:28:51.776481Z  INFO frontend: using log file: /Users/gaopin/code/Flavius/frontend/target/release/fe.log
    at cmd/bin/frontend.rs:88 on ThreadId(1)

  2024-04-10T09:28:51.777029Z  INFO frontend: FE config: FeConfig { deploy_mode: Cluster, http_service_config: HttpServiceConfig { host: "0.0.0.0", port: 55522 }, meta_config: MetaClientConfig { host: "16.162.167.0", port: 22131 } }
    at cmd/bin/frontend.rs:99 on ThreadId(1)

  2024-04-10T09:28:51.881977Z  INFO frontend: FE IS ALIVE
    at cmd/bin/frontend.rs:105 on ThreadId(1)
```

The frontend is alive!

#### Change the tracing level on the flyyyyy

```shell
curl --header "Content-Type: application/json" --request POST --data '{"trace_level": "DEBUG"}' http://<feip>:<fehttpport>/settings
```

#### Check HTTP server health

```shell
curl -w '%{http_code}\n' --header "Content-Type: application/json" --request GET --data '{}' http://<feip>:<fehttpport>/health
```

it will return `200` if success.

## Data Types

### List of Data Types

Flavius support the following data types:

| Data Type | Description                                      | Storage Size | Min Value                           | Max Value                           |
| --------- | ------------------------------------------------ | ------------ | ----------------------------------- | ----------------------------------- |
| BOOL      | Boolean                                          | 1 Byte       | N/A                                 | N/A                                 |
| INTEGER   | Int64                                            | 8 Bytes      | -9223372036854775808                | 9223372036854775807                 |
| FLOAT     | Float64                                          | 8 Bytes      | -1.7976931348623157E+308            | 1.7976931348623157E+308             |
| STRING    | UTF-8 valid string                               | N/A          | N/A                                 | N/A                                 |
| Vertex    | Vertex/Node structure                            | N/A          | N/A                                 | N/A                                 |
| Edge      | Edge/Relationship structure                      | N/A          | N/A                                 | N/A                                 |
| Date      | Date in the format 'YYYY-MM-DD'                  | 4 Bytes      | '0001-01-01'                        | '9999-12-31'                        |
| Time      | Time with nanosecond precision                   | 8 Bytes      | '00:00:00.000000000'                | '23:59:59.999999999'                |
| DateTime  | Date + Time with nanosecond precision            | 8 Bytes      | '1677-09-21 00:12:44.999999999'     | '2262-04-11 23:47:16.854775807'     |
| Timestamp | Date + Time with nanosecond precision + timezone | 8 Bytes      | '1677-09-21 00:12:44.999999999 UTC' | '2262-04-11 23:47:16.854775807 UTC' |

Vertex data type contains `__id___` field which is INTEGER type and describes
the flavius internal vertex id.

Edge data type contains `__srcid__` and `__dstid__` fields which are INTEGER
type and describe the flavius internal source vertex id and target vertex id.

Both Vertex and Edge data type contains `__label__` field which is STRING type
and describes the associated vertex/edge label.

### Data Type Conversions

Casting between different data types. Available casting (`E` means explicit, `A`
means both implicit and explicit, '-' means not):

| source data type / target data type | BOOL | INTEGER | FLOAT | STRING | VERTEX | EDGE | Date | Time | DateTime | Timestamp |
| ----------------------------------- | ---- | ------- | ----- | ------ | ------ | ---- | ---- | ---- | -------- | --------- |
| BOOL                                |      | E       | E     | E      | -      | -    | -    | -    | -        | -         |
| INTEGER                             | E    |         | A     | E      | -      | -    | -    | -    | -        | -         |
| FLOAT                               | E    | E       |       | E      | -      | -    | -    | -    | -        | -         |
| STRING                              | E    | E       | E     |        | -      | -    | E    | E    | E        | E         |
| VERTEX                              | -    | -       | -     | -      |        | -    | -    | -    | -        | -         |
| EDGE                                | -    | -       | -     | -      | -      |      | -    | -    | -        | -         |
| Date                                | -    | -       | -     | -      | -      | -    |      | -    | A        | A         |
| Time                                | -    | -       | -     | -      | -      | -    | -    |      | -        | -         |
| DateTime                            | -    | -       | -     | -      | -      | -    | E    | E    |          | A         |
| Timestamp                           | -    | -       | -     | -      | -      | -    | E    | E    | E        |           |

## Cypher Statements

### Namespace

#### Create Namespace

Create a namespace

**Syntax**

```sql
CREATE NAMESPACE <namespace_name>
```

**Example**

The following example create a namespace named `test_ns`.

```sql
CREATE NAMESPACE test_ns
```

#### Drop Namespace

Drop a namespace and all graphs inside.

**Syntax**

```sql
DROP NAMESPACE <namespace_name>
```

**Example**

The following example drop a namespace named `test_ns`.

```sql
DROP NAMESPACE test_ns
```

#### Describe Namespace

Desribe the meta information about namespace

**Syntax**

```sql
DESCRIBE NAMESPACE <namespace_name>
```

**Example**

```sql
DESCRIBE NAMESPACE test_ns
```

### Graph

#### Create Graph

Create a graph

**Syntax**

```sql
CREATE GRAPH <graph_name>
```

**Example**

Create a graph named `test_graph`

```sql
CREATE GRAPH test_graph
```

#### List Graph

List graph under a namespace.

**Syntax**

```sql
LIST GRAPH
```

**Example**

```sql
LIST GRAPH
```

#### Drop Graph

Drop graph and all underlying vertex tables and edge tables.

**Syntax**

```sql
DROP GRAPH <graph_name>
```

**Example**

Drop a graph named `test_graph`

```sql
DROP GRAPH test_graph
```

#### Describe Graph

Show meta information about given graph.

**Syntax**

```sql
DESCRIBE GRAPH <graph_name>
```

**Example**

```sql
DESCRIBE GRAPH test_graph
```

### Vertex Table

#### Create Vertex Table

Create vertex table with given name.

**Syntax**

```sql
CREATE VERTEX <vertex_table_name> 
(
    <column_name> <data_type> [NOT NULL | NULL ],
    <column_name> <data_type> ...
    ...
)
PRIMARY KEY <column_name> | ( <column_name>, ... )
```

**Example**

Create a vertex table named Person, has three columns, namely `col1`, `col2` and
`col3`. And requires `col1` has an NOT NULL constraint.

```sql
CREATE VERTEX Person
(
  col1 INTEGER NOT NULL,
  col2 STRING,
  col3 STRING
)
PRIMARY KEY col1
```

#### Drop Vertex Table

Drop a vertex table with given name.

**Syntax**

```sql
DROP VERTEX <vertex_table_name>
```

**Example**

```sql
DROP VERTEX Person
```

#### Describe Vertex Table

Describe meta information about a vertex table

**Syntax**

```sql
DESCRIBE VERTEX <vertex_table_name>
```

**Example**

```sql
DESCRIBE VERTEX Person
```

#### List Vertex Tables

List all vertex table names.

**Syntax**

```sql
LIST VERTEX
```

### Edge Table

#### Create Edge Table

Create edge table with associated endpoint vertex tables.

NOTE: Currently only support create directed edges.

**Syntax**

```sql
CREATE DIRECTED | UNDIRECTED EDGE <edge_table_name>
(
    FROM <source_vertex_table_name> 
    TO <target_vertex_table_name>,
    <column_name> <data_type> [NOT NULL | NULL ],
    <column_name> <data_type> ...
)
[ WITH REVERSE EDGE <reverse_edge_table_name> ]
[ EDGE_UNIQUENESS = SINGLE | MULTIPLE ]
```

EDGE_UNIQUENESS:

- SINGLE: There will be at most one edge with value
  `(src, dst, prop1, prop2, ...)`.
- MULTIPLE: Allow multiple edges with the same `(src, dst, prop1, prop2, ...)`.

**Example**

Create a edge table named `Buy`, with sourcee vertex table `User` and target
vertex table `Item`. And edge table has three columns, namely `col1`, `col2` and
`col3`. And requires `col1` has an NOT NULL constraint.

And also create an edge table named `rBuy` which store the reverse direction of
`Buy`.

```sql
CREATE DIRECTED EDGE Buy
(
  FROM User
  TO Item,
  col1 INTEGER NOT NULL,
  col2 STRING,
  col3 STRING
)
WITH REVERSE EDGE rBuy.
```

#### Drop Edge Table

Drop an edge table with given name.

**Syntax**

```sql
DROP EDGE <edge_table_name>
```

**Example**

```sql
DROP EDGE Buy
```

#### Describe Edge Table

Describe meta information about an edge table

**Syntax**

```sql
DESCRIBE EDGE <edge_table_name>
```

**Example**

```sql
DESCRIBE EDGE Buy
```

#### List Edge Tables

List all edge table names.

**Syntax**

```sql
LIST EDGE
```

### Alter Table

#### Rename Column

Rename table column if both table and column exists.

```sql
ALTER TABLE [IF EXISTS] <table_name>
RENAME COLUMN [IF EXISTS] <column_name> TO <new_column_name>
```

**Example**

```sql
ALTER TABLE Person RENAME COLUMN age To new_age
```

### Job

#### Create Import Job

##### Import Vertex Job

**Syntax**

```sql
IMPORT VERTEX <vertex_table_name>
COLUMNS (<vertex_property_name> = $<file_column_index>, <vertex_property_name> = $<file_column_index>, ... )
FROM <import_file_source_uri>[,<import_file_source_uri>]+ sourceOptions
FORMAT AS { CSV } fileFormatOptions
[ importOptions ]
```

For S3:

```sql
WITH (
  REGION = <region>,
  ACCESS_KEY_ID = <access_key_id>,
  SECRET_ACCESS_KEY = <secret_access_key>
)
```

For Oss :

```sql
WITH (
  REGION = <region>,
  ACCESS_KEY_ID = <access_key_id>,
  SECRET_ACCESS_KEY = <secret_access_key>,
  ENDPOINT = <endpoint>
)
```

**fileFormatOptions**

```sql
(
  <key> = <value>,
  <key> = <value>,
  ...
)
```

For csv file format, user can specify the following options:

| Key          | Description                           | Value Type | Default Value |
| ------------ | ------------------------------------- | ---------- | ------------- |
| `has_header` | Whether the file as header line       | Boolean    | `false`       |
| `delimiter`  | Delimiter to separate the columns     | String     | `","`         |
| `null_value` | Recognized spellings for null values. | String     | `""`          |

**importOptions**

```sql
PROPERTIES (
  <key> = <value>,
  <key> = <value>,
  ...
)
```

| Key                         | Description                                                     | Value Type                                                                                                     | Default Value |
| --------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------- |
| `duplicate_vertex_handling` | When importing encountered duplicated vertex, how to handle it. | `"fail"` : Fail the job. `"overwrite"` : Overwrite the duplicated vertex value. `"ignore"`: Ignore the vertex. | `"ignore"`    |
| `log_problematic_lines`     | Whether to log problematic lines.                               | Boolean                                                                                                        | `false`       |
| `format_error_handling`     | How to handle bad format lines.                                 | `"fail"` : Fail the job. `"ignore"` : Skip the error line.                                                     | `"ignore"`    |

**Example**

```sql
IMPORT VERTEX Person COLUMNS("col1" = $0, "col2" = $1, "col3" = $2)
  FROM "s3://kasma-fileio-ci/tinysoc/vPerson.csv","s3://kasma-fileio-ci/tinysoc/vPerson2.csv" 
  WITH (region = "xxx", access_key_id = "xxx", secret_access_key = "xxx" ) 
  FORMAT AS CSV (has_header = true, delimiter = ",")
  PROPERTIES (duplicate_vertex_handling = "ignore", log_problematic_lines = true, format_error_handling = "ignore")
```

Example of importing from oss

```sql
IMPORT VERTEX Person COLUMNS("col1" = $0, "col2" = $1, "col3" = $2) 
  FROM "oss://kasma-fileio-ci/tinysoc/vPerson.csv" 
  WITH (region = "xxx", access_key_id = "xxx", secret_access_ke = "xxx", endpoint = "https://oss-cn-hongkong.aliyuncs.com")
  FORMAT AS CSV (has_header = true, delimiter = "," )
```

##### Import Edge Job

**Syntax**

```sql
IMPORT EDGE <edge_table_name>
FROM ( <source_vertex_primary_key_name> = $<file_column_index>, <source_vertex_primary_key_name> = $<file_column_index>, ... )
TO ( <target_vertex_primary_key_name> = $<file_column_index>, <target_vertex_primary_key_name> = $<file_column_index>, ... )
COLUMNS ( <edge_property_name> = $<file_column_index>, <edge_property_name> = $<file_column_index>, ... )
FROM <import_file_source_uri>[,<import_file_source_uri>]+ sourceOptions
FORMAT AS { CSV } fileFormatOptions
[ importOptions ]
```

**importOptions**

```sql
PROPERTIES (
  <key> = <value>,
  <key> = <value>,
  ...
)
```

| Key                                   | Description                                                        | Value Type                                                 | Default Value |
| ------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------- | ------------- |
| `incident_vertex_not_exists_handling` | How to handle cases where the edge endpoint vertex does not exist. | `"fail"` : Fail the job. `"ignore"`: Ignore the edge.      | `"ignore"`    |
| `log_problematic_lines`               | Whether to log problematic lines.                                  | Boolean                                                    | `false`       |
| `format_error_handling`               | How to handle bad format lines.                                    | `"fail"` : Fail the job. `"ignore"` : Skip the error line. | `"ignore"`    |

**Example**

```sql
IMPORT EDGE Knows FROM ("col1" = $0) TO ("col1" = $1)
  COLUMNS("col1" = $2)
  FROM "s3://kasma-fileio-ci/tinysoc/eKnows.csv"
  WITH (region = "xxx", access_key_id = "xxx", secret_access_key = "xxx" ) 
  FORMAT AS CSV (has_header = true, delimiter = "," )
  PROPERTIES (incident_vertex_not_exists_handling = "fail", log_problematic_lines = true, format_error_handling = "ignore")
```

#### Check Import Job Staus

```cypher
CHECK JOB <job_id>
```

### ResourceGroup

NOTE: Currently, flavius has two buildin resource groups: "Query" and "Job",
where regular queries are submitted to `Query` group and importing load jobs and
backgroud compaction tasks are submitted to `Job` group.

Currently we have the following configurations for resource groups.

| Key                | Description                                                                        | Value Type | Default Value |
| ------------------ | ---------------------------------------------------------------------------------- | ---------- | ------------- |
| memory_limit_bytes | Memory limit of this resource group for each flavius compute node                  | Integer    |               |
| cpu_core_limit     | For each flavius compute, how many cpu cores are allocated for this resource group | Integer    |               |
| concurrency_limit  | Limit the number of concurrent running queries/jobs on this resource group         | Integer    |               |

If query queue enabled, the fowlloing configurations are used for manage the
behavior of query queue.

| Key                                              | Description                                                                                                                                                                                             | Value Type | Default Value |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ------------- |
| query_queue_enabled                              | If query queuing is enabled                                                                                                                                                                             | Boolean    | False         |
| query_queue_timeout_second                       | How long the query stay in the queue before timeout by the queue. 0 means unlimited.                                                                                                                    | Integer    | 0             |
| query_queue_concurrency_limit                    | If current running queries exceed this limit, new queries are pushed to the queue. 0 means unlimited.                                                                                                   | Integer    | 0             |
| query_queue_memory_percent_limit                 | If current flavius compute nodes memory useage exceed this limit, new queries will be pushed to the queue. 0 means unlimited.                                                                           | Integer    | 0             |
| query_queue_cpu_used_permille_limit              | If current flavius compute node cpu usage exceed this limit, new queries will be pushed to the queue. `cpu_usec_permille = folly::ThreadPool::usedCpuTime() / 1000000 / NUM_THREAD`. 0 means unlimited. | Integer    | 0             |
| query_queue_thread_pool_pending_task_count_limit | If current flavius compute node thread pool pending task count exceed this limit, new queries will be pushed to the queue. 0 means unlimited                                                            | Integer    | 0             |

#### List Resource Group

```sql
LIST RESOURCE GROUP
```

#### Describe Resource Group

```sql
DESCRIBE RESOURCE GROUP <group_name>
```

NOTE: resource group names are case sensitive.

**Example** Show the configurations of `Query` Resource group.

```sql
DESCRIBE RESOURCE GROUP Query
```

#### Alter Resource Group

Update the resource group configurations.

```sql
ALTER RESOURCE GROUP <group_name> WITH (
  <key> = <val>,
  <key> = <val>,
  ...
)
```

**Example** Update enable query queuing and update query queue concurreny limit

```sql
ALTER RESOURCE GROUP Query WITH (
  query_queue_enabled = true,
  query_queue_concurrency_limit = 100,
)
```

### Query

```cypher
MATCH (n:Person) RETURN n
```

#### Match on multiple node labels

Find nodes with `Person` or `Item` labels.

```cypher
MATCH (a:Person:Item) RETURN a
```

#### Match on multiple rel types

Find relationship with `rBuy` or `Knows` relationship types.

```cypher
MATCH (a)<-[r:rBuy|:Knows]-(b) RETURN a
```

### Insert to flavius

Insert one or mutiple record into a vertex/edge.

#### Syntax

```sql
INSERT INTO <vertex/edge>
    -- Optionally specify the insert properties
    ( PROPERTYES ( ... ) )
    -- Insertion options:
    {
        MATCH ...
    }
```

Properties for insert vertex:

| Key                       | Description                                                         | Value                                                                                                        |
| ------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| duplicate_vertex_handling | Indicates how to handle the case insert data has duplicated vertex. | `"fail"`: Fail the query. `"overwrite"`: overwrite the vertex value. `"ignore"`: ignore this vertex(default) |
| log_problematic_lines     | True on log the records that has problems.                          | `"true"`: log the records. `"false"`: do not log the records(Default).                                       |

Properties for insert edge:

| Key                                 | Description                                                                 | Value                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| incident_vertex_not_exists_handling | Indicateshow to handle cases where the edge endpoint vertex does not exist. | `"fail"`: Fail the query. `"ignore"`: Ignore the edge(Default).        |
| log_problematic_lines               | True on log the records that has problems.                                  | `"true"`: log the records. `"false"`: do not log the records(Default). |

#### Examples

Insert vertex

```sql
INSERT INTO Person2 PROPERTIES (duplicate_vertex_handling = "ignore", log_problematic_lines = "true")
MATCH (n:Person) RETURN n.col1, n.col2, n.col3
```

Insert edge

```sql
INSERT INTO Knows2 PROPERTIES (incident_vertex_not_exists_handling = "fail", log_problematic_lines = "true")
MATCH (a:Person)-[r:Knows]->(b:Person) RETURN a.col1, b.col1, r.col1
```

### Insert to object store

Insert one or mutiple record into a object store.

#### Syntax

```sql
INSERT INTO FILES(
    -- Optionally specify the insert properties
  <key> = <value>,
  ...
)
    {
        MATCH ...
    }
```

For local files, the valid key and values are :

| Key    | Description                                     | Value                                 |
| ------ | ----------------------------------------------- | ------------------------------------- |
| PATH   | path to export to, should starts with `file://` | String, e.g. "file://a/b/c            |
| FORMAT | file format                                     | String, avaialbe values: `"PARQUET"`. |

For s3 files, the valid key and values are :

| Key               | Description                                   | Value                                 |
| ----------------- | --------------------------------------------- | ------------------------------------- |
| PATH              | path to export to, should starts with `s3://` | String, e.g. "s3://a/b/c              |
| REGION            | s3 region to export to                        | String                                |
| ACCESS_KEY_ID     | s3 access key id                              | String                                |
| SECRET_ACCESS_KEY | s3 secret access key                          | String                                |
| FORMAT            | file format                                   | String, avaialbe values: `"PARQUET"`. |

For oss files, the valid key and values are :

| Key               | Description                                    | Value                                               |
| ----------------- | ---------------------------------------------- | --------------------------------------------------- |
| PATH              | path to export to, should starts with `oss://` | String, e.g. "oss://a/b/c                           |
| REGION            | oss region to export to                        | String                                              |
| ACCESS_KEY_ID     | oss access key id                              | String                                              |
| SECRET_ACCESS_KEY | oss secret access key                          | String                                              |
| ENDPOINT          | oss endpoint                                   | String, e.g. "https://oss-cn-hongkong.aliyuncs.com" |
| FORMAT            | file format                                    | String, avaialbe values: `"PARQUET"`.               |

### Explain

```cypher
EXPLAIN VERBOSE|HIR|REL <stmt>
```

### Functions

This section provides a detailed overview of aggregation and scalar functions in
the database, including parameter descriptions, return types, and usage examples
to help users apply them effectively.

#### Aggregation Functions

- **count**(*)

  **Description**: Returns the number of input rows. Applicable to all types.

  **Return Type**: `INTEGER`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN count(*) AS total_people;
  ```

- **count**(x)

  **Description**: Returns the count of non-null input values.

  **Parameter**:
  - `x`: any type

  **Return Type**: `INTEGER`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN count(n.age) AS known_ages;
  ```

- **sum**(x)

  **Description**: Returns the sum of all input values.

  **Parameter**:
  - `x`: `INTEGER` or `FLOAT`

  **Return Type**: same as input type

  **Example**:

  ```cypher
  MATCH (n:Transaction) RETURN sum(n.amount) AS total_amount;
  ```

- **min**(x)

  **Description**: Returns the minimum value among all input values, ignoring
  nulls. `x` must not contain nulls if it is a complex type.

  **Parameter**:
  - `x`: orderable type `INTEGER` or `FLOAT`

  **Return Type**: same as input type

  **Example**:

  ```cypher
  MATCH (n:Product) RETURN min(n.price) AS lowest_price;
  ```

- **max**(x)

  **Description**: Returns the maximum value among all input values, ignoring
  nulls. `x` must not contain nulls if it is a complex type.

  **Parameter**:
  - `x`: orderable type `INTEGER` or `FLOAT`

  **Return Type**: same as input type

  **Example**:

  ```cypher
  MATCH (n:Product) RETURN max(n.price) AS highest_price;
  ```

- **avg**(x)

  **Description**: Returns the average (arithmetic mean) of all non-null input
  values.

  **Parameter**:
  - `x`: `INTEGER` or `FLOAT`

  **Return Type**: `FLOAT`

  **Example**:

  ```cypher
  MATCH (n:Student) RETURN avg(n.grade) AS average_grade;
  ```

- **variance**(x)

  **Description**: Returns the sample variance of all input values.

  **Parameter**:
  - `x`: `INTEGER` or `FLOAT`

  **Return Type**: `FLOAT`

  **Example**:

  ```cypher
  MATCH (n:Employee) RETURN variance(n.salary) AS salary_variance;
  ```

- **stddev**(x)

  **Description**: Returns the sample standard deviation of all input values.

  **Parameter**:
  - `x`: `INTEGER` or `FLOAT`

  **Return Type**: `FLOAT`

  **Example**:

  ```cypher
  MATCH (n:Employee) RETURN stddev(n.salary) AS salary_stddev;
  ```

- **count_if**(x)

  **Description**: Returns the count of `TRUE` input values, equivalent to
  `count(CASE WHEN x THEN 1 END)`.

  **Parameter**:
  - `x`: boolean

  **Return Type**: `INTEGER`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN count_if(n.active) AS active_count;
  ```

- **set_agg**(x)

  **Description**: Returns an list created from distinct input `x` elements. For
  complex types, `x` must not contain nulls.

  **Parameter**:
  - `x`: any type

  **Return Type**: `LIST<[same as x]>`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN set_agg(n.city) AS unique_cities;
  ```

- **array_agg**(x)

  **Description**: Returns an list created from the input `x` elements. Ignores
  null inputs if the setting `presto.array_agg.ignore_nulls` is `false`.

  **Parameter**:
  - `x`: any type

  **Return Type**: `LIST<[same as x]>`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN array_agg(n.name) AS names;
  ```

#### Scalar Functions

- **logical** AND OR NOT XOR

  **Description**: Logical operators for combining boolean expressions.

  **Parameter**:
  - `x`: boolean

  **Return Type**: `BOOLEAN`

  **Example**:

  ```cypher
  MATCH (n:Person) WHERE n.age > 18 AND n.active RETURN n;
  ```

- **compare** `>` `>=` `<>` `<` `<=`

  **Description**: Comparison operators for comparing values.

  **Parameter**:
  - `x`: any comparable type

  **Return Type**: `BOOLEAN`

  **Example**:

  ```cypher
  MATCH (n:Person) WHERE n.age > 30 RETURN n;
  ```

- **math** `+` `-` `*` `/`

  **Description**: Arithmetic operators for performing mathematical operations.

  **Parameter**:

  - `x`: numeric type (`INTEGER` or `FLOAT`)

  **Return Type**: same as input type

  **Example**:

  ```cypher
  MATCH (n:Transaction) RETURN n.amount * 1.1 AS increased_amount;
  ```

- **coalesce**(expr1, expr2, ..., exprN)

  **Description**: Returns the first non-null value in the argument list. Like
  an IF or SWITCH expression, arguments are only evaluated if necessary.

  **Parameter**:
  - `expr1, expr2, ..., exprN`: multiple input expressions of the same type

  **Return Type**: [same as input expressions]

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN coalesce(n.name, n.nickname, 'Unknown') AS displayName;
  ```

- **ARRAY[Expression (, Expression)*]**

  **Description**: Create an array.

  **Parameter**:

  - `Expression`: array item

  **Return Type**: LIST

  **Example**:

  ```cypher
  MATCH (n:Transaction) RETURN ARRAY[n.name, "6"];
  ```

- **array_sort**(LIST(E))

  **Description**: Returns an list with the sorted order of the input array. `E`
  must be an orderable type. Null elements are placed at the end of the returned
  list. May throw an error if `E` is an `LIST` or `ROW` type and input values
  contain nested nulls.

  **Parameter**:
  - `LIST(E)`: an list to be sorted; `E` must be an orderable type

  **Return Type**: `LIST(E)`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN array_sort(n.friends) AS sorted_friends;
  ```

- **array_sort**(LIST(T), FUNCTION(T, U))

  **Description**: Returns the array sorted by values computed using specified
  lambda in ascending order. `U` must be an orderable type. Null elements will
  be placed at the end of the returned array. May throw if `E` is and `ARRAY` or
  `ROW` type and input values contain nested nulls. Throws if deciding the order
  of elements would require comparing nested null values.

  **Parameter**:
  - `LIST(T)`: a list to be sorted
  - `FUNCTION(T, U)`: a lambda function transform T to U
  - `U` must be an orderable type

  **Return Type**: `LIST(T)`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN array_sort(n.friends, x -> x.age) AS sorted_friends;
  ```

- **array_sort_desc**(LIST(E))

  **Description**: Returns the array sorted in the descending order. `E` must be
  an orderable type. Null elements will be placed at the end of the returned
  array. May throw if `E` is and `ARRAY` or `ROW` type and input values contain
  nested nulls. Throws if deciding the order of elements would require comparing
  nested null values.

  **Parameter**:
  - `LIST(E)`: an list to be sorted; `E` must be an orderable type

  **Return Type**: `LIST(E)`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN array_sort_desc(n.friends) AS sorted_friends;
  ```

- **array_sort_desc**(LIST(T), FUNCTION(T, U))

  **Description**: Returns the array sorted by values computed using specified
  lambda in descending order. `U` must be an orderable type. Null elements will
  be placed at the end of the returned array. May throw if `E` is and `ARRAY` or
  `ROW` type and input values contain nested nulls. Throws if deciding the order
  of elements would require comparing nested null values.

  **Parameter**:
  - `LIST(T)`: a list to be sorted
  - `FUNCTION(T, U)`: a lambda function transform T to U
  - `U` must be an orderable type

  **Return Type**: `LIST(T)`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN array_sort_desc(n.friends, x -> x.age) AS sorted_friends;
  ```

- **contains**(x, element)

  **Description**: Returns true if the array `x` contains the element. When
  `element` is of complex type, throws if `x` or `element` contains nested nulls
  and these need to be compared to produce a result. For `REAL` and `DOUBLE`,
  `NANs` (Not-a-Number) are considered equal.

  **Parameter**:
  - `x`: a list
  - `element`: any type

  **Return Type**: `Boolean`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN contains(ARRAY[1,2,3], 1);
  ```

- **slice**(array(E), start, length)

  **Description**: Returns a subarray starting from index `start`(or starting
  from the end if `start` is negative) with a length of length.

  **Parameter**:
  - `array(E)`: a list
  - `start`: start index of subarray. `start` != 0.
  - `length`: length of subarray. `length` >= 0.

  **Return Type**: `array(E)`

  **Example**:

  ```cypher
  MATCH (n:Person) RETURN slice(n.friends, 1, 10) AS sorted_friends;
  ```

#### Mathematical Functions

- **ceil**

  **Description**: This is an alias for `ceiling()`.

  **Parameter**:
  - `x`: numeric

  **Return Type**: [same as x]

  **Example**:

  ```cypher
  RETURN ceil(3.14);  -- Returns 4
  ```

- **ceiling**(x)

  **Description**: Returns `x` rounded up to the nearest integer.

  **Parameter**:
  - `x`: numeric

  **Return Type**: [same as x]

  **Example**:

  ```cypher
  RETURN ceiling(3.14);  -- Returns 4
  ```

#### String Functions

- **chr**(n)

  **Description**: Returns the Unicode code point `n` as a single character
  string.

  **Parameter**:
  - `n`: `INTEGER`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN chr(65) AS character; -- 返回 'A'
  ```

- **codepoint**(string) (暂不支持)

  **Description**: Returns the Unicode code point of the only character of
  `string`.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `INTEGER`

  **Example**:

  ```cypher
  RETURN codepoint('A') AS unicode_value; -- 返回 65
  ```

- **concat**(string1, ..., stringN)

  **Description**: Returns the concatenation of `string1`, `string2`, ...,
  `stringN`. This function provides the same functionality as the SQL-standard
  concatenation operator (`||`).

  **Parameter**:
  - `string1`: `STRING`
  - `string2`: `STRING`
  - ...,
  - `stringN`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN concat('Hello', ' ', 'World') AS greeting; -- 返回 'Hello World'
  ```

- **ends_with**(string, substring)

  **Description**: Returns whether `string` ends with `substring`.

  **Parameter**:
  - `string`: `STRING`
  - `substring`: `STRING`

  **Return Type**: `BOOLEAN`

  **Example**:

  ```cypher
  RETURN ends_with('Hello World', 'World') AS result; -- 返回 true
  ```

- **hamming_distance**(string1, string2)

  **Description**: Returns the Hamming distance of `string1` and `string2`, i.e.
  the number of positions at which the corresponding characters are different.
  Note that the two strings must have the same length.

  **Parameter**:
  - `string1`: `STRING`
  - `string2`: `STRING`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN hamming_distance('karolin', 'kathrin') AS distance; -- 返回 3
  ```

- **length**(string)

  **Description**: Returns the length of `string` in characters.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN length('Hello World') AS string_length; -- 返回 11
  ```

- **levenshtein_distance**(string_1, string_2)

  **Description**: Returns the Levenshtein edit distance of `string_1` and
  `string_2`, i.e. the minimum number of single-character edits (insertions,
  deletions, or substitutions) needed to convert `string_1` to `string_2`.

  **Parameter**:
  - `string_1`: `STRING`
  - `string_2`: `STRING`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN levenshtein_distance('kitten', 'sitting') AS distance; -- 返回 3
  ```

- **lower**(string)

  **Description**: Converts `string` to lowercase.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN lower('Hello World') AS lowercased_string; -- 返回 'hello world'
  ```

- **lpad**(string, size, padstring)

  **Description**: Left pads `string` to `size` characters with `padstring`. If
  `size` is less than the length of `string`, the result is truncated to `size`
  characters. `size` must not be negative and `padstring` must be non-empty.

  **Parameter**:
  - `string`: `STRING`
  - `size`: `INTEGER`
  - `padstring`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN lpad('Hello', 10, '*') AS padded_string; -- 返回 '*****Hello'
  ```

- **ltrim**(string)

  **Description**: Removes leading whitespace from `string`. See `trim()` for
  the set of recognized whitespace characters.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN ltrim('   Hello World') AS trimmed_string; -- 返回 'Hello World'
  ```

- **ltrim**(string, chars)

  **Description**: Removes the longest substring containing only characters in
  `chars` from the beginning of the `string`.

  **Parameter**:
  - `string`: `STRING`
  - `chars`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN ltrim('***Hello World', '*') AS trimmed_string; -- 返回 'Hello World'
  ```

- **replaceFirst**(string, search, replace) (暂不支持)

  **Description**: Removes the first instance of `search` with `replace` in
  `string`. If `search` is an empty string, inserts `replace` in front of
  `string`.

  **Parameter**:
  - `string`: `STRING`
  - `search`: `STRING`
  - `replace`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN replaceFirst('Hello World', 'World', 'Universe') AS result; -- 返回 'Hello Universe'
  RETURN replaceFirst('Hello World', '', 'Hi ') AS result; -- 返回 'Hi Hello World'
  ```

- **replace**(string, search)

  **Description**: Removes all instances of `search` from `string`.

  **Parameter**:
  - `string`: `STRING`
  - `search`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN replace('Hello World', 'o', '') AS result; -- 返回 'Hell Wrld'
  ```

- **replace**(string, search, replace)

  **Description**: Replaces all instances of `search` with `replace` in
  `string`. If `search` is an empty string, inserts `replace` in front of every
  character and at the end of the `string`.

  **Parameter**:
  - `string`: `STRING`
  - `search`: `STRING`
  - `replace`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN replace('Hello World', 'o', 'a') AS result; -- 返回 'Hella Warld'
  RETURN replace('Hello', '', '-') AS result; -- 返回 '-H-e-l-l-o-'
  ```

- **reverse**(string)

  **Description**: Returns the input `string` with characters in reverse order.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN reverse('Hello World') AS reversed_string; -- 返回 'dlroW olleH'
  ```

- **rpad**(string, size, padstring)

  **Description**: Right pads `string` to `size` characters with `padstring`. If
  `size` is less than the length of `string`, the result is truncated to `size`
  characters. `size` must not be negative and `padstring` must be non-empty.

  **Parameter**:
  - `string`: `STRING`
  - `size`: `INTEGER`
  - `padstring`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN rpad('Hello', 10, '*') AS padded_string; -- 返回 'Hello*****'
  ```

- **rtrim**(string)

  **Description**: Removes trailing whitespace from `string`. See `trim()` for
  the set of recognized whitespace characters.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN rtrim('Hello World   ') AS trimmed_string; -- 返回 'Hello World'
  ```

- **rtrim**(string, chars)

  **Description**: Removes the longest substring containing only characters in
  `chars` from the end of the `string`.

  **Parameter**:
  - `string`: `STRING`
  - `chars`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN rtrim('Hello World***', '*') AS trimmed_string; -- 返回 'Hello World'
  ```

- **split**(string, delimiter)

  **Description**: Splits `string` on `delimiter` and returns an array.

  **Parameter**:
  - `string`: `STRING`
  - `delimiter`: `STRING`

  **Return Type**: `ARRAY<VARCHAR>`

  **Example**:

  ```cypher
  RETURN split('Hello,World,Example', ',') AS result; -- 返回 ['Hello', 'World', 'Example']
  ```

- **split**(string, delimiter, limit)

  **Description**: Splits `string` on `delimiter` and returns an array of size
  at most `limit`. The last element in the array always contains everything left
  in the `string`. `limit` must be a positive number.

  **Parameter**:
  - `string`: `STRING`
  - `delimiter`: `STRING`
  - `limit`: `INTEGER`

  **Return Type**: `ARRAY<VARCHAR>`

  **Example**:

  ```cypher
  RETURN split('Hello,World,Example,Test', ',', 3) AS result; -- 返回 ['Hello', 'World', 'Example,Test']
  ```

- **split_part**(string, delimiter, index)

  **Description**: Splits `string` on `delimiter` and returns the part at
  `index`. Field indexes start with 1. If the `index` is larger than the number
  of fields, then `null` is returned.

  **Parameter**:
  - `string`: `STRING`
  - `delimiter`: `STRING`
  - `index`: `INTEGER`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN split_part('Hello,World,Example', ',', 2) AS result; -- 返回 'World'
  RETURN split_part('Hello,World,Example', ',', 5) AS result; -- 返回 null
  ```

- **split_to_map**(string, entryDelimiter, keyValueDelimiter)

  **Description**: Splits `string` by `entryDelimiter` and `keyValueDelimiter`
  and returns a map. `entryDelimiter` splits `string` into key-value pairs.
  `keyValueDelimiter` splits each pair into key and value. Note that
  `entryDelimiter` and `keyValueDelimiter` are interpreted literally, i.e., as
  full string matches. `entryDelimiter` and `keyValueDelimiter` must not be
  empty and must not be the same. `entryDelimiter` is allowed to be the trailing
  character. Raises an error if there are duplicate keys.

  **Parameter**:
  - `string`: `STRING`
  - `entryDelimiter`: `STRING`
  - `keyValueDelimiter`: `STRING`

  **Return Type**: `MAP<VARCHAR, VARCHAR>`

  **Example**:

  ```cypher
  RETURN split_to_map('key1=value1;key2=value2', ';', '=') AS result; -- 返回 {key1: 'value1', key2: 'value2'}
  ```

- **split_to_map**(string, entryDelimiter, keyValueDelimiter, function(K, V1,
  V2, R))

  **Description**: Splits `string` by `entryDelimiter` and `keyValueDelimiter`
  and returns a map. `entryDelimiter` splits `string` into key-value pairs.
  `keyValueDelimiter` splits each pair into key and value. Note that
  `entryDelimiter` and `keyValueDelimiter` are interpreted literally, i.e., as
  full string matches. `function(K, V1, V2, R)` is used to decide whether to
  keep the first or last value for duplicate keys. `(k, v1, v2) -> v1` keeps the
  first value. `(k, v1, v2) -> v2` keeps the last value. Arbitrary functions are
  not supported.

  **Parameter**:
  - `string`: `STRING`
  - `entryDelimiter`: `STRING`
  - `keyValueDelimiter`: `STRING`
  - `function(K, V1, V2, R)`: `FUNCTION`

  **Return Type**: `MAP<VARCHAR, VARCHAR>`

  **Example**:

  ```cypher
  RETURN split_to_map('key1=value1;key2=value2;key1=value3', ';', '=', (k, v1, v2) -> v1) AS result; -- 返回 {key1: 'value1', key2: 'value2'}
  RETURN split_to_map('key1=value1;key2=value2;key1=value3', ';', '=', (k, v1, v2) -> v2) AS result; -- 返回 {key1: 'value3', key2: 'value2'}
  ```

- **starts_with**(string, substring)

  **Description**: Returns whether `string` starts with `substring`.

  **Parameter**:
  - `string`: `STRING`
  - `substring`: `STRING`

  **Return Type**: `BOOLEAN`

  **Example**:

  ```cypher
  RETURN starts_with('Hello World', 'Hello') AS result; -- 返回 true
  RETURN starts_with('Hello World', 'World') AS result; -- 返回 false
  ```

- **strpos**(string, substring)

  **Description**: Returns the starting position of the first instance of
  `substring` in `string`. Positions start with 1. If not found, 0 is returned.

  **Parameter**:
  - `string`: `STRING`
  - `substring`: `STRING`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN strpos('Hello World', 'World') AS result; -- 返回 7
  RETURN strpos('Hello World', 'world') AS result; -- 返回 0
  ```

- **strpos**(string, substring, instance)

  **Description**: Returns the position of the N-th instance of `substring` in
  `string`. `instance` must be a positive number. Positions start with 1. If not
  found, 0 is returned. It takes into account overlapping strings when counting
  occurrences.

  **Parameter**:
  - `string`: `STRING`
  - `substring`: `STRING`
  - `instance`: `INTEGER`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN strpos('ababab', 'ab', 2) AS result; -- 返回 3
  RETURN strpos('Hello World World', 'World', 2) AS result; -- 返回 13
  RETURN strpos('Hello World', 'world', 1) AS result; -- 返回 0
  ```

- **strrpos**(string, substring)

  **Description**: Returns the starting position of the last instance of
  `substring` in `string`. Positions start with 1. If not found, 0 is returned.

  **Parameter**:
  - `string`: `STRING`
  - `substring`: `STRING`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN strrpos('Hello World World', 'World') AS result; -- 返回 13
  RETURN strrpos('Hello World', 'world') AS result; -- 返回 0
  ```

- **strrpos**(string, substring, instance)

  **Description**: Returns the position of the N-th instance of `substring` in
  `string` starting from the end of the `string`. `instance` must be a positive
  number. Positions start with 1. If not found, 0 is returned. It takes into
  account overlapping strings when counting occurrences.

  **Parameter**:
  - `string`: `STRING`
  - `substring`: `STRING`
  - `instance`: `INTEGER`

  **Return Type**: `INTERGER`

  **Example**:

  ```cypher
  RETURN strrpos('ababab', 'ab', 1) AS result; -- 返回 5
  RETURN strrpos('Hello World World', 'World', 1) AS result; -- 返回 13
  RETURN strrpos('Hello World World', 'World', 2) AS result; -- 返回 7
  RETURN strrpos('Hello World', 'world', 1) AS result; -- 返回 0
  ```

- **trail**(string, N) (暂不支持)

  **Description**: Returns the last `N` characters of the input `string` up to
  at most the length of `string`.

  **Parameter**:
  - `string`: `STRING`
  - `N`: `INTEGER`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN trail('Hello World', 5) AS result; -- 返回 'World'
  RETURN trail('Hello', 10) AS result; -- 返回 'Hello'
  ```

- **substr**(string, start)

  **Description**: Returns the rest of `string` from the starting position
  `start`. Positions start with 1. A negative starting position is interpreted
  as being relative to the end of the `string`. Returns an empty string if the
  absolute value of `start` is greater than the length of the `string`.

  **Parameter**:
  - `string`: `STRING`
  - `start`: `INTEGER`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN substr('Hello World', 7) AS result; -- 返回 'World'
  RETURN substr('Hello World', -5) AS result; -- 返回 'World'
  RETURN substr('Hello World', 20) AS result; -- 返回 ''
  ```

- **substr**(string, start, length)

  **Description**: Returns a substring from `string` of length `length` from the
  starting position `start`. Positions start with 1. A negative starting
  position is interpreted as being relative to the end of the `string`. Returns
  an empty string if the absolute value of `start` is greater than the length of
  the `string`.

  **Parameter**:
  - `string`: `STRING`
  - `start`: `INTEGER`
  - `length`: `INTEGER`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN substr('Hello World', 7, 5) AS result; -- 返回 'World'
  RETURN substr('Hello World', -5, 3) AS result; -- 返回 'Wor'
  RETURN substr('Hello World', 20, 5) AS result; -- 返回 ''
  ```

- **trim**(string)

  **Description**: Removes starting and ending whitespaces from `string`.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `STRING`

  **Recognized Whitespace Characters**:
  - `9`: TAB (horizontal tab)
  - `10`: LF (NL line feed, new line)
  - `11`: VT (vertical tab)
  - `12`: FF (NP form feed, new page)
  - `13`: CR (carriage return)
  - `28`: FS (file separator)
  - `29`: GS (group separator)
  - `30`: RS (record separator)
  - `31`: US (unit separator)
  - `32`: Space
  - `U+1680`: Ogham Space Mark
  - `U+2000`: En Quad
  - `U+2001`: Em Quad
  - `U+2002`: En Space
  - `U+2003`: Em Space
  - `U+2004`: Three-Per-Em Space
  - `U+2005`: Four-Per-Em Space
  - `U+2006`: Six-Per-Em Space
  - `U+2008`: Punctuation Space
  - `U+2009`: Thin Space
  - `U+200a`: Hair Space
  - `U+2028`: Line Separator
  - `U+2029`: Paragraph Separator
  - `U+205f`: Medium Mathematical Space
  - `U+3000`: Ideographic Space

  **Example**:

  ```cypher
  RETURN trim('  Hello World  ') AS result; -- 返回 'Hello World'
  RETURN trim('\tHello World\n') AS result; -- 返回 'Hello World'
  ```

- **trim**(string, chars)

  **Description**: Removes the longest substring containing only characters in
  `chars` from the beginning and end of the `string`.

  **Parameter**:
  - `string`: `STRING`
  - `chars`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN trim('---Hello World---', '-') AS result; -- 返回 'Hello World'
  RETURN trim('xyxHello Worldxyx', 'xy') AS result; -- 返回 'Hello World'
  RETURN trim('  Hello World  ', ' ') AS result; -- 返回 'Hello World'
  ```

- **upper**(string)

  **Description**: Converts `string` to uppercase.

  **Parameter**:
  - `string`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN upper('Hello World') AS result; -- 返回 'HELLO WORLD'
  RETURN upper('hello') AS result; -- 返回 'HELLO'
  ```

- **word_stem**(word)

  **Description**: Returns the stem of `word` in the English language. If the
  word is not an English word, the word in lowercase is returned.

  **Parameter**:
  - `word`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN word_stem('running') AS result; -- 返回 'run'
  RETURN word_stem('cats') AS result; -- 返回 'cat'
  RETURN word_stem('HELLO') AS result; -- 返回 'hello'
  RETURN word_stem('nonenglishword') AS result; -- 返回 'nonenglishword'
  ```
- **word_stem**(word, lang)

  **Description**: Returns the stem of `word` in the `lang` language. This
  function supports the following languages:

  | lang | Language   |
  | ---- | ---------- |
  | ca   | Catalan    |
  | da   | Danish     |
  | de   | German     |
  | en   | English    |
  | es   | Spanish    |
  | eu   | Basque     |
  | fi   | Finnish    |
  | fr   | French     |
  | hu   | Hungarian  |
  | hy   | Armenian   |
  | ir   | Irish      |
  | it   | Italian    |
  | lt   | Lithuanian |
  | nl   | Dutch      |
  | no   | Norwegian  |
  | pt   | Portuguese |
  | ro   | Romanian   |
  | ru   | Russian    |
  | sv   | Swedish    |
  | tr   | Turkish    |

  If the specified `lang` is not supported, this function throws a user error.

  **Parameter**:
  - `word`: `STRING`
  - `lang`: `STRING`

  **Return Type**: `STRING`

  **Example**:

  ```cypher
  RETURN word_stem('running', 'en') AS result; -- 返回 'run'
  RETURN word_stem('gatos', 'es') AS result; -- 返回 'gat'
  RETURN word_stem('laufen', 'de') AS result; -- 返回 'lauf'
  RETURN word_stem('nonenglishword', 'en') AS result; -- 返回 'nonenglishword'
  RETURN word_stem('correr', 'pt') AS result; -- 返回 'corr'
  ```

#### Cast

CAST(_expression_ AS _datatype_)

```cypher
CAST(3.14 AS INTEGER)
```

Casting between different data types. Available casting (`Y` means yes, `N`
means no):

| source data type / target data type | Bool | String | Integer | Float |
| ----------------------------------- | ---- | ------ | ------- | ----- |
| Bool                                | Y    | Y      | Y       | Y     |
| String                              | Y    | Y      | Y       | Y     |
| Integer                             | Y    | Y      | Y       | Y     |
| Float                               | Y    | Y      | Y       | Y     |

Neo4j compability note: Neo4j use
[functions](https://neo4j.com/docs/cypher-manual/current/values-and-types/casting-data/#search)
to casting expression values. Here we align with GQL standard which uses `CAST`
expression which is more general.

## Development

### Crates

- cmd: The executable binary.
- common: Utilities.
- config: Flavius configuration.
- cypher: Cypher parser and ast.
- data: Data representation in flavius.
- datatype: Data types in flavius.
- frontend: The frontend layer, including, Session/Connection, query
  complilation and execution.
- meta: The meta related structs, including catalog interface etc.
- proto: Protobuf objects in rust.
- rpc: Rpc client of meta server, compute server.

### How to generate openapi interface

First, start frontend, you can start an standalone frontend instance.

Then `curl http://localhost:30000/v1/api.json  | jq > api.json`

### Tracing and Metrics

Frontend will report metrics to `http://<ip>:<port>/metrics`.