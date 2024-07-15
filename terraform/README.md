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
AWS_ACCESS_KEY=YOUR_AWS_ACCESS_KEY
AWS_SECRET_KEY=YOUR_AWS_SECRET_KEY

C11_VPC=YOUR_VPC

DB_USERNAME=YOUR_DB_USERNAME
DB_PASSWORD=YOUR_DB_PASSWORD

DB_NAME=YOUR_DB_NAME
DB_IP=YOUR_DB_IP
DB_PORT=YOUR_DB_PORT
```


The script will automatically load the AWS keys and database details from this file.
