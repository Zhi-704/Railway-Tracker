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


## Configuration
Before running the script, you need to set up your AWS credentials. Create a new file called `.terraform.tfvars` in the `terraform` directory and add the following lines, with your actual AWS keys and database details:

```text
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key

C11_VPC=your_vpc

DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password

DB_NAME=your_db_name
DB_IP=your_db_host_ip_address
DB_PORT=your_db_port

REALTIME_USERNAME=your_realtime_username
REALTIME_PASSWORD=your_realtime_password
```


The script will automatically load the AWS keys and database details from this file.
