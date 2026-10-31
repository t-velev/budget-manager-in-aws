# 1. Define the Cloud Provider and Region
provider "aws" {
  region = "eu-central-1"

  # Safety net: Terraform refuses to run against any other AWS account
  allowed_account_ids = [var.aws_account_id]

  # Every resource gets this tag, which makes the post-destroy leftover audit easy
  default_tags {
    tags = {
      Project = "budget-manager"
    }
  }
}

data "aws_caller_identity" "current" {}

locals {
  # Every IAM role this project creates MUST carry this boundary.
  # The terraform-deployer role is only allowed to create roles that have it.
  permissions_boundary_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/admin-guard-boundary"
}

# 2. Security Group: The Virtual Firewall
resource "aws_security_group" "rds_sg" {
  name        = "budget-manager-rds-sg"
  description = "Allow inbound PostgreSQL traffic (Lambda runs outside a VPC, so no fixed source IP). Deploy windows must stay short; always run 'make down'."

  # INGRESS (Incoming traffic): Allow Port 5432 from anywhere (for AWS Lambda)
  ingress {
    description = "PostgreSQL from the internet"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # EGRESS (Outgoing traffic): Allow the database to talk to the internet (needed for updates)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Amazon RDS: The PostgreSQL Database
resource "aws_db_instance" "budget_db" {
  identifier        = "aws-budget-manager-db"
  db_name           = "aws_budget_manager"
  engine            = "postgres"
  engine_version    = "18"
  instance_class    = "db.t3.micro" # The deployer role refuses anything bigger than db.t3.micro / db.t4g.micro
  allocated_storage = 20            # The deployer role refuses anything above 20 GB
  storage_type      = "gp2"

  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = true # So the local VS Code can reach it
  skip_final_snapshot    = true # So we can cleanly delete it without AWS saving backups
}

# 4. Output: Print the database connection address after it builds
output "db_endpoint" {
  value       = aws_db_instance.budget_db.endpoint
  description = "The connection endpoint for the database"
}
