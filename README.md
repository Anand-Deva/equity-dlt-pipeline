# 📊 Data Load Tool (dlt) – Stock Data Ingestion Project

This repository contains a **dlt-based data ingestion pipeline** that loads stock market data from multiple sources into a PostgreSQL database.

---

## 🔎 Data Sources

- `yfinance`
- `stockdata`

The project uses **Docker Compose** to containerize:

- The **dlt ingestion application**
- A **PostgreSQL database**

This ensures a reproducible, isolated, and production-ready environment.

---

## 🐳 Architecture Overview

- Multi-stage Docker build using `uv`
- Dedicated Dockerfile for the dlt application
- PostgreSQL running in a separate container
- Managed via `docker-compose.yml`

---

## ⚙️ Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running  
- ✅ `pyproject.toml` includes:

```toml
dlt[postgres]
```

## Build & Start the Containers

From the project root (where docker-compose.yml is located):
```bash
docker compose up --build -d
```

This will:
    * Build the dlt application image
    * Start PostgreSQL
    * Launch the ingestion pipeline

## Working with PostgreSQL Data
After ingestion completes, you can connect to the PostgreSQL container.

### Access the PostgreSQL container
```bash
docker exec -it <container-name> psql -U <user> -d <database>
```

### Set the Correct Schema (Important)
dlt loads data into a dataset (schema).
Make sure to set the search path:
```bash
SET search_path TO <dataset-name>, public;
```

## Stopping the Environment
```bash
docker compose down
```
To remove volumes as well:
```bash
docker compose down -v
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
