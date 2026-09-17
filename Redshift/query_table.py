import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


root = Path(__file__).resolve().parents[1]
load_dotenv(root / ".env")


def required(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


schema_name = required("REDSHIFT_SCHEMA")
table_name = required("REDSHIFT_TABLE")
if not schema_name.isidentifier() or not table_name.isidentifier():
    raise ValueError("REDSHIFT_SCHEMA and REDSHIFT_TABLE must be valid identifiers")

database_url = URL.create(
    drivername="redshift+psycopg2",
    username=required("REDSHIFT_USER"),
    password=required("REDSHIFT_PASSWORD"),
    host=required("REDSHIFT_HOST"),
    port=int(required("REDSHIFT_PORT")),
    database=required("REDSHIFT_NAME"),
)
engine = create_engine(database_url)
table = f'"{schema_name}"."{table_name}"'

with engine.connect() as connection:
    rows = connection.execute(
        text(
            f"""
            SELECT status,
                COUNT(*) AS records,
                ROUND(SUM(amount), 2) AS total_amount,
                ROUND(AVG(amount), 2) AS average_amount
            FROM {table}
            GROUP BY status
            ORDER BY total_amount DESC
            """
        )
    ).fetchall()

engine.dispose()

print("Sales by status:")
for status, records, total_amount, average_amount in rows:
    print(
        f"{status}: {records} records, total amount = {total_amount}, "
        f"average amount = {average_amount}"
    )