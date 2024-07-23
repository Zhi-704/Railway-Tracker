# Terraform code to create AWS services: RDS

# Cloud provider:
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
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

data "aws_vpc" "c11-vpc" {
    id = var.C11_VPC
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



# REAL TIME PERFORMANCE ETL: LAMBDA 
    # policy document
    # iam role
    # lambda

# data "aws_iam_policy_document" "c11-railway-tracker-archive-lambda-policy-document" {
#     statement {
#         actions    = ["sts:AssumeRole"]
#         effect     = "Allow"
#         principals {
#             type        = "Service"
#             identifiers = ["lambda.amazonaws.com"]
#         }
#   }
# }

resource "aws_iam_role" "c11-railway-tracker-realtime-etl-lambda-role-tf" {
  name               = "c11-railway-tracker-realtime-etl-lambda-role-tf"
  assume_role_policy = data.aws_iam_policy_document.c11-railway-tracker-archive-lambda-policy-document.json
}


resource "aws_lambda_function" "c11-railway-tracker-realtime-etl-lambda-function-tf" {
  role          = aws_iam_role.c11-railway-tracker-archive-lambda-role.arn
  function_name = "c11-railway-tracker-realtime-etl-lambda-function-tf"
  package_type  = "Image"
  architectures = ["x86_64"]
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-trainwreck-realtime:latest"

  timeout = 720

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
    # policy document
    # iam role
    # event bridge schedule lambda at 12 am 

# data "aws_iam_policy_document" "c11-railway-tracker-archive-schedule-policy-document" {
#     statement {
#             actions    = ["sts:AssumeRole"]
#             effect     = "Allow"
#             principals {
#                 type        = "Service"
#                 identifiers = ["scheduler.amazonaws.com"]
#             }
#     }
# }
# policy is generic so can be reused.

resource "aws_iam_role" "c11-railway-tracker-realtime-etl-schedule-role-tf" {
  name               = "c11-railway-tracker-realtime-etl-schedule-role-tf"
  assume_role_policy = data.aws_iam_policy_document.c11-railway-tracker-archive-schedule-policy-document.json
}

# schedule realtime process 5pm everyday
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


# S3 BUCKET FOR REPORTS
resource "aws_s3_bucket" "c11-railway-tracker-s3" {
  bucket = "c11-railway-tracker-s3"
}



# ECS FOR DASHBOARD:
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


# SERVICE TO START DASHBOARD:

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

resource "aws_ecs_service" "c11-Fariha-stack-exchange-ECS-dashboard-service-terraform" {
    name = "c11-Fariha-dashboard-service-terraform"
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