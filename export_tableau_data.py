import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

EXPORT_FOLDER = Path("tableau_exports")
EXPORT_FOLDER.mkdir(exist_ok=True)


EXPORTS = {
    "airline_performance.csv": """
        SELECT *
        FROM analytics.mart_airline_performance
        ORDER BY total_flights DESC;
    """,

    "route_performance.csv": """
        SELECT *
        FROM analytics.mart_route_performance
        ORDER BY total_flights DESC;
    """,

    "daily_operations.csv": """
        SELECT *
        FROM analytics.mart_daily_operations
        ORDER BY full_date;
    """,

    "executive_summary.csv": """
        SELECT
            COUNT(*) AS total_flights,

            COUNT(*) FILTER (
                WHERE NOT cancelled
            ) AS completed_flights,

            COUNT(*) FILTER (
                WHERE cancelled
            ) AS cancelled_flights,

            ROUND(
                100.0
                * COUNT(*) FILTER (WHERE cancelled)
                / NULLIF(COUNT(*), 0),
                2
            ) AS cancellation_rate_percent,

            ROUND(
                AVG(departure_delay_min),
                2
            ) AS avg_departure_delay_min,

            ROUND(
                AVG(arrival_delay_min),
                2
            ) AS avg_arrival_delay_min,

            ROUND(
                AVG(load_factor) * 100,
                2
            ) AS avg_load_factor_percent,

            SUM(seats_booked) AS total_seats_booked

        FROM analytics.fact_flights;
    """
}


if not DATABASE_URL:
    raise ValueError(
        "SUPABASE_DB_URL was not found in the .env file."
    )


connection = None

try:
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    print("Connected to Supabase.")

    for file_name, query in EXPORTS.items():
        cursor.execute(query)

        rows = cursor.fetchall()

        column_names = [
            description[0]
            for description in cursor.description
        ]

        output_path = EXPORT_FOLDER / file_name

        with output_path.open(
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)

            writer.writerow(column_names)
            writer.writerows(rows)

        print(
            f"Exported {len(rows):,} rows -> {output_path}"
        )

    print("\nTableau exports completed successfully.")

except Exception as error:
    print(f"\nExport failed: {error}")
    raise

finally:
    if connection:
        connection.close()
        print("Database connection closed.")