# Terraform code to create AWS services: RDS

# Cloud provider:
provider "aws" {
    region      = var.AWS_REGION
    access_key  = var.AWS_ACCESS_KEY
    secret_key  = var.AWS_SECRET_KEY
}


data "aws_vpc" "c11-vpc" {
    id = "vpc-04b15cce2398e57f7"
}

data "aws_subnet" "c11-subnet-1" {
  id = "subnet-0e6c6a8f959dae31a"
}

data "aws_subnet" "c11-subnet-2" {
  id = "subnet-08781450402b81aa2"
}

data "aws_subnet" "c11-subnet-3" {
  id = "subnet-07de213eeae1f6307"
}

# --------------- RDS: 
resource "aws_db_instance" "c11-railway-tracker-db" {
    allocated_storage            = 10
    db_name                      = "railwaytrackerdb"
    identifier                   = "c11-railway-tracker-db"
    engine                       = "postgres"
    engine_version               = "16.1"
    instance_class               = "db.t3.micro"
    publicly_accessible          = true
    performance_insights_enabled = false
    skip_final_snapshot          = true
    db_subnet_group_name         = "c11-public-subnet-group"
    vpc_security_group_ids       = [aws_security_group.c11-railway-tracker-RDS-sg-terrafrom.id]
    username                     = var.DB_USERNAME
    password                     = var.DB_PASSWORD
}

resource "aws_security_group" "c11-railway-tracker-RDS-sg-terrafrom" {
    name        = "c11-railway-tracker-RDS-sg-terrafrom"
    description = "Security group for connecting to RDS database"
    vpc_id      = data.aws_vpc.c11-vpc.id

    egress {
        from_port        = 0
        to_port          = 0
        protocol         = "-1"
        cidr_blocks      = ["0.0.0.0/0"]
    }

    ingress {
        from_port        = 5432
        to_port          = 5432
        protocol         = "tcp"
        cidr_blocks      = ["0.0.0.0/0"]
    }
}



# --------------- ARCHIVE: LAMBDA & EVENT BRIDGE

data "aws_iam_policy_document" "c11-railway-tracker-archive-lambda-policy-document" {
    statement {
        actions    = ["sts:AssumeRole"]
        effect     = "Allow"
        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
  }
}

resource "aws_iam_role" "c11-railway-tracker-archive-lambda-role" {
  name               = "c11-railway-tracker-archive-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.c11-railway-tracker-archive-lambda-policy-document.json
}


resource "aws_lambda_function" "c11-railway-tracker-archive-lambda-function" {
  role          = aws_iam_role.c11-railway-tracker-archive-lambda-role.arn
  function_name = "c11-railway-tracker-archive-lambda-function"
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-railway-tracker-archive-lambda-ecr:latest"

  environment {
    variables = {
      ACCESS_KEY_ID     = var.AWS_ACCESS_KEY,
      SECRET_ACCESS_KEY = var.AWS_SECRET_KEY,
      DB_IP             = var.DB_IP,
      DB_NAME           = var.DB_NAME,
      DB_USERNAME       = var.DB_USERNAME,
      DB_PASSWORD       = var.DB_PASSWORD,
      DB_PORT           = var.DB_PORT,
    }
  }
}

# ARCHIVE EVENT BRIDGE SCHEDULE:

resource "aws_iam_role" "c11-railway-tracker-archive-scheduler_execution_role-tf" {
  name = "c11-railway-tracker-archive-scheduler_execution_role-tf"

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

resource "aws_iam_role_policy" "c11-railway-tracker-archive-scheduler_execution_policy-tf" {
  name = "c11-railway-tracker-archive-scheduler_execution_policy-tf"
  role = aws_iam_role.c11-railway-tracker-archive-scheduler_execution_role-tf.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.c11-railway-tracker-archive-lambda-function.arn
      }
    ]
  })
}

