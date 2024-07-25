# PDF Report

<<<<<<< HEAD
## Configuration
Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `pdf_report` directory and add the following lines:
```text
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_access_key
=======


## Configuration

Before running the script, you need to set up your National Rail API credentials. Create a new file called `.env` in the `pdf_report` directory and add the following lines:

```text
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_access_key

>>>>>>> f4497c0b8683b533fbec2a5e7ec4b41c01b69832
DB_PASSWORD=your_database_password
DB_USERNAME=your_database_username
DB_NAME=your_database_name
DB_PORT=your_database_port
DB_IP=your_database_ip_or_hostname
<<<<<<< HEAD
SOURCE_EMAIL=your_email_to_send_ses
S3_BUCKET_NAME=your_s3_bucket_name
```
The script will automatically load the API key from this file.
=======

SOURCE_EMAIL=your_email_to_send_ses
S3_BUCKET_NAME=your_s3_bucket_name 
```

The script will automatically load the API key from this file.
>>>>>>> f4497c0b8683b533fbec2a5e7ec4b41c01b69832
