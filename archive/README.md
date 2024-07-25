# Railway Tracker Database

This folder contains code for the archiving process of out of date incident and waypoint data to clean the database. Performance metrics are calculated and stored in the archive for long term storage. 

## Overview

- `.env`: This file contains environment variables for the database connection details.
- `archive.py`: A python script for running the archiving process; calling all other scripts in the directory. 
- `clean_national_rail.py`: A python script for cleaning the national rail incident data from the RDS.
- `clean_real_time_trains.py`: A python script for cleaning and archiving the realtime trains data from the RDS.
- `db_connection.py`: Helper functions for connecting to the AWS RDS database.
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

The main script to run the archiving process on the RDS is `archive.py`. You can run it with the following command:

```bash
python3 archive.py
```

This script will read the RDS and extract any out of date data, clean the RDS and insert a compressed version into the archive table for long term storage.

## Creating a docker image to run locally:
1. Build docker image: ```docker build -t railway-tracker-archive-local .```
2. View if docker image has been created locally:```docker image ls```
3. Run docker image with environment variables: ```docker run --env-file .env railway-tracker-archive-local```
