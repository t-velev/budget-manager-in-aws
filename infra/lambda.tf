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

# 3. The AWS Lambda Function
resource "aws_lambda_function" "extract_account" {
  function_name = "extract_and_load_account"
  role          = aws_iam_role.lambda_exec_role.arn

  # Tell Lambda to use our Docker Image from ECR!
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}:account-latest"

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