# Terraform code to create AWS services: RDS

# Cloud provider:
provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

# RDS: 
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

data "aws_vpc" "c11-vpc" {
    id = var.C11_VPC
}
