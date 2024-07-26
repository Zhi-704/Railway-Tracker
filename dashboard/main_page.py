"""Main page for the dashboard, authored by fm1psy"""

import pandas
import streamlit as st
import altair as alt
from st_pages import Page, show_pages

from main_page_functions import (get_avg_delays_all, get_avg_delays_over_a_minute, get_avg_delay,
                                 get_cancellations_per_operator, get_closest_scheduled_incident,
                                 get_delay_count_over_5_minutes_per_operator,
                                 get_greatest_delay, get_proportion_of_large_delays_per_operator,
                                 get_rolling_avg, get_rolling_cancellation_per_operator,
                                 get_station_with_highest_delay, get_total_delays_for_every_station,
                                 get_trains_cancelled_per_station_percentage)

TIME_RANGE_OPTIONS = ["last day", "last week", "All time"]
TIME_RANGE_OPTIONS_DICT = {
    "last day": '24 hours', "last week": '128 hours', "All time": None}

LOGO_URL = "../diagrams/train_logo.png"
LOGO_ICON_URL = "../diagrams/train_logo.png"

ROLLING_AVG_BEFORE = 7
ROLLING_AVG_AFTER = 0


def display_total_delays(date_range: str, time_group: str) -> alt.Chart:
    """return a bar chart with the total delays per station"""
    try:
        total_delays_df = pandas.DataFrame(
            get_total_delays_for_every_station(date_range, time_group))
        total_delays_df["total_delay_minutes"] = total_delays_df["total_delay_minutes"].astype(
            float)

        return alt.Chart(total_delays_df).mark_bar().encode(
            y=alt.Y("station_name").title("Station Name").sort("x"),
            x=alt.X("total_delay_minutes").title("Total Delay (mins)")
        )
    except Exception as e:  # pylint:disable=broad-exception-caught
        st.error(e)
        return None


def display_train_cancellation_percentage(date_range: str, time_group: str) -> alt.Chart:
    """return a bar chart with the cancellation percentage for every station"""
    try:
        train_percentages_df = pandas.DataFrame(
            get_trains_cancelled_per_station_percentage(date_range, time_group))
        train_percentages_df["cancel_percent"] = train_percentages_df["cancel_percent"].astype(
            float)
        return alt.Chart(train_percentages_df).mark_bar().encode(
            x=alt.X("cancel_percent", title="% of trains cancelled"),
            y=alt.Y("station_name", title="Station Name", sort="x")
        )
    except Exception as e:  # pylint:disable=broad-exception-caught
        st.error(e)
        return None


def display_avg_delay_all(date_range, time_group) -> alt.Chart:
    """return a bar chart with an average delay in minutes per station"""
    try:
        average_delay_df = pandas.DataFrame(
            get_avg_delays_all(date_range, time_group))
        average_delay_df["avg_arrival_delay"] = average_delay_df["avg_arrival_delay"].astype(
            float)
        average_delay_df["avg_departure_delay"] = average_delay_df["avg_departure_delay"].astype(
            float)
        delay_value = "avg_departure_delay" if time_group == "departure" else "avg_arrival_delay"
        return alt.Chart(average_delay_df).mark_bar().encode(
            y=alt.Y("station_name", title="Station Name", sort="x"),
            x=alt.X(delay_value, title="Average delay in Minutes")
        )
    except Exception as e:  # pylint:disable=broad-exception-caught
        st.error(e)
        return None


def display_avg_delays_over_a_minute(date_range: str, time_group: str) -> alt.Chart:
    """return a bar chart with an average delay in minutes per station
    only for delays longer than a minute"""
    try:
        avg_delay_long_df = pandas.DataFrame(
            get_avg_delays_over_a_minute(date_range))
        avg_delay_long_df["avg_arrival_delay"] = avg_delay_long_df["avg_arrival_delay"].astype(
            float)
        avg_delay_long_df["avg_departure_delay"] = avg_delay_long_df["avg_departure_delay"].astype(
            float)

        delay_value = "avg_arrival_delay" if time_group == "arrival" else "avg_departure_delay"
        return alt.Chart(avg_delay_long_df).mark_bar().encode(
            y=alt.Y("station_name", title="Station Name", sort="x"),
            x=alt.X(delay_value,
                    title="Average delay (over a minute long)")
        )
    except Exception as e:  # pylint:disable=broad-exception-caught
        st.error(e)
        return None


