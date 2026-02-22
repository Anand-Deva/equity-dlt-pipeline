# Use a lightweight Python image
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Install system dependencies for Postgres (psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project specification files
COPY pyproject.toml .

COPY uv.lock* . 

# to uv install without a virtualenv
RUN UV_SYSTEM_PYTHON=1 uv pip install .

# Copy the application code
COPY . .

# Change permission for executable shell script
RUN chmod +x script.sh

# Run the shell script
CMD ["./script.sh"]