# AWS Scheduler Schedule
resource "aws_scheduler_schedule" "c11-railway-tracker-archive-schedule-new-tf" {
  name                         = "c11-railway-tracker-archive-schedule-new-tf"
  schedule_expression          =  "cron(0 2 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c11-railway-tracker-archive-lambda-function.arn
    role_arn = aws_iam_role.c11-railway-tracker-archive-scheduler_execution_role-tf.arn
  }
}




# --------------- REAL TIME PERFORMANCE ETL: LAMBDA & EVENT BRIDGE

data "aws_iam_policy_document" "lambda_logging_doc" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role" "c11-railway-tracker-realtime-etl-lambda-role-tf" {
  name               = "c11-railway-tracker-realtime-etl-lambda-role-tf"
  assume_role_policy = data.aws_iam_policy_document.c11-railway-tracker-archive-lambda-policy-document.json
}

resource "aws_iam_policy" "function_logging_policy" {
  name   = "function-logging-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        Action : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect : "Allow",
        Resource : "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "function_logging_policy_attachment" {
  role       = aws_iam_role.c11-railway-tracker-realtime-etl-lambda-role-tf.id
  policy_arn = aws_iam_policy.function_logging_policy.arn
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/c11-railway-tracker-realtime-etl-lambda-function-tf"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}


resource "aws_lambda_function" "c11-railway-tracker-realtime-etl-lambda-function-tf" {
  role          = aws_iam_role.c11-railway-tracker-archive-lambda-role.arn
  function_name = "c11-railway-tracker-realtime-etl-lambda-function-tf"
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-trainwreck-realtime:latest"

  timeout       = 720
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
}

# REALTIME EVENT BRIDGE SCHEDULE:
data "aws_iam_policy_document" "c11-railway-tracker-realtime-schedule-policy-document" {
    statement {
            actions    = ["sts:AssumeRole"]
            effect     = "Allow"
            principals {
                type        = "Service"
                identifiers = ["scheduler.amazonaws.com"]
            }
    }
}
resource "aws_iam_role" "c11-railway-tracker-realtime-etl-schedule-role-tf" {
  name               = "c11-railway-tracker-realtime-etl-schedule-role-tf"
  assume_role_policy = data.aws_iam_policy_document.c11-railway-tracker-realtime-schedule-policy-document.json
}

resource "aws_iam_policy" "c11-railway-tracker-realtime-lambda-policy-tf" {
  name        = "c11-railway-tracker-realtime-lambda-policy-tf"
  description = "Policy to allow scheduler to invoke etl realtime lambda function"
  policy      = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "lambda:InvokeFunction",
        Resource = aws_lambda_function.c11-railway-tracker-realtime-etl-lambda-function-tf.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "scheduler_pipeline_realtime_lambda_invoke_policy" {
  role       = aws_iam_role.c11-railway-tracker-realtime-etl-schedule-role-tf.name
  policy_arn = aws_iam_policy.c11-railway-tracker-realtime-lambda-policy-tf.arn
}

# schedule realtime process 12am everyday
resource "aws_scheduler_schedule" "c11-railway-tracker-realtime-etl-schedule-tf" {
  name                         = "c11-railway-tracker-realtime-etl-schedule-tf"
  group_name                   = "default"
  schedule_expression          = "cron(0 1 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c11-railway-tracker-realtime-etl-lambda-function-tf.arn
    role_arn = aws_iam_role.c11-railway-tracker-realtime-etl-schedule-role-tf.arn
  }
}



# --------------- S3 REPORT BUCKET:
resource "aws_s3_bucket" "c11-railway-tracker-s3" {
  bucket = "c11-railway-tracker-s3"
}



# --------------- ECS FARGATE SERVICE: DASHBAORD

data "aws_ecs_cluster" "c11-cluster" {
    cluster_name = "c11-ecs-cluster"
}

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "c11-railway-tracker-dashboard-ECS-task-def-tf" {
  family                   = "c11-railway-tracker-dashboard-ECS-task-def-tf"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  execution_role_arn       = data.aws_iam_role.execution-role.arn
  cpu                      = 1024
  memory                   = 2048
  container_definitions    = jsonencode([
    {
      name         = "c11-railway-tracker-dashboard-ECS-task-def-tf"
      image        = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-railway-tracker-dashboard-erc:latest"
      cpu          = 10
      memory       = 512
      essential    = true
      portMappings = [
        {
            containerPort = 80
            hostPort      = 80
        },
        {
            containerPort = 8501
            hostPort      = 8501       
        }
      ]
      environment= [
                {
                    "name": "ACCESS_KEY",
                    "value": var.AWS_ACCESS_KEY
                },
                {
                    "name": "SECRET_ACCESS_KEY",
                    "value": var.AWS_SECRET_KEY
                },
                {
                    "name": "DB_NAME",
                    "value": var.DB_NAME
                },
                {
                    "name": "DB_USERNAME",
                    "value": var.DB_USERNAME
                },
                {
                    "name": "DB_PASSWORD",
                    "value": var.DB_PASSWORD
                },
                {
                    "name": "DB_IP",
                    "value": var.DB_IP
                },
                {
                    "name": "DB_PORT",
                    "value": var.DB_PORT
                }
            ]
            logConfiguration = {
                logDriver = "awslogs"
                options = {
                    "awslogs-create-group"  = "true"
                    "awslogs-group"         = "/ecs/c11-railway-tracker-dashboard-ECS-task-def-tf"
                    "awslogs-region"        = "eu-west-2"
                    "awslogs-stream-prefix" = "ecs"
                }
            }
    },
  ])
}

resource "aws_security_group" "c11-railway-tracker-dashboard-sg-tf" {
    name        = "c11-railway-tracker-dashboard-sg-tf"
    description = "Security group for connecting to dashboard"
    vpc_id      = data.aws_vpc.c11-vpc.id

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port   = 8501
        to_port     = 8501
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }


}

