# Realtime Trains

This folder provides functionality to retrieve real-time train information from the Realtime Trains API. For more information about Realtime Trains API, visit https://www.realtimetrains.co.uk/about/developer/pull/docs/. The API is queried using `api.rtt.io/api/v1/json/search/<filter>`. 

## Scripts
* ```realtime_trains.py``` - Runs the pipeline; calling all other scripts in the directory that are part of the ETL process.
* ```extract_real.py``` - Extracts the data from the Realtime trains API.
* ```transform_real.py``` - Retrieves useful data from the Realtime Trains extracted data, and cleans it ready for insertion into the RDS database.
* ```load_real.py``` - Loads the cleaned Realtime Trains data into the RDS.
* ```test_x.py``` - All Python scripts prefixed with 'test' are used to test other Python scripts within the directory, ensuring functionality is working.

## Installation

1. Navigate to the project directory:

```bash
cd realtime_trains
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

The main script to retrieve real-time train information is `realtime_trains.py`. You can run it with the following command:

```bash
python3 realtime_trains.py
```

This will import all of yesterday's arrivals/departures into the relational database from the listed stations:
-  Bath Spa Rail Station
- Edinburgh Rail Station
- Leeds Rail Station
- London Liverpool Street Rail Station
- Liverpool Central Rail Station
- Southampton Central Rail Station
- York Rail Station

## Configuration

Before running the script, you need to set up your Realtime Trains API credentials. Create a new file called `.env` in the `realtime_trains` directory and add the following lines, replacing `your_username` and `your_password` with your actual username and password given by Realtime Trains:

```text
REALTIME_USERNAME=your_username
REALTIME_PASSWORD=your_password

DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DB_IP=your_DB_IP_ip_address
DB_PORT=your_db_port
```

The script will automatically load the username and password from this file.