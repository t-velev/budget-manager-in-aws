# 1. Amazon S3 Bucket (The Data Lake) - LOOKED UP, NOT MANAGED
# The bucket also holds Databricks' Unity Catalog storage (__unitystorage/), so it must
# survive `terraform destroy`. Terraform only reads it; it never creates or deletes it.
data "aws_s3_bucket" "data_lake" {
  bucket = "aws-budget-manager-datalake-${data.aws_caller_identity.current.account_id}"
}

# 2. IAM Role: Give AWS Glue permission to read S3 and write to CloudWatch logs
resource "aws_iam_role" "glue_crawler_role" {
  name                 = "budget-manager-glue-crawler-role"
  permissions_boundary = local.permissions_boundary_arn

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

# Read-only access to the raw_notion/ prefix of the data lake (replaces AmazonS3FullAccess)
resource "aws_iam_role_policy" "glue_s3_read" {
  name = "read-raw-notion"
  role = aws_iam_role.glue_crawler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = ["${data.aws_s3_bucket.data_lake.arn}/raw_notion/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [data.aws_s3_bucket.data_lake.arn]
      }
    ]
  })
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
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/account/"
  }

  s3_target {
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/category/"
  }

  s3_target {
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/subcategory/"
  }

  s3_target {
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/year/"
  }

  s3_target {
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/month/"
  }

  s3_target {
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/budget/"
  }

  s3_target {
    path = "s3://${data.aws_s3_bucket.data_lake.bucket}/raw_notion/transaction/"
  }
}

# Output the bucket name so we can use it in Python
output "s3_bucket_name" {
  value = data.aws_s3_bucket.data_lake.bucket
}