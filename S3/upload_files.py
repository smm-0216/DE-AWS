import os
from pathlib import Path

import boto3
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

bucket = os.getenv("S3_BUCKET")
if not bucket:
    raise ValueError("Missing required environment variable: S3_BUCKET")

folder = Path(__file__).resolve().parents[1] / "files"
parquet_folder = folder / "customers"
parquet_files = sorted(parquet_folder.rglob("*.parquet"))
if not parquet_files:
    raise FileNotFoundError(
        "No Parquet files found. Run partition_sample_data.py first."
    )

s3 = boto3.client("s3")

for parquet_file in parquet_files:
    parquet_key = "data/customers/" + parquet_file.relative_to(parquet_folder).as_posix()
    s3.upload_file(str(parquet_file), bucket, parquet_key)

s3.upload_file(
    str(folder / "source_image.png"),
    bucket,
    "images/source_image.png",
)

print(f"Uploaded {len(parquet_files)} Parquet files and image to bucket: {bucket}")