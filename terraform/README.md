# Terraform

This directory focuses on **terraforming** all the AWS cloud services that are used throughout the Railway Tracker application.


## Installation

Navigate to the project directory:

```bash
cd terraform
```

## Usage

The main script to create AWS cloud services through terraform is `main.tf`. You can run it with the following command:

To initialise: 
```bash
terraform init 
```

To create the services:
```bash
terraform plan
terraform apply 
```
The ```apply``` command will prompt the user to enter ```yes``` to confirm the creation of the services. The services will then be created on AWS unless an error with any credentials has occurred. 

To destroy:
```bash
terraform destroy
```

## Terraformed AWS services:
* RDS - database
* Lambda - to run the archive process, scheduled for 9am everyday.
* Lambda - to run the RealTimeTrains pipeline, scheduled for 12am everyday.
* Lambda - to run the NationalRail incident pipeline, scheduled for every 5 minutes.
* Lambda - to run the PDF report generation pipeline, scheduled for 6am everyday.
* S3 bucket - long term storage to hold PDF summary reports.
* ECS service - to run the dashboard.


## Configuration
Before running the script, you need to set up your AWS credentials. Create a new file called `.terraform.tfvars` in the `terraform` directory and add the following lines, with your actual AWS keys and database details:

```text
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key

C11_VPC=your_vpc

DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password

DB_NAME=your_db_name
DB_IP=your_DB_IP_ip_address
DB_PORT=your_db_port

REALTIME_USERNAME=your_realtime_username
REALTIME_PASSWORD=your_realtime_password

NATIONAL_RAIL_API_KEY=your_nation_rail_key
```


The script will automatically load the AWS keys and database details from this file.