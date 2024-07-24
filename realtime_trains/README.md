# Realtime Trains

This folder provides functionality to retrieve real-time train information from the RealTime Trains API. For more information about RealTime Trains API, visit https://www.realtimetrains.co.uk/about/developer/pull/docs/. The API is queried using `api.rtt.io/api/v1/json/search/<filter>`. 

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

This will prompt you to enter a station name or code. After providing the input, the script will fetch and display real-time information about the next few train services for that station, including their current status and expected arrival/departure times.

## Configuration

Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `realtime_trains` directory and add the following lines, replacing `your_username` and `your_password` with your actual username and password:

```text
REALTIME_USERNAME=your_username
REALTIME_PASSWORD=your_password
DB_USERNAME=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
DB_IP=your_db_host_ip_address
DB_PORT=your_db_port
```

The script will automatically load the username and password from this file.