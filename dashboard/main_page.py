"""Main page for the dashboard, authored by fm1psy"""
import pandas
import streamlit as st
import altair as alt
from st_pages import Page, show_pages
from main_page_functions import get_average_delays_all, get_average_delays_over_a_minute, get_closest_scheduled_incident, get_station_with_highest_delay, get_total_delays_for_every_station, get_trains_cancelled_per_station_percentage

def display_total_delays() -> alt.Chart:
    """"""
    total_delays_df = pandas.DataFrame(get_total_delays_for_every_station())
    total_delays_df["total_delay_minutes"] = total_delays_df["total_delay_minutes"].astype(float)
    
    return alt.Chart(total_delays_df).mark_bar().encode(
        x=alt.X("station_name").title("Station Name"),
        y=alt.Y("total_delay_minutes").title("Total Delay (mins)")
    )

def display_train_cancellations() -> alt.Chart:
    """"""
    train_cancellation_percentages_df = pandas.DataFrame(get_trains_cancelled_per_station_percentage())
    train_cancellation_percentages_df["cancellation_percentage"] = train_cancellation_percentages_df["cancellation_percentage"].astype(float)
    pie= alt.Chart(train_cancellation_percentages_df).mark_arc(innerRadius=50, radius=100).encode(
        theta=alt.Theta("cancellation_percentage").stack(True),
        color=alt.Color("station_name").legend(None)
    )
    text = pie.mark_text(radius=120, size=20).encode(text="cancellation_percentage")

    return pie+text

def display_average_delay_all() -> alt.Chart:
    """"""
    average_delay_df = pandas.DataFrame(get_average_delays_all())
    average_delay_df["avg_arrival_delay_minutes"] = average_delay_df["avg_arrival_delay_minutes"].astype(float)
    average_delay_df["avg_departure_delay_minutes"] = average_delay_df["avg_departure_delay_minutes"].astype(float)
    arrival = alt.Chart(average_delay_df).mark_bar().encode(
        x=alt.X("station_name"),
        y=alt.Y("avg_arrival_delay_minutes")
    )
    departure = alt.Chart(average_delay_df).mark_bar().encode(
        x=alt.X("station_name"),
        y=alt.Y("avg_departure_delay_minutes")
    )
    return arrival+departure

def display_average_delays_over_a_minute() -> alt.Chart:
    """"""
    avg_delay_long_df = pandas.DataFrame(get_average_delays_over_a_minute())
    avg_delay_long_df["avg_overall_delay_minutes"] = avg_delay_long_df["avg_overall_delay_minutes"].astype(float)
    return alt.Chart(avg_delay_long_df).mark_bar().encode(
        x=alt.X("station_name"),
        y=alt.Y("avg_overall_delay_minutes")
    )


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
        st.write(closest_future_incident)
    else:
        st.write("No incident could be found.")

    st.subheader("Station with the highest delay")
    st.write(get_station_with_highest_delay())
    
    st.altair_chart(display_total_delays())

    st.altair_chart(display_train_cancellations())
    

    # st.write(get_average_delays_all())
    st.altair_chart(display_average_delay_all())

    st.altair_chart(display_average_delays_over_a_minute())

if __name__ == "__main__":
    deploy_home_page()
