


# IAM Role for Lambda execution
resource "aws_iam_role" "c11-railway-tracker-realtime-lambda_execution_role-new-tf" {
  name = "c11-railway-tracker-realtime-lambda_execution_role-new-tf"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda execution role
resource "aws_iam_role_policy" "c11-railway-tracker-realtime-lambda_execution_policy-new-tf" {
  name = "c11-railway-tracker-realtime-lambda_execution_policy-new-tf"
  role = aws_iam_role.c11-railway-tracker-realtime-lambda_execution_role-new-tf.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action   = "dynamodb:Query"
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_lambda_function" "c11-railway-tracker-realtime-etl-lambda-function-new-tf" {
  role          = aws_iam_role.c11-railway-tracker-archive-lambda-role.arn
  function_name = "c11-railway-tracker-realtime-etl-lambda-function-new-tf"
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-trainwreck-realtime:latest"

  timeout = 720
  depends_on    = [aws_cloudwatch_log_group.lambda_log_group]

  environment {
    variables = {
      ACCESS_KEY_ID     = var.AWS_ACCESS_KEY,
      SECRET_ACCESS_KEY = var.AWS_SECRET_KEY,
      DB_IP             = var.DB_IP,
      DB_NAME           = var.DB_NAME,
      DB_USERNAME       = var.DB_USERNAME,
      DB_PASSWORD       = var.DB_PASSWORD,
      DB_PORT           = var.DB_PORT,
      REALTIME_USERNAME = var.REALTIME_USERNAME,
      REALTIME_PASSWORD = var.REALTIME_PASSWORD
    }
  }
    logging_config {
    log_format = "Text"
    log_group  = "/aws/lambda/c11-railway-tracker-realtime-etl-lambda-function-new-tf"
  }

  tracing_config {
    mode = "PassThrough"
  }
}

# REALTIME EVENT BRIDGE SCHEDULE:
# new
# IAM Role for AWS Scheduler
resource "aws_iam_role" "c11-railway-tracker-realtime-scheduler_execution_role-tf" {
  name = "c11-railway-tracker-realtime-scheduler_execution_role-tf"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "c11-railway-tracker-realtime-scheduler_execution_policy-tf" {
  name = "c11-railway-tracker-realtime-scheduler_execution_policy-tf"
  role = aws_iam_role.c11-railway-tracker-realtime-scheduler_execution_role-tf.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.c11-railway-tracker-realtime-etl-lambda-function-new-tf.arn
      }
    ]
  })
}

# AWS Scheduler Schedule
resource "aws_scheduler_schedule" "c11-railway-tracker-realtime-schedule-new-tf" {
  name                         = "c11-railway-tracker-realtime-schedule-new-tf"
  schedule_expression          = "cron(*/5 * * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c11-railway-tracker-realtime-etl-lambda-function-new-tf.arn
    role_arn = aws_iam_role.c11-railway-tracker-realtime-scheduler_execution_role-tf.arn
  }
}

