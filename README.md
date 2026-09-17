# Ejercicios de AWS

Ejercicios prácticos de servicios de datos de AWS usando Python, SQLAlchemy, boto3, DuckDB y Gremlin.

## Requisitos

- Conda
- Python 3.12
- Credenciales de AWS configuradas localmente
- Acceso a los servicios que se quieran probar

## Preparar el entorno

Desde la raíz del proyecto, ejecuta el script con `source` para que la activación permanezca en la terminal:

```bash
source setup_env.sh
```

El script crea el entorno Conda `aws` con Python 3.12, instala `requirements.txt` y activa el entorno.

## Configuración

Crea un archivo `.env` en la raíz del proyecto. Este archivo no se versiona.

Variables utilizadas:

```env
# RDS
DB_HOST=
DB_PORT=5432
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_DRIVER=postgresql+psycopg
TABLE_NAME=rds_records

# DynamoDB
DDB_REGION=
DDB_TABLE=customers

# DocumentDB
DOCDB_HOST=
DOCDB_PORT=27017
DOCDB_NAME=
DOCDB_USER=
DOCDB_PASSWORD=
DOCDB_COLLECTION=customers

# S3
S3_BUCKET=

# Redshift
REDSHIFT_HOST=
REDSHIFT_PORT=5439
REDSHIFT_NAME=
REDSHIFT_USER=
REDSHIFT_PASSWORD=
REDSHIFT_SCHEMA=public
REDSHIFT_TABLE=customers
```

Configura las credenciales de AWS con:

```bash
aws configure
```

## Datos compartidos

Los datos comunes están en `files/`:

- `customers.json`: registros utilizados por los ejercicios de bases de datos.
- `source_image.png`: imagen que se carga a S3.
- `customers/`: archivos Parquet particionados por ciudad.

Los Parquet deben estar disponibles con una estructura similar a:

```text
files/customers/city=Madrid/data_0.parquet
files/customers/city=Barcelona/data_0.parquet
```

## Ejercicios

### RDS

Carga los registros de `files/customers.json` en una tabla PostgreSQL y valida la cantidad de filas:

```bash
python RDS/load_data.py
```

### DocumentDB

Carga los documentos de `files/customers.json` y consulta clientes activos. Requiere configurar las variables `DOCDB_*` en `.env` y ejecutar:

```bash
python DocumentDB/load_data.py
```

### DynamoDB

Crea la tabla si no existe, carga los documentos y recupera un elemento mediante `get_item`:

```bash
python DynamoDB/load_data.py
```

### S3

Sube las particiones Parquet y la imagen al bucket configurado:

```bash
python S3/upload_files.py
```

Después descarga la imagen y consulta directamente los Parquet remotos con DuckDB:

```bash
python S3/download_and_query.py
```

Los objetos Parquet se almacenan bajo:

```text
s3://<bucket>/data/customers/
```

### Redshift

Lee los Parquet locales con DuckDB y carga los datos en una tabla Redshift usando SQLAlchemy:

```bash
python Redshift/create_table.py
```

Consulta la tabla desde otro script:

```bash
python Redshift/query_table.py
```

### Athena

La consulta SQL para crear una tabla externa sobre los Parquet y agrupar los datos está en:

```text
Athena/query.sql
```

Actualiza el bucket de la sentencia SQL si utilizas otro bucket.
