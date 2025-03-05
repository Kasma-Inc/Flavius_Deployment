import time
import dateutil
from flavius import Client, DataType, GraphDatabase, TimeStamp
from minio import Minio
import os


def upload_data():
    client = Minio(
        "minio:9000", access_key="fvadmin", secret_key="fvadmin123", secure=False
    )
    cur_path = os.path.dirname(__file__)
    client.fput_object("flavius", "users.csv", f"{cur_path}/data/users.csv")
    client.fput_object("flavius", "knows.csv", f"{cur_path}/data/knows.csv")


def print_database_info(driver: Client):
    for namespace in driver.list_namespace():
        for graph in driver.list_graph(namespace):
            print(f"namespace: {namespace}, graph: {graph}")
            for vertex in driver.list_vertex(namespace, graph):
                print(f"vertex: {vertex}")
            for edge in driver.list_edge(namespace, graph):
                print(f"edge: {edge}")

        print()


if __name__ == "__main__":
    driver = GraphDatabase.driver("http://fe:30000")
    driver.verify_connectivity()

    ns = "ns" + str(int(time.time()))
    g = "g"

    # create namespace and graph
    driver.create_namespace(ns)
    driver.create_graph(g, namespace=ns)

    # create vertex table
    driver.create_vertex_table(
        "User",
        [
            ("integer", DataType.INTEGER, False),  # NOT NULL
            ("bool", DataType.BOOL),
            ("string", DataType.STRING),
            ("float", DataType.FLOAT),
            ("date", DataType.DATE),
            ("time", DataType.TIME),
            ("datetime", DataType.DATETIME),
            ("timestamp", DataType.TIMESTAMP),
        ],
        "integer",  # primary key
        namespace=ns,
        graph=g,
    )

    # create edge table
    driver.create_edge_table(
        "knows",
        source_vertex="User",
        target_vertex="User",
        columns=[
            ("col1", DataType.FLOAT),
        ],
        directed=True,
        namespace=ns,
        graph=g,
    )

    print_database_info(driver)

    # upload data
    upload_data()

    # import data
    driver.execute_query(
        "BLOCKING IMPORT VERTEX User COLUMNS"
        '("integer"=$0, "bool"=$1, "string"=$2, "float"=$3, "date"=$4, "time"=$5, "datetime"=$6, "timestamp"=$7) '
        "FROM 'oss://flavius/users.csv' WITH (region = 'cn-hongkong', "
        "access_key_id = 'fvadmin', secret_access_key = 'fvadmin123', endpoint = 'http://minio:9000') "
        "FORMAT AS CSV (has_header = false, delimiter = ',')",
        namespace=ns,
        graph=g,
    )  # Returns None
    driver.execute_query(
        'BLOCKING IMPORT EDGE knows FROM ("integer"=$1) TO ("integer"=$2) COLUMNS("col1"=$0) '
        "FROM 'oss://flavius/knows.csv' WITH (region = 'cn-hongkong', "
        "access_key_id = 'fvadmin', secret_access_key = 'fvadmin123', endpoint = 'http://minio:9000') "
        "FORMAT AS CSV (has_header = false, delimiter = ',')",
        namespace=ns,
        graph=g,
    )  # Returns None

    # execute query
    records, keys = driver.execute_query(
        "MATCH ()-[r:knows]->() WHERE r.col1 <= 0.75 RETURN r",
        namespace=ns,
        graph=g,
    )
    for record in records:
        for key in keys:
            print(f"{key}: {record[key]}, type: {type(record[key])}")
        print()

    # execute query with parameters
    ts = dateutil.parser.parse("2024-01-02 02:34:00Z")
    flavius_ts = TimeStamp(ts)
    records, keys = driver.execute_query(
        "MATCH (n:User) WHERE n.integer in $ids AND n.timestamp > $timestamp "
        "RETURN n.__vid__, n.__label__, n.integer, n.bool, n.string, n.float, n.date, n.time, n.datetime, n.timestamp",
        namespace=ns,
        graph=g,
        parameters={"ids": [1, 3], "timestamp": flavius_ts},
    )
    for record in records:
        for key in keys:
            print(f"{key}: {record[key]}, type: {type(record[key])}")
        print()

    driver.close()