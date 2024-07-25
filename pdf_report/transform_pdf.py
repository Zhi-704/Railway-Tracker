"""Queries database then creates a performance pdf"""

import logging
from io import BytesIO
from base64 import b64encode

from xhtml2pdf import pisa
import altair as alt
import pandas as pd
from psycopg2.extensions import connection
from extract_pdf import get_connection, query_db

REPORT_NAME = "performance_report.pdf"
CSS_PATH = "./styles.css"


def get_cancelled_percentage(conn: connection) -> pd.DataFrame:
    """Calculates the percentage of cancelled trains for each station"""
    data = query_db(conn, """
        WITH total_trains AS (
            SELECT station_id, COUNT(*) AS total_count
            FROM waypoint
            WHERE run_date = CURRENT_DATE - 1
            GROUP BY station_id
        ),
        cancelled_trains AS (
            SELECT station_id, COUNT(*) AS cancelled_count
            FROM waypoint
            JOIN cancellation USING (waypoint_id)
            WHERE run_date = CURRENT_DATE - 1
            GROUP BY station_id
        )
        SELECT station_name, station_crs, cancelled_count, total_count,
            CASE
                WHEN total_count = 0 THEN 0
                ELSE ROUND((cancelled_count * 100.0 / total_count), 2)::FLOAT
            END AS cancellation_percentage
        FROM total_trains
        JOIN cancelled_trains USING (station_id)
        JOIN station USING (station_id)""")
    logging.info("percentage of cancelled trains for each station: %s", data)
    return pd.DataFrame(
        data, columns=['station_name', 'station_crs', 'cancellation_percentage'])


def get_delayed_percentage(conn: connection) -> pd.DataFrame:
    """Calculates the percentage of delay for arrivals and departures for each station"""
    data = query_db(conn, """
        WITH total_trains AS (
            SELECT station_id, COUNT(*) AS total_count
            FROM waypoint
            WHERE run_date = CURRENT_DATE - 1
            GROUP BY station_id
        ),
        delayed_arrival_trains AS (
            SELECT station_id, COUNT(*) AS count_arrive_delay
            FROM waypoint
            WHERE run_date = CURRENT_DATE - 1 
                AND EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 > 0 
            GROUP BY station_id
        ),
        delayed_departure_trains AS (
            SELECT station_id, COUNT(*) AS count_departure_delay
            FROM waypoint
            WHERE run_date = CURRENT_DATE - 1 
                AND EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60 > 0
            GROUP BY station_id
        )
        SELECT station_name, station_crs, total_count, count_arrive_delay, count_departure_delay,
            CASE
                WHEN total_count = 0 THEN 0
                ELSE ROUND((count_arrive_delay * 100.0 / total_count), 2)::FLOAT
            END AS delayed_arrival_percentage,
            CASE
                WHEN total_count = 0 THEN 0
                ELSE ROUND((count_departure_delay * 100.0 / total_count), 2)::FLOAT
            END AS delayed_departure_percentage
        FROM total_trains
        LEFT JOIN delayed_arrival_trains USING (station_id)
        LEFT JOIN delayed_departure_trains USING (station_id)
        JOIN station USING (station_id);""")
    logging.info(
        "percentage of trains with delay for arrivals and departures for each station: %s", data)
    return pd.DataFrame(data, columns=['station_name', 'station_crs', 'delayed_arrival_percentage',
                                       'delayed_departure_percentage'])


def get_avg_delay(conn: connection) -> pd.DataFrame:
    """Calculates the average overall delay for each station"""
    data = query_db(conn, """
        SELECT station_name, station_crs,
            ROUND(AVG(EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60), 2)::FLOAT
                AS avg_arrive_delay_minutes,
            ROUND(AVG(EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60), 2)::FLOAT
                AS avg_departure_delay_minutes
        FROM waypoint
        JOIN station USING (station_id)
        WHERE run_date = CURRENT_DATE - 1
        GROUP BY station_name, station_crs;""")
    logging.info("average delay for each station: %s", data)
    return pd.DataFrame(data, columns=['station_name', 'station_crs',
                                       'avg_arrive_delay_minutes', 'avg_departure_delay_minutes'])


def get_avg_delay_long(conn: connection) -> pd.DataFrame:
    """Calculates the average delay more than 1 min for each station"""
    data = query_db(conn, """
        SELECT station_name, station_crs,
            ROUND(AVG( EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60), 2)::FLOAT
                AS avg_arrive_delay_long_minutes,
            ROUND(AVG( EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60), 2)::FLOAT
                AS avg_departure_delay_long_minutes
        FROM waypoint
        JOIN station USING (station_id)
        WHERE EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 > 1 AND
            EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 > 1 AND
            run_date = CURRENT_DATE - 1
        GROUP BY station_name, station_crs;""")
    logging.info("average delay more than 1 min for each station: %s", data)
    return pd.DataFrame(data, columns=['station_name', 'station_crs',
                                       'avg_arrive_delay_long_minutes',
                                       'avg_departure_delay_long_minutes'])