def display_rolling_avg_delay() -> alt.Chart:
    """return a bar chart with a rolling average to show the average delay for each day"""
    try:
        rolling_avg_df = pandas.DataFrame(get_rolling_avg())
        rolling_avg_df["average_delay"] = rolling_avg_df["average_delay"].astype(
            float)

        bar_chart = alt.Chart(rolling_avg_df).mark_bar().encode(
            x=alt.X("run_date", title="Date"),
            y=alt.Y("average_delay", title="Average Delay (mins)")
        )

        line = alt.Chart(rolling_avg_df).mark_line(color='red').transform_window(
            # The field to average
            rolling_mean='mean(average_delay)',
            # The number of values before and after the current value to include.
            frame=[ROLLING_AVG_BEFORE, ROLLING_AVG_AFTER]
        ).encode(
            x='run_date',
            y='rolling_mean:Q'
        )

        return bar_chart+line
    except Exception as e:  # pylint:disable=broad-exception-caught
        st.error(e)
        return None


def display_avg_delay_comparisons() -> alt.Chart:
    """return a table showing the comparisons between the average day yesterday and the day before
    do this for every station"""
    try:
        avg_delays_df = pandas.DataFrame(
            get_avg_delay()).set_index("station_name")
        avg_delays_df["avg_delay_yday"] = avg_delays_df["avg_delay_yday"].astype(  # pylint: disable=unsupported-assignment-operation,unsubscriptable-object
            float)
        avg_delays_df["avg_delay_day_before"] = avg_delays_df["avg_delay_day_before"].astype(  # pylint: disable=unsupported-assignment-operation,unsubscriptable-object
            float)

        avg_delays_df = avg_delays_df.rename(columns={
            "station_name": "Station",
            "avg_delay_yday": "Yesterday",
            "avg_delay_day_before": "Day Before"
        })

        return avg_delays_df
    except Exception as e:  # pylint:disable=broad-exception-caught
        st.error(e)
        return None


def deploy_station_dashboard():
    """deploy the station dashboard tab"""
    st.subheader("Next scheduled incident: ")
    closest_future_incident = get_closest_scheduled_incident()
    if closest_future_incident:
        st.write(closest_future_incident)
    else:
        st.write("No incident scheduled in the near future could be found.")

    date_range = st.selectbox(
        "Select the span of time for the dashboard", TIME_RANGE_OPTIONS)
    time_group = st.radio("Select what group of times to analyse",
                          ["arrival", "departure", "sum total"])
    st.subheader(f"Station with the highest delay since ({date_range})")
    date_range = TIME_RANGE_OPTIONS_DICT[date_range]
    st.write(get_station_with_highest_delay(date_range, time_group))

    proportions_column = st.columns(2, gap="large")
    with proportions_column[0]:
        st.subheader("Greatest Delay by any station")
        st.write(get_greatest_delay(date_range, time_group))
    with proportions_column[1]:
        st.subheader("Comparison of average delay per station in minutes")
        st.write(display_avg_delay_comparisons())

    st.header("Sum Delays")
    bar_charts = st.columns(2, gap="large")
    with bar_charts[0]:
        st.subheader("Total Delay in minutes by Station")
        st.altair_chart(display_total_delays(date_range, time_group))
    with bar_charts[1]:
        st.subheader("Percentage of Trains cancelled per station")
        st.altair_chart(display_train_cancellation_percentage(
            date_range, time_group))

    st.header("Average Delays")
    delays = st.columns(2, gap="large")
    with delays[0]:
        st.subheader("Total")
        st.altair_chart(display_avg_delay_all(date_range, time_group))
    with delays[1]:
        st.subheader("Delays over a minute")
        st.altair_chart(display_avg_delays_over_a_minute(
            date_range, time_group))

    st.subheader("Rolling average for the average delay in minutes")
    st.altair_chart(display_rolling_avg_delay(), use_container_width=True)