resource "aws_ecs_service" "c11-railway-tracker-dashboard-service-tf" {
    name            = "c11-railway-tracker-dashboard-service-tf"
    cluster         = data.aws_ecs_cluster.c11-cluster.id
    task_definition = aws_ecs_task_definition.c11-railway-tracker-dashboard-ECS-task-def-tf.arn
    desired_count   = 1
    launch_type     = "FARGATE" 
    
    network_configuration {
        subnets          = [data.aws_subnet.c11-subnet-1.id, data.aws_subnet.c11-subnet-2.id, data.aws_subnet.c11-subnet-3.id] 
        security_groups  = [aws_security_group.c11-railway-tracker-dashboard-sg-tf.id] 
        assign_public_ip = true
    }
}

# --------------- INCIDENT: LAMBDA & EVENT BRIDGE

# IAM Policy Document for Lambda Assume Role
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# IAM Role for Lambda Execution
resource "aws_iam_role" "lambda_execution_role" {
  name               = "lambda_execution_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

# IAM Policy Document for Lambda Execution Role
data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions   = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
    effect    = "Allow"
  }
}

# IAM Policy for Lambda Execution Role
resource "aws_iam_role_policy" "lambda_execution_role_policy" {
  name   = "lambda_execution_role_policy"
  role   = aws_iam_role.lambda_execution_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

# CloudWatch Log Group for Lambda Logs
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/c11-railway-tracker-national-rail"
  retention_in_days = 14
}

