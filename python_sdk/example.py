import dateutil
from flavius import GraphDatabase, DataType, TimeStamp
import boto3
import os


def upload_data():
    # boto3 is an AWS-SDK for connection of s3-protocol objstore
    client: boto3.client = boto3.client(
        "s3", # using s3 protocol
        aws_access_key_id="fvadmin", # minio access key id
        aws_secret_access_key="fvadmin123", # minio secret key
        region_name="cn-hongkong", # region, useless here
        endpoint_url="http://localhost:30900", # minio server address
        # config=boto3.session.Config(s3={'addressing_style': 'path'}),  # using Path-Style
    )
    cur_path = os.path.dirname(__file__)
    # upload_file(local_file_path, bucket_name, file_name on obj)
    client.upload_file(f"{cur_path}/data/users.csv", "flavius", "users.csv")
    client.upload_file(f"{cur_path}/data/knows.csv", "flavius", "knows.csv")


def print_database_info(driver: GraphDatabase):
    for namespace in driver.list_namespace():
        for graph in driver.list_graph(namespace):
            print(f"namespace: {namespace}, graph: {graph}")
            for vertex in driver.list_vertex(namespace, graph):
                print(f"vertex: {vertex}")
            for edge in driver.list_edge(namespace, graph):
                print(f"edge: {edge}")

        print()


if __name__ == "__main__":
    driver = GraphDatabase.driver("http://localhost:30000")
    driver.verify_connectivity()

    ns = "ns"
    g = "g"

    # create namespace and graph
    driver.create_namespace(ns)
    driver.create_graph(g, namespace=ns)

    # create vertex table
    driver.create_vertex_table(
        "User",
        [
            ("col1", DataType.INTEGER, False),  # NOT NULL
            ("col2", DataType.STRING),
            ("col3", DataType.BOOL),
            ("col4", DataType.FLOAT),
            ("col5", DataType.TIMESTAMP),
        ],
        "col1",  # primary key
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
        'BLOCKING IMPORT VERTEX User COLUMNS("col1"=$0, "col2"=$1, "col3"=$2, "col4"=$3, "col5"=$4) '
        "FROM 's3://flavius/users.csv' WITH (region = 'cn-hongkong', "
        "access_key_id = 'fvadmin', secret_access_key = 'fvadmin123', endpoint = 'http://localhost:30900') "
        "FORMAT AS CSV (has_header = false, delimiter = ',')",
        namespace=ns,
        graph=g,
    )  # Returns None
    driver.execute_query(
        'BLOCKING IMPORT EDGE knows FROM ("col1"=$1) TO ("col1"=$2) COLUMNS("col1"=$0) '
        "FROM 's3://flavius/knows.csv' WITH (region = 'cn-hongkong', "
        "access_key_id = 'fvadmin', secret_access_key = 'fvadmin123', endpoint = 'http://localhost:30900') "
        "FORMAT AS CSV (has_header = false, delimiter = ',')",
        namespace=ns,
        graph=g,
    )  # Returns None

    # execute query
    records, keys = driver.execute_query(
        "MATCH ()-[r:knows]->() RETURN r",
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
        "MATCH (n:User) WHERE n.col1 in $ids AND n.col5 > $timestamp "
        "MATCH (n:User) WHERE n.col1 in $ids "
        "RETURN n.__vid__, n.__label__, n.col1, n.col2, n.col3, n.col4, n.col5",
        namespace=ns,
        graph=g,
        parameters={"ids": [1, 3], "timestamp": flavius_ts},
    )
    for record in records:
        for key in keys:
            print(f"{key}: {record[key]}, type: {type(record[key])}")
        print()

    driver.close()
