# 1. The ECS Cluster (Logical grouping)
resource "aws_ecs_cluster" "dbt_cluster" {
  name = "budget-manager-cluster"
}

# Attach Fargate Capacity Providers to the Cluster
resource "aws_ecs_cluster_capacity_providers" "dbt_cluster_cp" {
  cluster_name = aws_ecs_cluster.dbt_cluster.name

  capacity_providers =["FARGATE"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# 2. CloudWatch Log Group (Where dbt will print its output)
resource "aws_cloudwatch_log_group" "dbt_logs" {
  name              = "/ecs/dbt-budget-manager"
  retention_in_days = 7 # Automatically delete old logs to save money
}

# 3. IAM Role: Task Execution Role (Allows ECS to pull from ECR and push logs to CloudWatch)
resource "aws_iam_role" "ecs_execution_role" {
  name = "dbt-ecs-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement =[{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Attach AWS managed policy for standard ECS execution rights
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 4. The ECS Task Definition (The Blueprint)
resource "aws_ecs_task_definition" "dbt_task" {
  family                   = "dbt-budget-manager-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # 0.25 vCPU (More than enough for dbt)
  memory                   = "512" # 0.5 GB RAM
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  # The actual container configuration
  container_definitions = jsonencode([{
    name      = "dbt-container"
    image     = "${aws_ecr_repository.lambda_repo.repository_url}:dbt-latest"
    essential = true

    # Inject the database credentials so dbt knows where to build
    environment =[
      { name = "POSTGRES_HOST", value = aws_db_instance.budget_db.address },
      { name = "POSTGRES_DB", value = aws_db_instance.budget_db.db_name },
      { name = "POSTGRES_USER", value = var.db_username },
      { name = "POSTGRES_PASSWORD", value = var.db_password },
      { name = "DBT_PROFILES_DIR", value = "/usr/app/dbt/budget_manager" },
      { name = "DBT_PROJECT_DIR", value = "/usr/app/dbt/budget_manager" }
    ]

    # Route the terminal output to CloudWatch
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.dbt_logs.name
        "awslogs-region"        = "eu-central-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}