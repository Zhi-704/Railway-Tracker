"""Main page for the dashboard, authored by fm1psy"""
import pandas
import streamlit as st
import altair as alt
from st_pages import Page, show_pages
from main_page_functions import get_average_delays_all, get_average_delays_over_a_minute, get_avg_delay, get_cancellations_per_operator, get_closest_scheduled_incident, get_rolling_average, get_station_with_highest_delay, get_total_delays_for_every_station, get_trains_cancelled_per_station_percentage

TIME_RANGE_OPTIONS = ["last day", "last week", "All time"]
TIME_RANGE_OPTIONS_DICT = {
    "last day": '24 hours', "last week": '128 hours', "All time": None}

LOGO_URL = "../diagrams/train_logo.png"
LOGO_ICON_URL = "../diagrams/train_logo.png"


def display_total_delays(date_range: str) -> alt.Chart:
    """"""
    total_delays_df = pandas.DataFrame(
        get_total_delays_for_every_station(date_range))
    total_delays_df["total_delay_minutes"] = total_delays_df["total_delay_minutes"].astype(
        float)

    return alt.Chart(total_delays_df).mark_bar().encode(
        y=alt.Y("station_name").title("Station Name").sort("x"),
        x=alt.X("total_delay_minutes").title("Total Delay (mins)")
    )


def display_train_cancellation_proportion() -> alt.Chart:
    """"""
    return alt.Chart()
    # pie = alt.Chart(train_cancellation_percentages_df).mark_arc(innerRadius=50, radius=100).encode(
    #     theta=alt.Theta("cancellation_percentage").stack(True),
    #     color=alt.Color("station_name").legend(None)
    # )
    # text = pie.mark_text(radius=120, size=20).encode(
    #     text="cancellation_percentage")

    # return pie+text


def display_train_cancellation_percentage() -> alt.Chart:
    """"""
    train_cancellation_percentages_df = pandas.DataFrame(
        get_trains_cancelled_per_station_percentage())
    train_cancellation_percentages_df["cancellation_percentage"] = train_cancellation_percentages_df["cancellation_percentage"].astype(
        float)
    return alt.Chart(train_cancellation_percentages_df).mark_bar().encode(
        x=alt.X("cancellation_percentage", title="% of trains cancelled"),
        y=alt.Y("station_name", title="Station Name", sort="x")
    )


def display_average_delay_all() -> alt.Chart:
    """"""
    average_delay_df = pandas.DataFrame(get_average_delays_all())
    average_delay_df["avg_arrival_delay_minutes"] = average_delay_df["avg_arrival_delay_minutes"].astype(
        float)
    average_delay_df["avg_departure_delay_minutes"] = average_delay_df["avg_departure_delay_minutes"].astype(
        float)
    return alt.Chart(average_delay_df).mark_bar().encode(
        y=alt.Y("station_name", title="Station Name", sort="x"),
        x=alt.X("avg_arrival_delay_minutes", title="Average delay in Minutes")
    )


def display_average_delays_over_a_minute() -> alt.Chart:
    """"""
    avg_delay_long_df = pandas.DataFrame(get_average_delays_over_a_minute())
    avg_delay_long_df["avg_overall_delay_minutes"] = avg_delay_long_df["avg_overall_delay_minutes"].astype(
        float)
    return alt.Chart(avg_delay_long_df).mark_bar().encode(
        y=alt.Y("station_name", title="Station Name", sort="x"),
        x=alt.X("avg_overall_delay_minutes",
                title="Average delay (over a minute long)")
    )


def display_rolling_average_delay() -> alt.Chart:
    """"""
    rolling_avg_df = pandas.DataFrame(get_rolling_average())
    rolling_avg_df["average_delay_in_minutes"] = rolling_avg_df["average_delay_in_minutes"].astype(
        float)

    bar = alt.Chart(rolling_avg_df).mark_bar().encode(
        x=alt.X("run_date", title="Date"),
        y=alt.Y("average_delay_in_minutes", title="Average Delay (mins)")
    )

    line = alt.Chart(rolling_avg_df).mark_line(color='red').transform_window(
        # The field to average
        rolling_mean='mean(average_delay_in_minutes)',
        # The number of values before and after the current value to include.
        frame=[-7, 0]
    ).encode(
        x='run_date',
        y='rolling_mean:Q'
    )

    return (bar+line)


def display_avg_delay_comparisons() -> alt.Chart:
    """"""
    avg_delays_per_station_df = pandas.DataFrame(get_avg_delay())
    avg_delays_per_station_df["avg_delay_yesterday_mins"] = avg_delays_per_station_df["avg_delay_yesterday_mins"].astype(
        float)
    avg_delays_per_station_df["avg_delay_day_before_mins"] = avg_delays_per_station_df["avg_delay_day_before_mins"].astype(
        float)

    # for row in avg_delays_per_station_df:
    #     st.metric("sun", value=row["avg_delay_yesterday_mins"],
    #               delta=row["avg_delay_day_before_mins"])


def deploy_station_dashboard():
    """"""
    st.subheader("Next scheduled incident: ")
    closest_future_incident = get_closest_scheduled_incident()
    if closest_future_incident:
        st.write(closest_future_incident)
    else:
        st.write("No incident scheduled in the near future could be found.")

    date_range = st.selectbox(
        "Select the span of time for the dashboard", TIME_RANGE_OPTIONS)
    st.subheader(f"Station with the highest delay since ({date_range})")
    date_range = TIME_RANGE_OPTIONS_DICT[date_range]
    st.write(get_station_with_highest_delay(date_range))

    # TODO: change statistics collected
    sigma = st.radio("label", ["arrival", "departure", "sum total"])

    proportions_column = st.columns(2, gap="large")
    with proportions_column[0]:
        st.altair_chart(display_train_cancellation_percentage())
    with proportions_column[1]:
        ...
        # st.altair_chart(display_train_cancellation_proportion())

    bar_charts = st.columns(2, gap="large")
    with bar_charts[0]:
        st.subheader("Total Delay in minutes by Station")
        st.altair_chart(display_total_delays(date_range))
    with bar_charts[1]:
        st.subheader("Percentage of Trains cancelled per station")
        st.altair_chart(display_train_cancellation_percentage())

    st.header("Place Holder header")
    delays = st.columns(2, gap="large")
    with delays[0]:
        st.subheader("Delay all")
        st.altair_chart(display_average_delay_all())
    with delays[1]:
        st.subheader("Delay over")
        st.altair_chart(display_average_delays_over_a_minute())

    overall_stats = st.columns(2, gap="large")
    with overall_stats[0]:
        st.subheader("Rolling average for the average delay in minutes")
        st.altair_chart(display_rolling_average_delay())
    with overall_stats[1]:
        st.write(display_avg_delay_comparisons())


def display_cancellations_per_operator():
    """"""
    cancellations_df = pandas.DataFrame(get_cancellations_per_operator())

    pie = alt.Chart(cancellations_df).mark_arc().encode(
        theta=alt.Theta("number_of_cancellations", stack=True),
        color=alt.Color("operator_name")
    )

    text = pie.mark_text(radius=175, size=20).encode(
        text="number_of_cancellations")

    return (pie + text).properties(width=600)


def deploy_operator_dashboard():
    """"""
    cancellations_column = st.columns(2, gap="large")

    with cancellations_column[0]:
        st.altair_chart(display_cancellations_per_operator())


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
