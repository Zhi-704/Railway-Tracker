# National Rail

This folder contains code for interacting with the National Rail API to retrieve information about train services in the UK. For more information about National Rail API, visit https://raildata.org.uk/dataProduct/P-cf16832d-d971-46e7-8883-4fca2101d3fa/specification.

## Scripts
* ```national_rail.py``` - Runs the pipeline; calling all other scripts in the directory that are part of the ETL process.
* ```extract.py``` - Extracts the data from the NationalRail API.
* ```transform.py``` - Retrieves useful data from the NationalRail extracted data, and cleans it ready for insertion into the RDS database.
* ```load.py``` - Loads the cleaned NationalRail incident data into the RDS.
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

This will retrieve information about any incidents occurring in NationalRail. 

## Configuration

Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `national_rail` directory and add the following lines:

```text
NATIONAL_RAIL_API_KEY=YOUR_API_KEY

DB_USERNAME=YOUR_DB_USERNAME
DB_PASSWORD=YOUR_DB_PASSWORD
DB_NAME=YOUR_DB_NAME
DB_IP=YOUR_DB_HOST_IP_ADDRESS
DB_PORT=YOUR_DB_PORT

```

Replace 'YOUR_X' with your details.

The script will automatically load the API key from this file.