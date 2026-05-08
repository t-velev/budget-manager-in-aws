# 1. IAM Role for Step Functions
resource "aws_iam_role" "step_function_role" {
  name = "budget-manager-sfn-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement =[{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "states.amazonaws.com" }
    }]
  })
}

# Allow Step Functions to trigger Lambda, Fargate, and create EventBridge monitoring rules
resource "aws_iam_role_policy" "sfn_execution_policy" {
  name = "sfn_execution_policy"
  role = aws_iam_role.step_function_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement =[
      {
        Effect   = "Allow"
        Action   = ["lambda:InvokeFunction"]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   =[
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:DescribeTasks"
        ]
        Resource = ["*"]
      },
      {
        # Permissions for .sync
        Effect   = "Allow"
        Action   =[
          "events:PutTargets",
          "events:PutRule",
          "events:DescribeRule"
        ]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource =[aws_iam_role.ecs_execution_role.arn]
      }
    ]
  })
}

# 2. The Step Function State Machine (Our DAG)
resource "aws_sfn_state_machine" "etl_pipeline" {
  name     = "budget-manager-etl-pipeline"
  role_arn = aws_iam_role.step_function_role.arn

  # ASL (Amazon States Language) - This is the DAG definition!
  definition = jsonencode({
    Comment = "Notion to DWH ETL Pipeline",
    StartAt = "ExtractAndLoadAccount",
    States = {
      # Task 1: Extract Account
      ExtractAndLoadAccount = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_account.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        Next = "ExtractAndLoadCategory"
      },

      # Task 2: Extract Category
      ExtractAndLoadCategory = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_category.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        Next = "ExtractAndLoadSubcategory"
      },

      # Task 3: Extract Subcategory
      ExtractAndLoadSubcategory = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_subcategory.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        Next = "ExtractAndLoadYear"
      },

      # Task 4: Extract Year
      ExtractAndLoadYear = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_year.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        Next = "ExtractAndLoadMonth"
      },

      # Task 5: Extract Month
      ExtractAndLoadMonth = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_month.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        Next = "ExtractAndLoadBudget"
      },

      # Task 6: Extract Budget
      ExtractAndLoadBudget = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_budget.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        Next = "ExtractAndLoadTransaction"
      },      

      # Task 7: Extract Transaction
      ExtractAndLoadTransaction = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        Parameters = {
          FunctionName = aws_lambda_function.extract_transaction.function_name
          Payload = {
            "run_id.$" = "$$.Execution.StartTime" 
          }
        },
        # Extract JUST the Payload from Lambda so we can easily grab $.run_id
        OutputPath = "$.Payload",
        Next = "PrepareDbtArgs"
      },      

      # Task 2: Format the string for dbt
      PrepareDbtArgs = {
        Type = "Pass",
        Parameters = {
          # This builds the exact JSON string dbt wants: {"run_id": 20260507163428}
          "dbt_vars.$" = "States.JsonToString($)"
        },
        Next = "RunDbtTransformations"
      },

      # Task 3: Run dbt in Fargate
      RunDbtTransformations = {
        Type     = "Task",
        Resource = "arn:aws:states:::ecs:runTask.sync",
        Parameters = {
          LaunchType     = "FARGATE"
          Cluster        = aws_ecs_cluster.dbt_cluster.id
          TaskDefinition = aws_ecs_task_definition.dbt_task.arn
          NetworkConfiguration = {
            AwsvpcConfiguration = {
              Subnets        =["subnet-06df2f4600f421434"]
              AssignPublicIp = "ENABLED"
            }
          }
          Overrides = {
            ContainerOverrides =[{
              Name = "dbt-container"
              # Dynamically build the Command Array using States.Array!
              "Command.$" = "States.Array('dbt', 'build', '--project-dir', '/usr/app/dbt/budget_manager', '--profiles-dir', '/usr/app/dbt/budget_manager', '--exclude', 'resource_type:seed', '--vars', $.dbt_vars)"
            }]
          }
        },
        End = true
      }
    }
  })
}