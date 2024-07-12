# Realtime Trains

This folder provides functionality to retrieve real-time train information from the RealTime Trains API. For more information about RealTime Trains API, visit https://www.realtimetrains.co.uk/about/developer/pull/docs/. The API is queried using `api.rtt.io/api/v1/json/search/<filter>`. 

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.6 or later
- pip (Python package installer)

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

Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `realtime_trains` directory and add the following lines, replacing `YOUR_API_KEY` with your actual API key:

```text
NATIONAL_RAIL_API_KEY=YOUR_API_KEY
```

The script will automatically load the API key from this file.