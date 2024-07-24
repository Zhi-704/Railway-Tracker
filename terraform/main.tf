# Terraform code to create AWS services: RDS

# Cloud provider:
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

# --------------- RDS: 
# resource "aws_db_instance" "c11-railway-tracker-db" {
#     allocated_storage            = 10
#     db_name                      = "railwaytrackerdb"
#     identifier                   = "c11-railway-tracker-db"
#     engine                       = "postgres"
#     engine_version               = "16.1"
#     instance_class               = "db.t3.micro"
#     publicly_accessible          = true
#     performance_insights_enabled = false
#     skip_final_snapshot          = true
#     db_subnet_group_name         = "c11-public-subnet-group"
#     vpc_security_group_ids       = [aws_security_group.c11-railway-tracker-RDS-sg-terrafrom.id]
#     username                     = var.DB_USERNAME
#     password                     = var.DB_PASSWORD
# }

# resource "aws_security_group" "c11-railway-tracker-RDS-sg-terrafrom" {
#     name = "c11-railway-tracker-RDS-sg-terrafrom"
#     description = "Security group for connecting to RDS database"
#     vpc_id = data.aws_vpc.c11-vpc.id

#     egress {
#         from_port        = 0
#         to_port          = 0
#         protocol         = "-1"
#         cidr_blocks      = ["0.0.0.0/0"]
#     }

#     ingress {
#         from_port = 5432
#         to_port = 5432
#         protocol = "tcp"
#         cidr_blocks      = ["0.0.0.0/0"]
#     }
# }

data "aws_vpc" "c11-vpc" {
    id = var.C11_VPC
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
