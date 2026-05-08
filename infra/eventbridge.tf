# 1. The Schedule (Runs at 23:00 UTC, which is 02:00 AM in Sofia)
#    AWS EventBridge schedules are always in UTC
resource "aws_cloudwatch_event_rule" "daily_etl_trigger" {
  name                = "daily-budget-etl-trigger"
  description         = "Trigger the Budget Manager ETL pipeline every night"
  # AWS explicitly requires a 6-field expression
  # The * means "every. The ? means "I don't care about this specific field."
  # The 6-field version often forbids using * for both "Day of Month" and "Day of Week". Use ? for one of them.
  schedule_expression = "cron(0 5/4 * * ? *)"  # cron(Minutes Hours Day-of-month Month Day-of-week Year)
  state = "DISABLED"
}

# 2. IAM Role: Give EventBridge permission to push the "Start" button
resource "aws_iam_role" "eventbridge_sfn_role" {
  name = "eventbridge-invoke-sfn-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement =[{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "events.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "eventbridge_sfn_policy" {
  name = "eventbridge-invoke-sfn-policy"
  role = aws_iam_role.eventbridge_sfn_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement =[{
      Action   = "states:StartExecution"
      Effect   = "Allow"
      Resource = aws_sfn_state_machine.etl_pipeline.arn
    }]
  })
}

# 3. The Target: Connect the Schedule to the Step Function
resource "aws_cloudwatch_event_target" "trigger_sfn" {
  rule      = aws_cloudwatch_event_rule.daily_etl_trigger.name
  target_id = "budget-manager-sfn"
  arn       = aws_sfn_state_machine.etl_pipeline.arn
  role_arn  = aws_iam_role.eventbridge_sfn_role.arn

  # Automatically inject the JSON payload for normal nightly incremental runs!
  input = jsonencode({
    "is_initial_load" = false
  })
}