# National Rail

This folder contains code for interacting with the National Rail API to retrieve information about train services in the UK. For more information about National Rail API, visit https://raildata.org.uk/dataProduct/P-cf16832d-d971-46e7-8883-4fca2101d3fa/specification.

## Scripts
* ```national_rail.py``` - Runs the pipeline; calling all other scripts in the directory that are part of the ETL process.
* ```extract_national.py``` - Extracts the data from the NationalRail API.
* ```transform_national.py``` - Retrieves useful data from the NationalRail extracted data, and cleans it ready for insertion into the RDS database.
* ```load_national.py``` - Loads the cleaned NationalRail incident data into the RDS.
* ```sns_reporting.py``` - Alerts any users of incidents that affects their subscribed operator/s.
* ```test_x.py``` - All Python scripts prefixed with 'test' are used to test other Python scripts within the directory, ensuring functionality is working.


## Installation

1. Navigate to the project directory:

```bash
cd national_rail
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

The main script to interact with the National Rail API is `national_rail.py`. You can run it with the following command:

```bash
python3 national_rail.py
```

This will retrieve information about any incidents occurring in NationalRail as well as alert any users of recent incidents. 

## Configuration

Before running the script, you need to set up your National Rail API and AWS credentials. Create a new file called `.env` in the `national_rail` directory and add the following lines:

```text
NATIONAL_RAIL_API_KEY=your_api_key

DB_PASSWORD=your_database_password
DB_USERNAME=your_database_username
DB_NAME=your_database_name
DB_PORT=your_database_port
DB_IP=your_database_ip_or_hostname

ACCESS_KEY=your_aws_key
SECRET_ACCESS_KEY=your_secret_aws_key
```

The script will automatically load the API key from this file.