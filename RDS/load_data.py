import json
import os
from pathlib import Path
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def required(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


driver = required("DB_DRIVER")
host = required("DB_HOST")
port = int(required("DB_PORT"))
database = required("DB_NAME")
username = required("DB_USER")
password = required("DB_PASSWORD")
table_name = os.getenv("TABLE_NAME", "rds_records")
batch_id = str(uuid4())
data_file = Path(__file__).resolve().parents[1] / "files" / "customers.json"

with data_file.open(encoding="utf-8") as file:
    data = pd.DataFrame(json.load(file))

data.insert(0, "batch_id", batch_id)

database_url = URL.create(
    drivername=driver,
    username=username,
    password=password,
    host=host,
    port=port,
    database=database,
)
engine = create_engine(database_url)

try:
    data.to_sql(table_name, engine, if_exists="append", index=False)

    with engine.connect() as connection:
        loaded_rows = connection.execute(
            text(f"SELECT COUNT(*) FROM {table_name} WHERE batch_id = :batch_id"),
            {"batch_id": batch_id},
        ).scalar_one()

    if loaded_rows != len(data):
        raise RuntimeError(
            f"Validation failed: expected {len(data)} rows, found {loaded_rows}."
        )

    print(f"Loaded and validated {loaded_rows} rows in {table_name}.")
finally:
    engine.dispose()