import streamlit as st


def deploy_home_page():
    """This displays the main page of the dashboard."""
    st.set_page_config(layout="wide")
    st.title("Railway Tracker 🚆")


if __name__ == "__main__":
    deploy_home_page()
