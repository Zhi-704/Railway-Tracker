# Dashboard

This folder contains code for the dashboard. 

## Overview

- `.env`: This file contains environment variables for the database connection details.
- `dockerfile`: code to create docker image of archive process. 

## Setup

1. Ensure you have a PostgreSQL server running and accessible.
2. Ensure you have connection to your database for the Railway Tracker project.
3. Create a `.env` file in the same directory as the other files, and add the following lines, replacing the placeholders with your actual database connection details:

```text
DB_PASSWORD=your_database_password
DB_USERNAME=your_database_username
DB_NAME=your_database_name
DB_PORT=your_database_port
DB_IP=your_database_ip_or_hostname
```

## Usage:

The main script to run the dashboard is `main_page.py`. You can run it with the following command:

```bash
streamlit run main_page.py
```


## Creating a docker image to run locally:

1. Build docker image: ```docker build -t railway-tracker-dashboard-local .```
2. View if docker image has been created locally:```docker image ls```
3. Run docker image with environment variables: ```docker run -it -p 8501:8501 --env-file .env railway-tracker-dashboard-local```

## Creating a docker image to run on AWS:

1. Create an ECR repository on AWS.
2. Follow steps from the push commands to upload the docker image.
3. Connect the docker image to an ECS Fargate service (`Terraform/main.tf`).