def generate_grouped_bar_chart(df: pd.DataFrame, x_col: str,
                               y_cols: list[str], title: str, y_axis: str) -> alt.Chart:
    """Generates a grouped bar chart with separate bars for each station"""
    df = df.rename(columns={y_cols[0]: 'Arrival', y_cols[1]: 'Departure'})
    delay_types = ['Arrival', 'Departure']

    melted_df = df.melt(id_vars=x_col, value_vars=delay_types,
                        var_name='Delay Type', value_name='Minutes')

    chart = alt.Chart(melted_df).mark_bar().encode(
        x=alt.X('Delay Type:N', title=None),
        y=alt.Y('Minutes:Q', axis=alt.Axis(title=y_axis)),
        color=alt.Color('Delay Type:N', legend=None),
        column=alt.Column(f'{x_col}:N', title='Station CRS', header=alt.Header(
            labelAngle=0, labelAlign='center')),
        tooltip=[alt.Tooltip(x_col, title='Station CRS'), alt.Tooltip(
            'Minutes:Q', title=y_axis), 'Delay Type:N']
    ).properties(
        title=title,
        width=600/len(df[x_col].unique()),
        spacing=0
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_header(
        titleFontSize=14,
        labelFontSize=12
    )

    return chart


def generate_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> alt.Chart:
    """Generates a bar chart using Altair"""
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_col, title="Station CRS"),
        y=alt.Y(y_col, title="Percentage of Cancelled Trains (%)"),
        tooltip=[x_col, y_col]
    ).properties(
        title=title,
        width=600,
        height=400
    ).configure_axis(
        labelAngle=0
    )


def convert_altair_chart_to_html_embed(chart: alt.Chart) -> str:
    """Converts an Altair chart to a string representation."""
    with BytesIO() as bs:
        chart.save(bs, format="png")
        bs.seek(0)
        data = b64encode(bs.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"


def convert_html_to_pdf(source_html: str, output_filename: str) -> bool:
    """Outputs HTML to a target file."""
    with open(output_filename, "w+b") as f:
        pisa_status = pisa.CreatePDF(source_html, dest=f)
    return pisa_status.err


def transform_pdf() -> None:
    """Main function which creates pdf"""
    conn = get_connection()
    cancelled_df = get_cancelled_percentage(conn)
    delayed_df = get_delayed_percentage(conn)
    avg_delay_df = get_avg_delay(conn)
    avg_delay_long_df = get_avg_delay_long(conn)
    conn.close()

    cancellation_chart = generate_bar_chart(
        cancelled_df, 'station_crs', 'cancellation_percentage',
        'Cancellation Percentage by Station (%)')
    delay_chart = generate_grouped_bar_chart(
        delayed_df, 'station_crs',
        ['delayed_arrival_percentage',
            'delayed_departure_percentage'], 'Delay Percentage by Station',
        'Percentage of Delayed Trains (%)')
    avg_delay_chart = generate_grouped_bar_chart(
        avg_delay_df, 'station_crs',
        ['avg_arrive_delay_minutes',
            'avg_departure_delay_minutes'], 'Average Delay by Station',
        'Average Delay (minutes)')
    avg_delay_long_chart = generate_grouped_bar_chart(
        avg_delay_long_df, 'station_crs',
        ['avg_arrive_delay_long_minutes', 'avg_departure_delay_long_minutes'],
        'Average Delay more than 1 min by Station', 'Average Delay more than 1 min (minutes)')

    cancellation_chart_embed = convert_altair_chart_to_html_embed(
        cancellation_chart)
    delay_chart_embed = convert_altair_chart_to_html_embed(delay_chart)
    avg_delay_chart_embed = convert_altair_chart_to_html_embed(avg_delay_chart)
    avg_delay_long_chart_embed = convert_altair_chart_to_html_embed(
        avg_delay_long_chart)

    station_info = delayed_df[['station_name',
                               'station_crs']].drop_duplicates()

    station_info_html = "<p><b>Station CRS</b> - <b>Station Name</b></p><ul>"
    for _, row in station_info.iterrows():
        station_info_html += f"<li>{row['station_crs']}\
              - {row['station_name']}</li>"
    station_info_html += "</ul>"

    html_report = f"""
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta charset="utf-8"/>
            <title>Train Delay and Cancellation Report</title>
            <link rel="stylesheet" type="text/css" href="{CSS_PATH}"/>
        </head>
        <body>
            <h1>Train Delay and Cancellation Report</h1>
            <img src="{cancellation_chart_embed}" alt="Cancellation Chart">
            <img src="{delay_chart_embed}" alt="Arrival Delay Chart">
            <img src="{avg_delay_chart_embed}" alt="Overall Delay Chart">
            <img src="{avg_delay_long_chart_embed}" alt="Long Delay Chart">

            <h2>Station Common Reporting Standard (CRS)<h2>
            <p>Station CRS is a unique identifier for each station in the UK.
            It is used to identify the station in the train timetable data.</p>
            {station_info_html}
        </body>
        </html>
    """

    result = convert_html_to_pdf(html_report, REPORT_NAME)

    if result:
        logging.error("Failed to create PDF report.")
    else:
        logging.info("PDF report created successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    transform_pdf()
