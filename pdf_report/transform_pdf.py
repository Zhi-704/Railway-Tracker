import logging
from io import BytesIO
from base64 import b64encode

from xhtml2pdf import pisa
import altair as alt
import pandas as pd
from psycopg2.extensions import connection
from extract_pdf import get_connection, query_db


def get_cancelled_percentage(conn: connection) -> pd.DataFrame:
    """Calculates the percentage of cancelled trains for each station"""
    data = query_db(conn,
                    """WITH total_trains AS (
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
                    SELECT station_id, station_crs, station_name, cancelled_count, total_count,
                        CASE
                            WHEN total_count = 0 THEN 0
                            ELSE ROUND((cancelled_count * 100.0 / total_count), 2)
                        END AS cancellation_percentage
                    FROM total_trains
                    JOIN cancelled_trains USING (station_id)
                    JOIN station USING (station_id)""")
    logging.info("percentage of cancelled trains for each station: %s", data)
    df = pd.DataFrame(data, columns=['station_id', 'station_crs', 'station_name',
                      'cancelled_count', 'total_count', 'cancellation_percentage'])
    df['cancellation_percentage'] = df['cancellation_percentage'].astype(float)
    return df


def get_delayed_percentage(conn: connection) -> pd.DataFrame:
    """Calculates the average delay for arrivals and departures for each station"""
    data = query_db(conn,
                    """SELECT station_name,
                    ROUND(AVG(EXTRACT(EPOCH FROM(actual_arrival - booked_arrival)) / 60), 2)
                    AS avg_arrival_delay_minutes,
                    ROUND(AVG(EXTRACT(EPOCH FROM(actual_departure - booked_departure)) / 60), 2)
                    AS avg_departure_delay_minutes
                    FROM waypoint
                    JOIN station USING (station_id)
                    WHERE run_date = CURRENT_DATE - 1
                    GROUP BY station_name""")
    logging.info(
        "average delay for arrivals and departures for each station: %s", data)
    df = pd.DataFrame(data, columns=[
                      'station_name', 'avg_arrival_delay_minutes', 'avg_departure_delay_minutes'])
    df['avg_arrival_delay_minutes'] = df['avg_arrival_delay_minutes'].astype(
        float)
    df['avg_departure_delay_minutes'] = df['avg_departure_delay_minutes'].astype(
        float)
    return df


def get_avg_delay(conn: connection) -> pd.DataFrame:
    """Calculates the average overall delay for each station"""
    data = query_db(conn,
                    """SELECT station_name,
                        ROUND(AVG(
                            EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 +
                            EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60
                        ), 2) AS avg_overall_delay_minutes
                    FROM waypoint
                    JOIN station USING (station_id)
                    WHERE run_date = CURRENT_DATE - 1
                    GROUP BY station_name;""")
    logging.info("average overall delay for each station: %s", data)
    df = pd.DataFrame(
        data, columns=['station_name', 'avg_overall_delay_minutes'])
    df['avg_overall_delay_minutes'] = df['avg_overall_delay_minutes'].astype(
        float)
    return df


def get_avg_delay_long(conn: connection) -> pd.DataFrame:
    """Calculates the average delay more than 1 min for each station"""
    data = query_db(conn,
                    """SELECT station_name,
                        ROUND(AVG( EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60), 2) 
                        AS avg_arrive_delay_long_minutes
                    FROM waypoint
                    JOIN station USING (station_id)
                    WHERE EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 > 1 AND run_date = CURRENT_DATE - 1
                    GROUP BY station_name;""")
    logging.info("average delay more than 1 min for each station: %s", data)
    df = pd.DataFrame(
        data, columns=['station_name', 'avg_arrive_delay_long_minutes'])
    df['avg_arrive_delay_long_minutes'] = df['avg_arrive_delay_long_minutes'].astype(
        float)
    return df


