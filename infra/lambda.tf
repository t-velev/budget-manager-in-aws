# Fetch the exact SHA256 digest of the latest image in ECR
data "aws_ecr_image" "lambda_image" {
  repository_name = aws_ecr_repository.lambda_repo.name
  image_tag       = "master-latest"
}

# 1. IAM Role: The "Identity" of the Lambda function
resource "aws_iam_role" "lambda_exec_role" {
  name = "budget-manager-lambda-role"

  # "Assume Role Policy" allows the Lambda service to use this identity
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement =[{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# 2. IAM Policies: What is the Lambda allowed to do?
# Allow it to write logs so we can debug it
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Allow it to upload files to Amazon S3
resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# 3. The AWS ACCOUNT Lambda Function
resource "aws_lambda_function" "extract_account" {
  function_name = "extract_and_load_account"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_account.lambda_handler"]
  }

  timeout       = 120 # Give it 2 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST        = aws_db_instance.budget_db.address
      POSTGRES_DB          = aws_db_instance.budget_db.db_name
      POSTGRES_USER        = var.db_username
      POSTGRES_PASSWORD    = var.db_password
      S3_BUCKET_NAME       = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY       = var.notion_api_key
      NOTION_DB_ID_ACCOUNT = var.notion_db_id_account
    }
  }
}


# 4. The AWS CATEGORY Lambda Function
resource "aws_lambda_function" "extract_category" {
  function_name = "extract_and_load_category"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_category.lambda_handler"]
  }

  timeout       = 120 # Give it 2 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST         = aws_db_instance.budget_db.address
      POSTGRES_DB           = aws_db_instance.budget_db.db_name
      POSTGRES_USER         = var.db_username
      POSTGRES_PASSWORD     = var.db_password
      S3_BUCKET_NAME        = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY        = var.notion_api_key
      NOTION_DB_ID_CATEGORY = var.notion_db_id_category
    }
  }
}


# 5. The AWS SUBCATEGORY Lambda Function
resource "aws_lambda_function" "extract_subcategory" {
  function_name = "extract_and_load_subcategory"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_subcategory.lambda_handler"]
  }

  timeout       = 120 # Give it 2 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST            = aws_db_instance.budget_db.address
      POSTGRES_DB              = aws_db_instance.budget_db.db_name
      POSTGRES_USER            = var.db_username
      POSTGRES_PASSWORD        = var.db_password
      S3_BUCKET_NAME           = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY           = var.notion_api_key
      NOTION_DB_ID_SUBCATEGORY = var.notion_db_id_subcategory
    }
  }
}


# 6. The AWS YEAR Lambda Function
resource "aws_lambda_function" "extract_year" {
  function_name = "extract_and_load_year"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_year.lambda_handler"]
  }

  timeout       = 120 # Give it 2 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST     = aws_db_instance.budget_db.address
      POSTGRES_DB       = aws_db_instance.budget_db.db_name
      POSTGRES_USER     = var.db_username
      POSTGRES_PASSWORD = var.db_password
      S3_BUCKET_NAME    = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY    = var.notion_api_key
      NOTION_DB_ID_YEAR = var.notion_db_id_year
    }
  }
}


# 7. The AWS MONTH Lambda Function
resource "aws_lambda_function" "extract_month" {
  function_name = "extract_and_load_month"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_month.lambda_handler"]
  }

  timeout       = 120 # Give it 2 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST      = aws_db_instance.budget_db.address
      POSTGRES_DB        = aws_db_instance.budget_db.db_name
      POSTGRES_USER      = var.db_username
      POSTGRES_PASSWORD  = var.db_password
      S3_BUCKET_NAME     = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY     = var.notion_api_key
      NOTION_DB_ID_MONTH = var.notion_db_id_month
    }
  }
}


# 8. The AWS BUDGET Lambda Function
resource "aws_lambda_function" "extract_budget" {
  function_name = "extract_and_load_budget"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_budget.lambda_handler"]
  }

  timeout       = 600 # Give it 10 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST       = aws_db_instance.budget_db.address
      POSTGRES_DB         = aws_db_instance.budget_db.db_name
      POSTGRES_USER       = var.db_username
      POSTGRES_PASSWORD   = var.db_password
      S3_BUCKET_NAME      = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY      = var.notion_api_key
      NOTION_DB_ID_BUDGET = var.notion_db_id_budget
    }
  }
}


# 9. The AWS TRANSACTION Lambda Function
resource "aws_lambda_function" "extract_transaction" {
  function_name = "extract_and_load_transaction"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["extract_and_load_transaction.lambda_handler"]
  }

  timeout       = 600 # Give it 10 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST            = aws_db_instance.budget_db.address
      POSTGRES_DB              = aws_db_instance.budget_db.db_name
      POSTGRES_USER            = var.db_username
      POSTGRES_PASSWORD        = var.db_password
      S3_BUCKET_NAME           = aws_s3_bucket.data_lake.bucket
      NOTION_API_KEY           = var.notion_api_key
      NOTION_DB_ID_TRANSACTION = var.notion_db_id_transaction
    }
  }
}

# 10. The AWS RESET_RAW_NOTION_DATES Lambda Function
resource "aws_lambda_function" "reset_raw_notion_dates" {
  function_name = "reset_raw_notion_dates"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use the Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"

  # Override the CMD to tell this specific Lambda which script to run!
  image_config {
    command = ["reset_raw_notion_dates.lambda_handler"]
  }

  timeout       = 120 # Give it 2 minutes to run
  memory_size   = 256 # Give Pandas a little extra RAM to work with

  # Pass Terraform state directly into Lambda Environment Variables
  environment {
    variables = {
      POSTGRES_HOST     = aws_db_instance.budget_db.address
      POSTGRES_DB       = aws_db_instance.budget_db.db_name
      POSTGRES_USER     = var.db_username
      POSTGRES_PASSWORD = var.db_password
    }
  }
}