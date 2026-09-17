import os
from pathlib import Path

import duckdb
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


root = Path(__file__).resolve().parents[1]
load_dotenv(root / ".env")


def required(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


host = required("REDSHIFT_HOST")
port = int(required("REDSHIFT_PORT"))
database = required("REDSHIFT_NAME")
username = required("REDSHIFT_USER")
password = required("REDSHIFT_PASSWORD")
schema_name = required("REDSHIFT_SCHEMA")
table_name = required("REDSHIFT_TABLE")

table = f'"{schema_name}"."{table_name}"'
parquet_folder = root / "files" / "customers"
parquet_path = parquet_folder / "**" / "*.parquet"

duckdb_connection = duckdb.connect()
data = duckdb_connection.execute(
    "SELECT * FROM read_parquet(?, hive_partitioning = true)",
    [str(parquet_path)],
).fetchdf()
duckdb_connection.close()

database_url = URL.create(
    drivername="redshift+psycopg2",
    username=username,
    password=password,
    host=host,
    port=port,
    database=database,
)
engine = create_engine(database_url)

with engine.begin() as connection:
    connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
    connection.execute(
        text(
            f"CREATE TABLE {table} ("
            "name VARCHAR(100), city VARCHAR(50), age INTEGER, "
            "status VARCHAR(20), amount DECIMAL(10, 2))"
        )
    )
    data.to_sql(
        table_name,
        con=connection,
        schema=schema_name,
        if_exists="append",
        index=False,
        method="multi",
    )

engine.dispose()

print(f"Created and loaded {len(data)} rows into {schema_name}.{table_name}.")