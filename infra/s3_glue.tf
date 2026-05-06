# 1. Amazon S3 Bucket (The Data Lake)
# Bucket names must be globally unique across all of AWS, so we add a random suffix
resource "aws_s3_bucket" "data_lake" {
  bucket        = "aws-budget-manager-datalake-${data.aws_caller_identity.current.account_id}"
  force_destroy = true # Allows us to delete the bucket later even if it has files in it
}

# Explicitly Block ALL Public Access
resource "aws_s3_bucket_public_access_block" "secure_lake" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Get current AWS account ID to make the bucket name unique
data "aws_caller_identity" "current" {}

# 2. IAM Role: Give AWS Glue permission to read S3 and write to CloudWatch logs
resource "aws_iam_role" "glue_crawler_role" {
  name = "AWSGlueServiceRole-BudgetManager"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
  })
}

# Attach standard AWS managed policies to the role
resource "aws_iam_role_policy_attachment" "glue_service_attach" {
  role       = aws_iam_role.glue_crawler_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy_attachment" "s3_read_attach" {
  role       = aws_iam_role.glue_crawler_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# 3. AWS Glue Catalog Database
resource "aws_glue_catalog_database" "budget_db" {
  name = "budget_manager_lakehouse"
}

# 4. AWS Glue Crawler
resource "aws_glue_crawler" "notion_crawler" {
  name          = "notion-raw-data-crawler"
  database_name = aws_glue_catalog_database.budget_db.name
  role          = aws_iam_role.glue_crawler_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw_notion/account/"
  }
}

# Output the bucket name so we can use it in Python
output "s3_bucket_name" {
  value = aws_s3_bucket.data_lake.bucket
}