def display_cancellations_per_operator():
    """return a pie chart of the total cancellations on each operator"""
    cancellations_df = pandas.DataFrame(get_cancellations_per_operator())

    pie = alt.Chart(cancellations_df).mark_arc(radius=125).encode(
        theta=alt.Theta("number_of_cancellations",
                        title="Number of Cancellations", stack=True),
        color=alt.Color("operator_name", title="Operator")
    )

    text = pie.mark_text(radius=145, size=20).encode(
        text="number_of_cancellations")

    return pie + text


def display_5_min_delays_per_operator():
    """return a bar chart showing the number of delayed trains per operator"""
    five_min_delays_df = pandas.DataFrame(
        get_delay_count_over_5_minutes_per_operator())

    pie = alt.Chart(five_min_delays_df).mark_bar().encode(
        x=alt.X("number_of_delayed_trains", title="Number of trains delayed"),
        y=alt.Y("operator_name", title="Operator", sort="x")
    )

    return pie


def display_proportion_of_long_delays_per_operator():
    """return a bar chart showing the percentage of trains delayed per operator"""
    operator_long_delays_df = pandas.DataFrame(
        get_proportion_of_large_delays_per_operator())

    operator_long_delays_df["percent_delayed"] = operator_long_delays_df["percent_delayed"].astype(
        float)

    return alt.Chart(operator_long_delays_df).mark_bar().encode(
        x=alt.X("percent_delayed", title="% of trains delayed"),
        y=alt.Y("operator_name", title="Operator", sort="x")
    )


def display_rolling_total_delays():
    """return a bar chart with a rolling average for the total delays per operator"""
    rolling_delays_df = pandas.DataFrame(
        get_rolling_cancellation_per_operator())
    rolling_delays_df["total_delayed_trains"] = rolling_delays_df["total_delayed_trains"].astype(
        float)

    bar_chart = alt.Chart(rolling_delays_df).mark_bar().encode(
        x=alt.X("run_date", title="Date"),
        y=alt.Y("total_delayed_trains", title="Number of Delays")
    )

    line = alt.Chart(rolling_delays_df).mark_line(color='red').transform_window(
        # The field to average
        rolling_mean='mean(total_delayed_trains)',
        # The number of values before and after the current value to include.
        frame=[ROLLING_AVG_BEFORE, ROLLING_AVG_AFTER]
    ).encode(
        x='run_date',
        y='rolling_mean:Q'
    )

    return bar_chart + line


def deploy_operator_dashboard():
    """deploy the operator dashboard tab"""

    st.subheader("Proportion of cancellations per Operator")
    column = st.columns(1)
    with column[0]:
        st.altair_chart(display_cancellations_per_operator(),
                        use_container_width=True)

    st.subheader("Data on train delays over five minutes")
    cancellations_column = st.columns(2, gap="large")
    with cancellations_column[0]:
        st.altair_chart(display_5_min_delays_per_operator())
    with cancellations_column[1]:
        st.altair_chart(display_proportion_of_long_delays_per_operator())

    st.subheader("Total delays per day")
    st.altair_chart(display_rolling_total_delays(), use_container_width=True)


def deploy_home_page():
    """This displays the main page of the dashboard."""
    st.set_page_config(
        layout="wide", page_title="Railway Tracker", page_icon=LOGO_URL)

    st.logo(LOGO_URL, icon_image=LOGO_ICON_URL)
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

    tab1, tab2 = st.tabs(["Stations", "Operators"])
    with tab1:
        deploy_station_dashboard()
    with tab2:
        deploy_operator_dashboard()


if __name__ == "__main__":
    deploy_home_page()
