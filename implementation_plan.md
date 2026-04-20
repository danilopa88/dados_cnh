# Modern Data Stack for CNH Data (Detailed Plan)

This project builds a complete **Data Lakehouse** architecture on Windows using Docker Compose. The goal is to ingest monthly CNH CSV data from government portals, store it in an Iceberg format, and provide a professional BI and transformation layer.

## Implementation Details & Workflow

### 1. Ingestion (ELT) with `dlt`
- **What it does**: `dlt` (Data Load Tool) is a Python library that simplifies loading data. We will create a script that iterates through the months, fetches the CSVs from the government portal, and loads them into the Bronze layer.
- **Benefits**: It automatically detects the schema, handles table creation, and keeps track of which months were already imported (state management).

### 2. Storage (Data Lakehouse) with MinIO & Apache Iceberg
- **Object Storage**: **MinIO** acts as your local "S3". It will store the raw CSVs (Bronze) and the Iceberg data files.
- **Table Format**: **Apache Iceberg** is used instead of traditional Parquet files. It allows for:
  - **ACID Transactions**: No more corrupted tables if a write fails.
  - **Schema Evolution**: You can add/rename columns without rebuilding the table.
  - **Time Travel**: Query how the data looked last month.
- **Catalog**: **Project Nessie** acts as the catalog for Iceberg. It provides "Git for Data" features (branching/merging), allowing you to experiment with data in a branch before "merging" it to main.

### 3. Compute & Query with Trino
- **Role**: **Trino** is the high-performance SQL engine that reads the Iceberg tables in MinIO. It is the bridge between storage and the user/BI tools.
- **Why Trino?**: It's designed for massive scale and speed, and it's vendor-neutral.

### 4. Transformation (Modeling) with SQLMesh
- **Alternative to dbt**: **SQLMesh** is a modern transformation tool.
- **Key Feature**: **Virtual Environments**. When you change a SQL model, SQLMesh creates a virtual environment to show you the impact *before* you apply it to production. It handles data backfills automatically and efficiently.
- **Structure**: `Bronze` (Raw) -> `Silver` (Cleaned/Typed) -> `Gold` (Aggregated/Business Metrics).

### 5. Orchestration with Apache Airflow
- **Role**: The "Conductor". It schedules the `dlt` ingestion, then the `SQLMesh` transformations, and finally the quality checks.
- **Custom Docker Image**: I will provide a Dockerfile for Airflow that includes all necessary providers (Trino, SQLMesh, dlt).

### 6. Visualization with Apache Superset
- **Role**: Professional BI tool to create dashboards. It connects directly to Trino.

### 7. Observability with Great Expectations (GX)
- **Role**: Data Quality. We define "Expectations" (e.g., "The CNH category must be A, B, C, D, or E"). GX runs during the pipeline to ensure bad data doesn't reach the Gold layer.

## Windows & Docker Considerations

> [!IMPORTANT]
> **Docker on Windows**: There are no problems setting this up on Windows as long as you use **Docker Desktop with the WSL2 backend**. 
> - **Recommendation**: Ensure you have at least **16GB of RAM**.
> - **Performance**: I will configure Trino and Airflow with memory limits suitable for a local machine to prevent system freezing.

## Proposed Changes

### Infrastructure
- `docker-compose.yml`: All-in-one setup for MinIO, Nessie, Trino, Postgres, Airflow, and Superset.
- `trino/catalog/iceberg.properties`: Configuration for connecting Trino to Nessie and MinIO.

### Python Environment
- `requirements.txt`: Including `dlt`, `sqlmesh`, `trino-python-client`, and `great-expectations`.

### Ingestion & Pipeline
- `dlt/cnh_pipeline.py`: Script to fetch CSVs from the government portal.
- `airflow/dags/cnh_workflow.py`: The main DAG orchestrating the end-to-end flow.

## Open Questions

1. **Specific URL**: Could you share one specific URL of the government page so I can check the exact CSV structure and link pattern?
2. **WSL2**: Do you have Docker Desktop installed with WSL2 enabled?

## Verification Plan
1. **Infrastructure**: `docker-compose up -d` and check health of all services.
2. **Ingestion**: Run the `dlt` script and verify files in MinIO Browser.
3. **Transformation**: Run `sqlmesh plan` and check if Silver/Gold tables are created in Iceberg.
4. **BI**: Connect Superset to Trino and visualize one table.
