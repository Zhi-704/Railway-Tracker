import logging
from dotenv import load_dotenv

from transform_pdf import transform_pdf
from load_pdf import load_pdf

REPORT_FILENAME = 'performance_report.pdf'


def main(_event, _context):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    try:
        logging.info("Report PDF pipeline has started")

        transform_pdf(REPORT_FILENAME)
        logging.info(
            "Extracting & Transforming to create a PDF Summary Report complete.")

        load_pdf(REPORT_FILENAME)
        logging.info("Loading to S3 and sending emails complete.")

    except Exception as e:
        logging.error(
            "An error occurred during the PDF Report pipeline execution: %s", e)

    logging.info("Report pipeline has ended.")
