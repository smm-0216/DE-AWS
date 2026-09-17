import json
import os
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv


folder = Path(__file__).parent
load_dotenv(folder.parent / ".env")


def required(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


region = required("DDB_REGION")
table_name = required("DDB_TABLE")
dynamodb = boto3.resource("dynamodb", region_name=region)

try:
    table = dynamodb.create_table(
        TableName=table_name,
        # KeyType HASH indica que "id" es la clave de partición.
        # DynamoDB usa su valor para decidir en qué partición guardar el elemento.
        # RANGE se usaría para una clave de ordenamiento adicional.
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        # AttributeType S significa String, es decir, texto.
        # Otros tipos disponibles son N (Number) y B (Binary).
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        # AWS cobra según las solicitudes realizadas, sin reservar capacidad.
        BillingMode="PAY_PER_REQUEST",
    )
    table.wait_until_exists()
except dynamodb.meta.client.exceptions.ResourceInUseException:
    table = dynamodb.Table(table_name)

data_file = folder.parent / "files" / "customers.json"
with data_file.open(encoding="utf-8") as file:
    documents = json.load(file, parse_float=Decimal)

load_id = str(uuid4())
# batch_writer agrupa las escrituras y las reintenta si alguna no se procesa.
with table.batch_writer() as batch:
    for number, document in enumerate(documents, start=1):
        document["id"] = f"customer:{number}"
        document["load_id"] = load_id
        batch.put_item(Item=document)

# get_item recupera directamente un elemento usando su clave primaria "id".
first_item = table.get_item(Key={"id": "customer:1"}).get("Item")
print("Item retrieved with get_item:")
print(first_item)

# scan recorre los elementos de la tabla y devuelve los que cumplen el filtro.
loaded_documents = table.scan(
    FilterExpression=Attr("load_id").eq(load_id)
)["Items"]
if len(loaded_documents) != len(documents):
    raise RuntimeError(
        f"Validation failed: expected {len(documents)} documents, "
        f"found {len(loaded_documents)}."
    )

response = table.scan(
    FilterExpression=Attr("load_id").eq(load_id) & Attr("status").eq("active")
)
active_documents = response["Items"]

print(f"Loaded and validated {len(loaded_documents)} documents into {table_name}.")
print("Active customers:")
for document in active_documents:
    print(document)
