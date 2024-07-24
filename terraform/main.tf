# Terraform code to create AWS services: RDS

# Cloud provider:
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
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
    name = "c11-railway-tracker-RDS-sg-terrafrom"
    description = "Security group for connecting to RDS database"
    vpc_id = data.aws_vpc.c11-vpc.id

    egress {
        from_port        = 0
        to_port          = 0
        protocol         = "-1"
        cidr_blocks      = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
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
data "aws_iam_policy_document" "c11-railway-tracker-archive-schedule-policy-document" {
    statement {
            actions    = ["sts:AssumeRole"]
            effect     = "Allow"
            principals {
                type        = "Service"
                identifiers = ["scheduler.amazonaws.com"]
            }
    }
}

resource "aws_iam_role" "c11-railway-tracker-archive-schedule-role" {
  name               = "c11-railway-tracker-archive-schedule-role"
  assume_role_policy = data.aws_iam_policy_document.c11-railway-tracker-archive-schedule-policy-document.json
}

# 
resource "aws_iam_policy" "c11-railway-tracker-archive-lambda-policy" {
  name        = "c11-railway-tracker-archive-lambda-policy"
  description = "Policy to allow scheduler to invoke archive lambda function"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
        Resource = aws_lambda_function.c11-railway-tracker-archive-lambda-function.arn
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "scheduler_pipeline_archive_lambda_invoke_policy" {
  role       = aws_iam_role.c11-railway-tracker-archive-schedule-role.name
  policy_arn = aws_iam_policy.c11-railway-tracker-archive-lambda-policy.arn
}

# schedule archive process 9 am everyday
resource "aws_scheduler_schedule" "c11-railway-tracker-archive-schedule" {
  name = "c11-railway-tracker-archive-schedule"
  group_name = "default"
  schedule_expression = "cron(0 9 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn = aws_lambda_function.c11-railway-tracker-archive-lambda-function.arn
    role_arn = aws_iam_role.c11-railway-tracker-archive-schedule-role.arn
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
}

# ARCHIVE EVENT BRIDGE SCHEDULE:
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
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = "lambda:InvokeFunction",
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
  name = "c11-railway-tracker-realtime-etl-schedule-tf"
  group_name = "default"
  schedule_expression = "cron(0 0 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn = aws_lambda_function.c11-railway-tracker-realtime-etl-lambda-function-tf.arn
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
  family = "c11-railway-tracker-dashboard-ECS-task-def-tf"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  execution_role_arn = data.aws_iam_role.execution-role.arn
  cpu = 1024
  memory = 2048
  container_definitions = jsonencode([
    {
      name = "c11-railway-tracker-dashboard-ECS-task-def-tf"
      image = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-railway-tracker-dashboard-erc:latest"
      cpu = 10
      memory = 512
      essential = true
      portMappings = [
        {
            containerPort = 80
            hostPort = 80
        },
        {
            containerPort = 8501
            hostPort = 8501       
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
                    "awslogs-create-group" = "true"
                    "awslogs-group" = "/ecs/c11-railway-tracker-dashboard-ECS-task-def-tf"
                    "awslogs-region" = "eu-west-2"
                    "awslogs-stream-prefix" = "ecs"
                }
            }
    },
  ])
}

resource "aws_security_group" "c11-railway-tracker-dashboard-sg-tf" {
    name = "c11-railway-tracker-dashboard-sg-tf"
    description = "Security group for connecting to dashboard"
    vpc_id = data.aws_vpc.c11-vpc.id

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
    name = "c11-railway-tracker-dashboard-service-tf"
    cluster = data.aws_ecs_cluster.c11-cluster.id
    task_definition = aws_ecs_task_definition.c11-railway-tracker-dashboard-ECS-task-def-tf.arn
    desired_count = 1
    launch_type = "FARGATE" 
    
    network_configuration {
        subnets = [data.aws_subnet.c11-subnet-1.id, data.aws_subnet.c11-subnet-2.id, data.aws_subnet.c11-subnet-3.id] 
        security_groups = [aws_security_group.c11-railway-tracker-dashboard-sg-tf.id] 
        assign_public_ip = true
    }
}