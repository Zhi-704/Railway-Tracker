"""Main page for the dashboard, authored by fm1psy"""
import streamlit as st
from st_pages import Page, show_pages
import main_page_functions as mpf

def deploy_home_page():
    """This displays the main page of the dashboard."""
    st.set_page_config(layout="wide")

    show_pages(
        [
            Page("main_page.py", "Home", "🏠"),
            Page("pages/daily_report.py",
                 "Summary Report", "📄"),
            Page("pages/incident_alerts.py",
                 "Train Alerts", "⚠️")
        ]
    )
    st.title("Railway Tracker 🚆")
    st.subheader("Next scheduled incident: ")
    st.write(mpf.get_closest_scheduled_incident())

if __name__ == "__main__":
    deploy_home_page()
