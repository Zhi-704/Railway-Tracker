""" Loads the PDF summary report of RealTimeTrains data into an S3 bucket. """
from os import environ, path
import logging
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime

from boto3 import client
from botocore.exceptions import NoCredentialsError, ClientError
# from xhtml2pdf import pisa


def get_s3_client() -> client:
    """ Returns s3 client. """
    load_dotenv()
    try:
        s3_client = client('s3',
                           aws_access_key_id=environ['AWS_ACCESS_KEY'],
                           aws_secret_access_key=environ['AWS_SECRET_KEY'])
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def upload_pdf_data_to_s3(s3: client, bucket_name: str, s3_filename: str, pdf: BytesIO):
    """ Uploads pdf of summary report to S3 bucket. """

    s3.upload_fileobj(pdf, bucket_name, s3_filename)
    logging.info(f"pdf file uploaded: {s3_filename}")


def upload_pdf_to_s3():
    """ Uploads a PDF file from local directory into S3 bucket. """
    s3 = get_s3_client()
    bucket = environ['S3_BUCKET_NAME']
    prefix = datetime.now()
    local_file = 'report.pdf'
    s3_file_name = f"{prefix}_{local_file}"

    try:
        s3.upload_file(local_file, bucket, s3_file_name)
        print(f"Upload Successful: {s3_file_name} to bucket {bucket}")
        return True
    except FileNotFoundError:
        logging.error("The file was not found.")
        return False
    except Exception as e:
        logging.error(
            "Error occurred when connecting and uploading to S3 bucket.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    upload_pdf_to_s3()
