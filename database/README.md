# Railway Tracker Database

This folder contains the database schema, scripts, and related files for the Railway Tracker project.

## Overview

- `.env`: This file contains environment variables for the database connection details.
- `schema.sql`: This SQL script defines the database schema, including tables, indexes, and relationships for the Railway Tracker application.
- `query.sql`: This SQL script contains various queries to retrieve data from the database tables.
- `clear.sh`: A bash script to drop and recreate the database schema.
- `query.sh`: A bash script to execute the queries in the `query.sql` file against the database.

## Setup

1. Ensure you have a PostgreSQL server running and accessible.
2. Create a new database for the Railway Tracker project.
3. Create a `.env` file in the same directory as the other files, and add the following lines, replacing the placeholders with your actual database connection details:

```text
DB_PASSWORD=your_database_password
DB_USERNAME=your_database_username
DB_NAME=your_database_name
DB_PORT=your_database_port
DB_IP=your_database_ip_or_hostname
```

4. Run the `clear.sh` script to create the database schema:

```bash
bash clear.sh
```

This script will drop any existing tables and recreate the schema based on the `schema.sql` file.

## Querying the Database

To execute the queries defined in the `query.sql` file, run the `query.sh` script:

```bash
bash query.sh
```

This script will connect to the database using the credentials from the `.env` file and execute the queries in the `query.sql` file. The results will be printed to the console.

## Database Schema

The `schema.sql` file defines the following tables:

- `operator`: Stores information about train operators.
- `station`: Stores information about railway stations.
- `users`: Stores user information for the Railway Tracker application.
- `cancel_code`: Stores codes and descriptions for cancellation reasons.
- `incident`: Stores information about incidents and disruptions on the railway network.
- `station_performance_archive`: Stores historical performance data for stations, including average delays and cancellation counts.
- `subscription`: Stores user subscriptions to receive updates from specific operators.
- `waypoint`: Stores information about scheduled and actual arrival and departure times for trains at stations.
- `cancellation`: Stores information about cancelled train services, including the cancellation reason and associated waypoint.
- `affected_operator`: Stores information about operators affected by a particular incident.

## Updating

When making changes to the database schema, follow these steps:

1. Update the `schema.sql` file with the desired changes.

2. Run the `clear.sh` script to apply the changes to your local database for testing.

3. Update the `query.sql` file with any new queries or modifications as needed.