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

### Job

#### Create Import Job

##### Import Vertex Job

**Syntax**

```sql
IMPORT VERTEX <vertex_table_name>
COLUMNS (<vertex_property_name> = $<file_column_index>, <vertex_property_name> = $<file_column_index>, ... )
FROM <import_file_source_uri> sourceOptions
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
  FROM "s3://kasma-fileio-ci/tinysoc/vPerson.csv" 
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
FROM <import_file_source_uri> sourceOptions
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
  MATCH (n:Person) RETURN array_sort_desc(n.friends, x -> x.age) AS sorted_friends;
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
