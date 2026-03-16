# 📊 Data Load Tool (dlt) &  Google Cloud Platform (GCP) 
This repository contains a **dlt-based data ingestion pipeline** that loads stock market data from multiple sources and depending on configuration it can load a local **PostgreSQL** or **Bigquery** & **GCS Bucket**.

---

## 🔎 Data Sources & Destinations

- **Sources**
  - `yfinance`
  - `stockdata`

- **Destinations (implementations)**
  - **PostgreSQL** (`yfinance_pipeline.py`)
  - **Google BigQuery** (`stockdata_pipeline.py`)
  - **GCS Bucket** (`storage_pipeline.py`)

The project uses **Docker Compose** to containerize:

- The **dlt ingestion application**
- A **PostgreSQL database** (for local testing)
- A **Google Cloud project** with BigQuery and Cloud Storage APIs enabled.
- A **service account JSON key** with write access to both BigQuery and GCS bucket.

This ensures a reproducible, isolated, and production-ready environment.  
For storing the local directory into GCS bucket run the python script `storage_pipeline.py` locally outside of Docker, as long as the required GCP credentials are available locally or via environment variables.

---

## 🐳 Architecture Overview

- Dedicated Dockerfile for the dlt application
- PostgreSQL running in a separate container
- Managed via `docker-compose.yml`

---

## ⚙️ Prerequisites

Before starting, ensure you have:

- ✅ **Docker Desktop** installed and running  
- ✅ `pyproject.toml` includes:

```toml
# for PostgreSQL, BigQuery, Google Cloud Storage
dlt[postgres, bigquery, filesystem] = "*"
```

## Build & Start the Containers

## Run in local machine

From the project root (where docker-compose.yml is located):
```bash
docker compose up --build -d
```

> The same container image is used for PostgreSQL and BigQuery pipelines; which destination is targeted is controlled by environment variables passed to the dlt command in `docker-compose.yml` or your shell.

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

## CI/CD & Deployment (AWS EKS)
This project uses GitHub Actions to automate the build-and-deploy process. Every push to the main branch triggers a container build, which is then deployed to Amazon EKS as a scheduled CronJob.

### Architecture

* Build: GitHub Actions builds the Docker image and tags it with the Git Commit SHA.
* Store: The image is pushed to Amazon ECR (Elastic Container Registry).
* Sync: GitHub Actions securely injects environment variables into a Kubernetes Secret.
* Deploy: The cronjob.yml is updated with the new image tag and applied to the EKS Cluster.
* Run: Kubernetes triggers the container on the defined schedule (e.g., every 15 minutes).

### Secret Management
Sensitive credentials (like Google Service Account keys) are stored in GitHub Secrets and injected into the cluster during the deployment step.

## Deployment Configuration

### GitHub Actions Workflow
The workflow is located at .github/workflows/deploy.yml. It uses OIDC to authenticate with AWS, removing the need for long-lived AWS Access Keys.

### Kubernetes CronJob
The scheduling and resource configuration are defined in cronjob.yml.

Schedule: 0/15 * * * * (Every 15 minutes)

Image Pull Policy: Uses the specific Commit SHA to ensure version consistency.

Environment: All secrets are mapped via envFrom into the container's environment variables.
---

## License

[MIT](https://choosealicense.com/licenses/mit/)