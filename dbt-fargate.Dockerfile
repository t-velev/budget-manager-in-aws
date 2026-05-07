# Use a lightweight Python base image
FROM python:3.12-slim-bookworm

# Install git, gcc (C-compiler), and libpq-dev (Postgres headers)
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dbt-postgres directly
RUN pip install --no-cache-dir dbt-postgres==1.8.0

# Set the working directory inside the container
WORKDIR /usr/app/dbt

# Copy the entire dbt project into the container
COPY dbt/budget_manager /usr/app/dbt/budget_manager

# Set the working directory to where the dbt_project.yml lives
WORKDIR /usr/app/dbt/budget_manager

# When the Fargate container wakes up, run dbt build!
CMD ["dbt", "build"]