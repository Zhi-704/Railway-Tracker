"""Main page for the dashboard, authored by fm1psy"""
import streamlit as st
from st_pages import Page, show_pages
from main_page_functions import get_closest_scheduled_incident, get_station_with_highest_delay, get_total_delays_for_every_station, get_trains_cancelled_per_station_percentage

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
    closest_future_incident = get_closest_scheduled_incident()
    if closest_future_incident:
        st.write(get_closest_scheduled_incident())
    else:
        st.write("No incident could be found.")

    st.subheader("Station with the highest delay")
    st.write(get_station_with_highest_delay())
    st.write(get_total_delays_for_every_station())

    st.write(get_trains_cancelled_per_station_percentage())

if __name__ == "__main__":
    deploy_home_page()
