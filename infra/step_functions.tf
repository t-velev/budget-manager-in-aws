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
        Resource =[
          aws_lambda_function.extract_account.arn,
          aws_lambda_function.extract_category.arn,
          aws_lambda_function.extract_subcategory.arn,
          aws_lambda_function.extract_year.arn,
          aws_lambda_function.extract_month.arn,
          aws_lambda_function.extract_budget.arn,
          aws_lambda_function.extract_transaction.arn,
          aws_lambda_function.reset_raw_notion_dates.arn
        ]
      },
      {
        Effect   = "Allow"
        Action   =[
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:DescribeTasks"
        ]
        Resource =[
          aws_ecs_task_definition.dbt_task.arn,
          "${aws_ecs_task_definition.dbt_task.arn_without_revision}:*",
          "arn:aws:ecs:*:*:task/${aws_ecs_cluster.dbt_cluster.name}/*"
        ]
      },
      {
        # Permissions for .sync
        Effect   = "Allow"
        Action   =[
          "events:PutTargets",
          "events:PutRule",
          "events:DescribeRule"
        ]
        Resource =[
          "arn:aws:events:*:*:rule/StepFunctionsGetEventsForECSTaskRule"
        ]
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
            "execution_input.$" = "$$.Execution.Input"
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
            "execution_input.$" = "$$.Execution.Input"
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
            "execution_input.$" = "$$.Execution.Input"
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
            "execution_input.$" = "$$.Execution.Input"
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
            "execution_input.$" = "$$.Execution.Input"
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
            "execution_input.$" = "$$.Execution.Input"
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
            "execution_input.$" = "$$.Execution.Input"
          }
        },
        # Extract JUST the Payload from Lambda so we can easily grab $.run_id
        OutputPath = "$.Payload",
        Next = "MergeDbtVars"
      },

      # Task 8: Bundle the run_id and the Global Execution Input together
      MergeDbtVars = {
        Type = "Pass",
        Parameters = {
          "run_id.$"          = "$.run_id",
          "execution_input.$" = "$$.Execution.Input"
        },
        Next = "StringifyDbtVars"
      },

      # Task 9: Stringify the payload (but preserve the state so we can check it again)
      StringifyDbtVars = {
        Type = "Pass",
        ResultPath = "$.dbt_vars_output",
        Parameters = {
          # This builds the exact JSON string dbt wants: {"run_id": 20260507163428}
          "stringified.$" = "States.JsonToString($)"
        },
        Next = "CheckSeedRequirement"
      },

      # CHOICE: Do we need to exclude seeds?
      CheckSeedRequirement = {
        Type = "Choice",
        Choices =[
          {
            And =[
              { Variable = "$.execution_input.is_initial_load", IsPresent = true },
              { Variable = "$.execution_input.is_initial_load", BooleanEquals = true }
            ],
            Next = "BuildCommandInitial"
          }
        ],
        Default = "BuildCommandIncremental"
      },

      # Task 10A: Array WITHOUT exclude (Initial Load)
      BuildCommandInitial = {
        Type = "Pass",
        Parameters = {
          "Command.$" = "States.Array('dbt', 'build', '--project-dir', '/usr/app/dbt/budget_manager', '--profiles-dir', '/usr/app/dbt/budget_manager', '--vars', $.dbt_vars_output.stringified)"
        },
        Next = "RunDbtTransformations"
      },

      # Task 10B: Array WITH exclude (Incremental Load)
      BuildCommandIncremental = {
        Type = "Pass",
        Parameters = {
          "Command.$" = "States.Array('dbt', 'build', '--project-dir', '/usr/app/dbt/budget_manager', '--profiles-dir', '/usr/app/dbt/budget_manager', '--exclude', 'resource_type:seed', '--vars', $.dbt_vars_output.stringified)"
        },
        Next = "RunDbtTransformations"
      },

      # Task 11: Run dbt in Fargate
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
              # Magic Trick: Inject the dynamically built Command Array from Task 10A or 10B!
              "Command.$" = "$.Command"
            }]
          }
        },
        End = true
      }
    }
  })
}