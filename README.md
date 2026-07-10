# AWS Serverless Data Lakehouse: Notion Budget Manager

## Project Objective

This is the "Cloud Evolution" of my personal [Notion Budget Manager portfolio project](https://github.com/t-velev/budget-manager), which was built locally.

Coming from 1.5 years of experience in Data Warehousing, I had already built a robust local ELT pipeline using Docker-Compose, Postgres, dbt, and Airflow.

However, modern Data Engineering needed hands-on experience with cloud platforms, Infrastructure as Code (IaC), and decoupled storage/compute architectures.

Instead of just clicking around the AWS UI, I used this project as a sandbox to migrate my entire local pipeline to AWS using **Terraform**.
The goal was to build a secure, serverless, automated Data Lakehouse entirely from scratch, keeping cloud costs strictly optimized (and surviving the AWS billing learning curve!).

## Tech Stack

*   **Source:** Notion API
*   **Ingestion (Compute):** AWS Lambda (Python, Pandas, SQLAlchemy, boto3)
*   **Data Lake (Storage):** Amazon S3
*   **Data Catalog:** AWS Glue & Amazon Athena
*   **Data Warehouse:** Amazon RDS (PostgreSQL 18)
*   **Transformation:** dbt-core via AWS ECS Fargate (Serverless Docker)
*   **Orchestration:** AWS Step Functions
*   **Scheduling:** Amazon EventBridge
*   **Infrastructure as Code:** HashiCorp Terraform
*   **CI/CD & Testing:** GitHub Actions, pytest, pytest-mock
*   **Dev Environment:** VS Code Dev Containers, Makefile, Git
*   **Support:** Google Gemini (Acting as my virtual Senior Data Engineer mentor).

## Architecture Overview

This project transitions from a traditional database-only ELT flow to a modern Data Lakehouse pattern:
- **Extract & Double-Write (AWS Lambda):** Python scripts run in serverless Docker containers. They pull from the Notion API and do a "double write": saving a permanent raw CSV to **Amazon S3** (Data Lake) and performing an idempotent upsert into **Amazon RDS** (Data Warehouse).
- **Orchestration (Step Functions):** Replaced Apache Airflow. A visual state machine handles sequential execution (to respect Notion's API rate limits), passes the unified `run_id` state dynamically, and includes conditional `Choice` logic for initial vs. incremental loads.
- **Transformation (ECS Fargate):** Serverless container orchestration spins up to execute `dbt build`, processing Slowly Changing Dimensions (SCD2) and generating Kimball dimensional models, then scales back to zero.
- **Data Cataloging (Glue & Athena):** An AWS Glue Crawler scans the raw CSV files in S3, making the raw "Bronze" layer instantly queryable via standard SQL in Amazon Athena without touching the Postgres database.
- **Automation (EventBridge):** Acts as a cloud cron job, triggering the Step Function automatically at 2:00 AM local time.

## The End-to-End Data Flow
- **The Trigger (EventBridge):** At a predefined time, Amazon EventBridge wakes up and pushes the "Start" button on the AWS Step Function, injecting a JSON payload (is_initial_load: false).
- **The Extraction (Lambda):** The Step Function triggers the Python Docker containers running in AWS Lambda sequentially. The Lambda functions reach out to the Notion API over the public internet and pull the JSON data into a Pandas DataFrame.
- **The "Double Write" Fork:**
    - **Path A (The Data Lake):** The Lambda function converts the data to a CSV file named with the unique run_id and uploads it directly to Amazon S3.
    - **Path B (The Data Warehouse):** The same Lambda function securely connects to the Amazon RDS PostgreSQL database and executes an idempotent DELETE/INSERT into the raw schema.
- **The Audit (Lambda):** The script pulls a "skinny" payload of IDs from Notion, compares it against the raw schema in RDS, and performs a hard-delete synchronization, logging the row counts to the sys_etl_stats table.
- **The Transformation (ECS Fargate):** Once all extraction Lambdas finish successfully, the Step Function triggers a serverless Docker container in ECS Fargate. This container boots up, runs dbt build, reads the raw schema, processes the Slowly Changing Dimensions (SCD Type 2), and builds the final Kimball dimensional models in the warehouse schema.
- **The Catalog (Glue):** Later, an AWS Glue Crawler scans the S3 bucket, automatically detects the schemas of the raw CSV files, and updates the Data Catalog, making the raw data instantly queryable via Amazon Athena.

## Key Technical Challenges & Learnings

Migrating to the cloud exposed me to real-world DevOps and Cloud Engineering hurdles that you simply don't face on a local machine:

- **Software Engineering Rigor (Testing & CI/CD)**
    - **The Problem:** Manually testing extraction scripts against a live API is slow, risks data corruption, and violates rate limits. Furthermore, deploying infrastructure and code manually via the terminal is error-prone and violates DevOps best practices.
    - **The Solution:** I refactored the extraction Python scripts into a "Hub and Spoke" pattern, separating execution logic from the core pipeline engine. This allowed me to write a comprehensive unit testing suite using `pytest`. I used `pytest-mock` to fake Notion API paginated responses and SQLAlchemy database connections, ensuring the logic was mathematically sound without needing internet access. Finally, I built a **GitHub Actions** CI/CD pipeline that automatically provisions an Ubuntu runner, installs dependencies, and executes the test suite on every push.

- **The "Serverless Docker" Trap (C-Compilers & Cold Starts)**
    - **The Problem:** Deploying Python with `pandas` and `psycopg2` (which requires C-compilers) to AWS Lambda and ECS Fargate. Initially, `dbt-postgres` failed to compile in the cloud because I was using a lightweight `-slim` Linux image.
    - **The Solution:** I learned how to write Dockerfiles that install `gcc` and `libpq-dev` for the build step, minimizing the final image size to reduce AWS network pull times and mitigate "Cold Start" delays. I also learned to disable Docker provenance attestations to ensure AWS Lambda accepts the images.

- **Cloud Networking & Security (IAM & VPCs)**
    - **The Problem:** How does a serverless Lambda function talk to the public Notion API *and* a secure private RDS database without racking up a $32/month AWS NAT Gateway bill?
    - **The Solution:** I grasped the "Enterprise vs. Learner" trade-offs. I opted to keep Lambda in the public network for free internet access, opened the RDS Security Group to the internet (`0.0.0.0/0`), but secured the database using strong, Terraform-injected variables. I also learned to write strict IAM Policies (Principle of Least Privilege) so services could only trigger exact resources.

- **Dynamic State Management without Airflow**
    - **The Problem:** In my local project, Airflow easily injected a `run_id` (timestamp) into all scripts. In AWS, Lambda functions and Fargate tasks run in isolation and don't share state.
    - **The Solution:** I used Amazon States Language (ASL) in Step Functions to grab the AWS Execution Start Time, pass it to my Python Lambda (which formatted it to Sofia local time using `pendulum`), and return it. I then used `States.JsonToString` to dynamically inject it into the `dbt` Docker container via ECS container overrides.

- **Cloud FinOps & The AWS Billing Reality**
    - **The Problem:** Expecting a $0.00 bill but seeing charges for Public IPv4 addresses and RDS compute.
    - **The Solution:** I learned the crucial difference between the "Classic Free Tier" and the "Credit-based Free Plan." I learned how to analyze AWS invoices and implemented a strategy to stop the RDS instance during downtime while relying on `terraform apply` / `destroy` and `Makefiles` to quickly spin infrastructure up and down.

- **Git History & Secrets Management**
    - **The Problem:** Accidentally hardcoding my AWS Account ID in a `Makefile` commit.
    - **The Solution:** Instead of wiping the repository and losing my commit history, I learned how to use Git Interactive Rebasing (`git rebase -i`), edited the past commit to use environment variables (`include .env`), and safely rewrote the timeline without losing my project's story.

## Data Warehouse Structure
The data structure remains consistent with my local DW project, utilizing Kimball dimensional modeling:
- **S3 Data Lake:** `raw_notion/` directory containing immutable, timestamped CSV files of every API pull.
- **RDS raw schema:** A direct replica for staging.
- **RDS warehouse schema:** SCD2 Dimensions (`dim_account`, `dim_category`, etc.) and Fact tables (`fact_transaction`, `fact_budget`) with rigorous referential integrity enforced by custom dbt post-hooks.
- **Audit:** Custom Python and dbt macros updating a shared `sys_etl_stats` table for deep visibility into extracted, loaded, and hard-deleted row counts per run.

## How to Deploy and Run
Because of the private nature of my Notion data, the project isn’t ready for others to run.

## Future Improvements and Next Steps
By deliberately splitting the storage (S3) and metadata (Glue), I have built the foundational layer required for a modern Data Lakehouse.

My next planned step in my Data Engineering journey is to integrate **Databricks** into this AWS environment.