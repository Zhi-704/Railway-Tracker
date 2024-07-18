# Terraform code to create AWS services: RDS

# Cloud provider:
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

# # RDS: 
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




# ARCHIVE PROCESS: LAMBDA 
    # policy document
    # iam role
    # lambda

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
  
    #   data.aws_ecr_image.archive-lambda-image.image_uri

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
    # policy document
    # iam role
    # event bridge schedule lambda at 9:30

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

resource "aws_scheduler_schedule" "c11-railway-tracker-archive-schedule" {
    # schedule archive process 9 am everyday
  name = "c11-railway-tracker-archive-schedule"
  group_name = "default"

  schedule_expression = "cron(*/2 * * * ? *)"
#   "cron(0 9 * * ? *)"
  schedule_expression_timezone = "Europe/London"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn = aws_lambda_function.c11-railway-tracker-archive-lambda-function.arn
    role_arn = aws_iam_role.c11-railway-tracker-archive-schedule-role.arn
  }
}