def generate_grouped_bar_chart(df: pd.DataFrame, x_col: str, y_col_1: str, y_col_2: str, title: str) -> alt.Chart:
    """Generates a grouped bar chart using Altair for two variables."""
    # Melting the DataFrame to get a single column for delay type
    melted_df = df.melt(id_vars=x_col, value_vars=[y_col_1, y_col_2],
                        var_name='Delay Type', value_name='Minutes')

    # Creating the grouped bar chart
    chart = alt.Chart(melted_df).mark_bar().encode(
        x=alt.X(f'{x_col}:N', axis=alt.Axis(title='Station Name'),
                scale=alt.Scale(paddingInner=0.3)),
        y=alt.Y('Minutes:Q', axis=alt.Axis(title='Delay (minutes)')),
        color=alt.Color('Delay Type:N', title='Type of Delay'),
        column=alt.Column('Delay Type:N', header=alt.Header(title='')),
        tooltip=[x_col, 'Minutes', 'Delay Type']
    ).properties(
        title=title,
        width=alt.Step(40)  # controls the width of each group of bars
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    return chart


def generate_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> alt.Chart:
    """Generates a bar chart using Altair"""
    return alt.Chart(df).mark_bar().encode(
        x=alt.X(x_col, title=x_col),
        y=alt.Y(y_col, title=y_col),
        tooltip=[x_col, y_col]
    ).properties(
        title=title,
        width=600,
        height=400
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
    return pisa_status.err  # Flag success or failure


def transform_pdf() -> None:
    """Main function which creates pdf"""
    conn = get_connection()

    # Fetch data from the database
    cancelled_df = get_cancelled_percentage(conn)
    delayed_df = get_delayed_percentage(conn)
    avg_delay_df = get_avg_delay(conn)
    avg_delay_long_df = get_avg_delay_long(conn)

    # Generate charts
    cancellation_chart = generate_bar_chart(
        cancelled_df, 'station_name', 'cancellation_percentage', 'Cancellation Percentage by Station')
    delay_chart = generate_grouped_bar_chart(
        delayed_df, 'station_name', 'avg_arrival_delay_minutes', 'avg_departure_delay_minutes', 'Average Delay by Station')
    avg_delay_chart = generate_bar_chart(
        avg_delay_df, 'station_name', 'avg_overall_delay_minutes', 'Average Overall Delay by Station')
    avg_delay_long_chart = generate_bar_chart(
        avg_delay_long_df, 'station_name', 'avg_arrive_delay_long_minutes', 'Average Long Delay by Station')

    # Convert charts to HTML embeddable format
    cancellation_chart_embed = convert_altair_chart_to_html_embed(
        cancellation_chart)
    delay_chart_embed = convert_altair_chart_to_html_embed(delay_chart)
    avg_delay_chart_embed = convert_altair_chart_to_html_embed(avg_delay_chart)
    avg_delay_long_chart_embed = convert_altair_chart_to_html_embed(
        avg_delay_long_chart)

    # Set styles filepath
    css_path = "./styles.css"

    # HTML template
    html_report = f"""
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta charset="utf-8" />
            <title>Train Delay and Cancellation Report</title>
            <link rel="stylesheet" type="text/css" href="{css_path}" />
        </head>
        <body>
            <h1>Train Delay and Cancellation Report</h1>
            <h2>Cancellation Percentage by Station</h2>
            <img src="{cancellation_chart_embed}" alt="Cancellation Chart">

            <h2>Average Arrival Delay by Station</h2>
            <img src="{delay_chart_embed}" alt="Arrival Delay Chart">

            <h2>Average Overall Delay by Station</h2>
            <img src="{avg_delay_chart_embed}" alt="Overall Delay Chart">

            <h2>Average Long Delay by Station</h2>
            <img src="{avg_delay_long_chart_embed}" alt="Long Delay Chart">
        </body>
        </html>
    """

    # Create the report
    result = convert_html_to_pdf(html_report, "train_delay_report.pdf")

    if result:
        logging.error("Failed to create PDF report.")
    else:
        logging.info("PDF report created successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    transform_pdf()
