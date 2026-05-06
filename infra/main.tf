# 1. Define the Cloud Provider and Region
provider "aws" {
  region = "eu-central-1"
}

# 2. Data Source: Ask an external service what my current public IP address is
data "http" "myip" {
  url = "https://ipv4.icanhazip.com"
}

# 3. Security Group: The Virtual Firewall
resource "aws_security_group" "rds_sg" {
  name        = "budget-manager-rds-sg"
  description = "Allow inbound PostgreSQL traffic from my IP"

  # INGRESS (Incoming traffic): Allow Port 5432 from anywhere (for AWS Lambda)
  ingress {
    description = "PostgreSQL from the internet"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks =["0.0.0.0/0"]
  }

  # EGRESS (Outgoing traffic): Allow the database to talk to the internet (needed for updates)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. Amazon RDS: The PostgreSQL Database
resource "aws_db_instance" "budget_db" {
  identifier        = "aws-budget-manager-db"
  db_name           = "aws_budget_manager"  
  engine            = "postgres"
  engine_version    = "18"
  instance_class    = "db.t3.micro" # This is the Free Tier eligible instance
  allocated_storage = 20            # 20 GB is the max Free Tier storage
  storage_type      = "gp2"

  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = true # So the local VS Code can reach it
  skip_final_snapshot    = true # So we can cleanly delete it without AWS saving backups
}

# 5. Output: Print the database connection address after it builds
output "db_endpoint" {
  value       = aws_db_instance.budget_db.endpoint
  description = "The connection endpoint for the database"
}