[![badge](./.github/badges/passed_percentage.svg)](./.util/pytest_scores.txt)
[![badge](./.github/badges/avg_score.svg)](./.util/pylint_scores.txt)
[![badge](./.github/badges/number_of_tests.svg)](./.util/pylint_scores.txt)

# Railway-Tracker

## Overview

### Description
Welcome to the Railway Tracker! Train data is extracted via an ETL pipeline from National Rail and Realtime Train, which is then used to create three different outputs. These outputs will provide various information on a station's cancellations, delays, and departures/arrivals. Furthermore, any incidents will send an alert notification to all subscribed users. The code for these outputs are in the folder: **dashboard**, **national_rail**, and **pdf_report**. This results in our **tracker** which is provided to consumers as a service.

### Deliverables
- Two full data pipeline hosted in the cloud.
- Automatic alerts for delays/cancellations for certain train operators.
- Regular PDF summary reports directly emailed to subscribers.
- Visualisation of stations' data on the dashboard.


## Design

### Entity-Relationship Diagram
![ERD Diagram](https://github.com/Zhi-704/Railway-Tracker/blob/main/diagrams/ERD.png)

This diagram explicitly shows how the data extracted from the API is stored in the database. We have decided to use a **3NF RD** for our database due to the requirements of the tracker.

### Architecture Diagram
![Architecture Diagram](https://github.com/Zhi-704/Railway-Tracker/blob/main/diagrams/Architecture_Diagram.png)

This is a diagram that shows how every different AWS services work and interact with each other in order to complete the requirements of the tracker.

#### **IMPORTANT**
 >Information regarding each section of the AD will not be found here. Instead, **clicking on** the bullet points below will send you to the relative **README** located in the **directories** of the section that you would like to look at. There you can find out all the information that you need.


- [**National Rail ETL Pipeline**](./national_rail/README.md)

- [**Realtime Trains ETL Pipeline**](./realtime_trains/README.md)

- [**Relational Database**](./database/README.md)

- [**PDF Report**](./pdf_report/README.md)

- [**Dashboard**](./dashboard/README.md)




## Getting Started

### Installations
The following languages/softwares are **required** for this project. Things assigned as **optional** are only required if you desire to host this tracker on the cloud.
- Python
- Bash
- Docker (Optional)

### Dependencies
There are various **directories** for each part of the project. In order to run the scripts in each folder, you will need to install the **required libraries**. This can be done using the code provided below:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the scripts
All the scripts only require **basic** commands to be executed. Different commands are used **depending on the software**. Ensure that you are in the directory of the file you want to run before using these commands.
```
# Python
python3 "example_script.py"

# Bash
bash "example_script.sh"

# Terraform
terraform init
terraform apply
yes

# Docker
docker build -t "example_image"
docker run --env-file .env -t "example_image:tag"
```
#### **IMPORTANT**
>One thing to note is that the majority of scripts use environment variables. Make sure to create your own .env and fill out all the variables required to run the code successfully. Smaller READMEs will be found in each folder going into more depth on how to use that specific part of the repository.


## Running the Repository

### Repository Structure
There are several directories within the repository to maintain an organised project. Each directory will be labelled below with a brief sentence explaining what they do. 

#### **IMPORTANT**
>Clicking on the link provided will redirect you to the README in that directory which provides more information

- `archive` - Contains scripts that archive month-old data in the database to avoid over-inflation of data storage. [**Click here**](./archive/README.md).
- `dashboard` - Contains all the scripts involved in creating and hosting the dashboard. [**Click here**](./dashboard/README.md).
- `database` - Contains the schema used to create the RDS hosted on AWS as well as any auxiliary functions. [**Click here**](./database/README.md).
- `diagrams` - Only contains the .png files of the diagrams used in this README.
- `national_rail` - Contains all scripts involved in creating the ETL pipeline for tracking incidents as well as scripts required to send emails/sms to subscribers to notify them when an incident has occurred.
 [**Click here**](./national_rail/README.md).
- `pdf_report` - Contains all the scripts required to send a daily email to registered subscribers which contains the PDF on the data from yesterday. [**Click here**](./pdf_report/README.md)
- `realtime_trains` - Contains all the scripts involved in creating the ETL pipeline for import stations data to the database. [**Click here**](./realtime_trains/README.md).
- `terraform` - Contains the main terraform script used to host the tracker on the cloud. [**Click here**](./terraform/README.md).


### Cloud Resources
For this tracker, we have designed it with the intention of hosting everything on the cloud in order to automate it. The python scripts can still be ran locally but the terraform scripts have been included within the repository if you desire to host this service on the cloud as well. The cloud service that has been used is **AWS**.


## Help
Common issues which people face are:

- Not setting up environment variables correctly - you need to ensure that you have done the following: 
  1. **Create** .env file for python scripts or a terraform.tfvars for terraform scripts
  2. Create the file in the **same directory as the file** you want to run
  3. Make sure the variable names in your **file are the same as the ones used in the script** that you would like to run.

- Not downloading the required libraries before running the script.
  1. **Go to the directory** of the script that you want to run.
  2. **Create** a .venv and activate it.
  3. **Install** the requirements onto your .venv.

- For any other problems, make sure to reach out and contact us so we can support you further.


## Authors
- https://github.com/FarihaChoudhury
- https://github.com/Zhi-704
- https://github.com/A-Faris
- https://github.com/fm1psy

