import json
import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from pymongo import MongoClient


folder = Path(__file__).parent
load_dotenv(folder.parent / ".env")


data_file = folder.parent / "files" / "customers.json"
with data_file.open(encoding="utf-8") as file:
    documents = json.load(file)

load_id = str(uuid4())
for document in documents:
    document["load_id"] = load_id

client = MongoClient()
database_name = "your_database_name"
collection_name = "your_collection_name"
collection = client[database_name][collection_name]

try:
    collection.insert_many(documents)
    loaded_documents = collection.count_documents({"load_id": load_id})

    if loaded_documents != len(documents):
        raise RuntimeError(
            f"Validation failed: expected {len(documents)} documents, "
            f"found {loaded_documents}."
        )

    active_documents = collection.find(
        {"load_id": load_id, "status": "active", "age": {"$gt": 30}},
        {"_id": 0, "name": 1, "city": 1, "age": 1, "amount": 1},
    )

    print(f"Loaded and validated {loaded_documents} documents.")
    print("Active customers older than 30:")
    for document in active_documents:
        print(document)
finally:
    client.close()