# Lambda Function Resource
resource "aws_lambda_function" "c11_railway_tracker_national_rail" {
  function_name = "c11-railway-tracker-national-rail"
  role          = aws_iam_role.lambda_execution_role.arn
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-railway-tracker-national:latest"
  package_type  = "Image"
  timeout       = 180

  environment {
    variables = {
      ACCESS_KEY_ID         = var.AWS_ACCESS_KEY,
      SECRET_ACCESS_KEY     = var.AWS_SECRET_KEY,
      DB_IP                 = var.DB_IP,
      DB_NAME               = var.DB_NAME,
      DB_USERNAME           = var.DB_USERNAME,
      DB_PASSWORD           = var.DB_PASSWORD,
      DB_PORT               = var.DB_PORT,
      NATIONAL_RAIL_API_KEY = var.NATIONAL_RAIL_API_KEY
    }
  }

  logging_config {
    log_format = "Text"
    log_group  = aws_cloudwatch_log_group.lambda_log_group.name
  }

  tracing_config {
    mode = "PassThrough"
  }
}

# IAM Policy Document for AWS Scheduler Assume Role
data "aws_iam_policy_document" "scheduler_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

# IAM Role for AWS Scheduler
resource "aws_iam_role" "scheduler_execution_role" {
  name               = "scheduler_execution_role"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume_role_policy.json
}

# IAM Policy Document for AWS Scheduler Role
data "aws_iam_policy_document" "scheduler_policy" {
  statement {
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.c11_railway_tracker_national_rail.arn]
    effect    = "Allow"
  }
}

# IAM Policy for AWS Scheduler Role
resource "aws_iam_role_policy" "scheduler_execution_role_policy" {
  name   = "scheduler_execution_role_policy"
  role   = aws_iam_role.scheduler_execution_role.id
  policy = data.aws_iam_policy_document.scheduler_policy.json
}

# AWS Scheduler Schedule
resource "aws_scheduler_schedule" "c11_railway_tracker_national_rail_schedule" {
  name                         = "c11-railway-tracker-national-rail-schedule"
  schedule_expression          = "cron(*/5 * * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    maximum_window_in_minutes = 5
    mode                      = "FLEXIBLE"
  }

  target {
    arn      = aws_lambda_function.c11_railway_tracker_national_rail.arn
    role_arn = aws_iam_role.scheduler_execution_role.arn
  }
}




# --------------- REPORT ETL: LAMBDA & EVENT BRIDGE

# IAM Role for Lambda execution
resource "aws_iam_role" "c11-railway-tracker-report_execution_role-new-tf" {
  name = "c11-railway-tracker-report_execution_role-new-tf"

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
  role = aws_iam_role.c11-railway-tracker-report_execution_role-new-tf.id

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

resource "aws_lambda_function" "c11-railway-tracker-report-lambda-function-new-tf" {
  role          = aws_iam_role.c11-railway-tracker-report_execution_role-new-tf.arn
  function_name = "c11-railway-tracker-report-lambda-function-new-tf"
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-railway-tracker-report-ecr:latest"

  timeout       = 720
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
    log_group  = "/aws/lambda/c11-railway-tracker-report-lambda-function-new-tf"
  }

  tracing_config {
    mode = "PassThrough"
  }
}

# REALTIME EVENT BRIDGE SCHEDULE:
# new
# IAM Role for AWS Scheduler
resource "aws_iam_role" "c11-railway-tracker-report-scheduler_execution_role-tf" {
  name = "c11-railway-tracker-report-scheduler_execution_role-tf"

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

resource "aws_iam_role_policy" "c11-railway-tracker-report-scheduler_execution_policy-tf" {
  name = "c11-railway-tracker-report-scheduler_execution_policy-tf"
  role = aws_iam_role.c11-railway-tracker-report-scheduler_execution_role-tf.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.c11-railway-tracker-report-lambda-function-new-tf.arn
      }
    ]
  })
}

# AWS Scheduler Schedule
resource "aws_scheduler_schedule" "c11-railway-tracker-report-schedule-new-tf" {
  name                         = "c11-railway-tracker-report-schedule-new-tf"
  schedule_expression          =  "cron(0 6 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.c11-railway-tracker-report-lambda-function-new-tf.arn
    role_arn = aws_iam_role.c11-railway-tracker-report-scheduler_execution_role-tf.arn
  }
}

