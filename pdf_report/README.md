# PDF Report


## Scripts
* ```pdf_report.py``` - Runs the pipeline; calling all other scripts in the directory that are part of the ETL process of creating a PDF report.
* ```extract_pdf.py``` - Extracts the data from the RDS database.
* ```transform_pdf.py``` - Retrieves useful data from the NationalRail extracted data, and cleans it ready for insertion into the RDS database.
* ```load_pdf.py``` - Loads the cleaned NationalRail incident data into the RDS.
* ```test_x.py``` - All Python scripts prefixed with 'test' are used to test other Python scripts within the directory, ensuring functionality is working.


## Installation

1. Navigate to the project directory:

```bash
cd pdf_report
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

The main script to run the PDF Summary Report generation is `pdf_report.py`. You can run it with the following command:

```bash
python3 pdf_report.py
```

This will retrieve information about any incidents occurring in NationalRail. 

## Configuration

Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `pdf_report` directory and add the following lines:

```text
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_access_key

DB_PASSWORD=your_database_password
DB_USERNAME=your_database_username
DB_NAME=your_database_name
DB_PORT=your_database_port
DB_IP=your_database_ip_or_hostname

SOURCE_EMAIL=your_email_to_send_ses
S3_BUCKET_NAME=your_s3_bucket_name 
```

The script will automatically load the API key from this file.
