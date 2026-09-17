import os
from pathlib import Path

import boto3
import duckdb
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

bucket = os.getenv("S3_BUCKET")
if not bucket:
    raise ValueError("Missing required environment variable: S3_BUCKET")

folder = Path(__file__).resolve().parents[1] / "files"
image_path = folder / "downloaded_image.png"
s3 = boto3.client("s3")

s3.download_file(bucket, "images/source_image.png", str(image_path))
print(f"Downloaded image: {image_path.name}")

connection = duckdb.connect()
connection.execute("INSTALL httpfs")
connection.execute("LOAD httpfs")
connection.execute(
    """
    CREATE OR REPLACE SECRET aws_credentials (
        TYPE S3,
        PROVIDER credential_chain
    )
    """
)
rows = connection.execute(
    """
    SELECT city, COUNT(*) AS records, ROUND(SUM(amount), 2) AS total_amount
    FROM read_parquet(?, hive_partitioning = true)
    GROUP BY city
    ORDER BY total_amount DESC
    """,
    [f"s3://{bucket}/data/customers/**/*.parquet"],
).fetchall()
connection.close()

print("Sales by city:")
for city, records, total_amount in rows:
    print(f"{city}: {records} records, total amount = {total_amount}")