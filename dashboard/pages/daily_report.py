"""
creates a page in the dashboard that allows users to subscribe to a summary report that
is emailed to them every day. These reports are also stored in an S3 bucket
"""
from boto3 import client
from dotenv import load_dotenv
import streamlit as st
from os import environ


def get_s3_client() -> client:
    """"""
    try:
        s3_client = client('s3',
                           aws_access_key_id=environ['AWS_ACCESS_KEY'],
                           aws_secret_access_key=environ['AWS_SECRET_KEY'])
        return s3_client
    except Exception as e:
        print(e)
        return None


def deploy_page():
    """"""
    st.title("Summary Report")
    st.subheader(
        "If you wish to subscribe to a daily report on our tracking results, submit your email below.")


if __name__ == "__main__":
    load_dotenv()
    deploy_page()
