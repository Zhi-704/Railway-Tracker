"""
creates a page in the dashboard that allows users to subscribe to a summary report that
is emailed to them every day. These reports are also stored in an S3 bucket
"""
import streamlit as st


def deploy_page():
    """"""
    st.title("Summary Report")
    st.subheader(
        "If you wish to subscribe to a daily report on our tracking results, submit your email below.")


if __name__ == "__main__":
    deploy_page()
