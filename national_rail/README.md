# National Rail

This folder contains code for interacting with the National Rail API to retrieve information about train services in the UK. For more information about National Rail API, visit https://raildata.org.uk/dataProduct/P-cf16832d-d971-46e7-8883-4fca2101d3fa/specification.

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.6 or later
- pip (Python package installer)

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

This will prompt you to enter a station name or code. After providing the input, the script will retrieve and display information about the next few train services for that station.

## Configuration

Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `national_rail` directory and add the following lines, replacing `YOUR_API_KEY` with your actual API key:

```text
NATIONAL_RAIL_API_KEY=YOUR_API_KEY
```

The script will automatically load the API key from this file.