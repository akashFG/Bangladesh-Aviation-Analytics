import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL was not found in .env")

processed_root = Path("pipeline_data/processed")

date_folders = sorted(
    [folder for folder in processed_root.iterdir() if folder.is_dir()],
    reverse=True
)

if not date_folders:
    raise FileNotFoundError("No processed-data folder found.")

latest_folder = date_folders[0]

print(f"Loading data from: {latest_folder}")


def clean_value(value):
    """Convert pandas missing values into PostgreSQL NULL."""
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    return value


def dataframe_rows(dataframe, columns):
    return [
        tuple(clean_value(row[column]) for column in columns)
        for _, row in dataframe.iterrows()
    ]


airlines = pd.read_csv(latest_folder / "dim_airlines.csv")
airports = pd.read_csv(latest_folder / "dim_airports.csv")
routes = pd.read_csv(latest_folder / "dim_routes.csv")
flights = pd.read_csv(latest_folder / "fact_flights.csv")

flights["flight_date"] = pd.to_datetime(
    flights["flight_date"],
    errors="raise"
)

time_columns = [
    "scheduled_departure",
    "actual_departure",
    "scheduled_arrival",
    "actual_arrival"
]

for column in time_columns:
    flights[column] = pd.to_datetime(
        flights[column],
        errors="coerce",
        format="mixed"
    ).dt.time

flights["date_key"] = (
    flights["flight_date"].dt.strftime("%Y%m%d").astype(int)
)

dates = (
    flights[["flight_date", "date_key"]]
    .drop_duplicates()
    .sort_values("flight_date")
)

dates["full_date"] = dates["flight_date"].dt.date
dates["day"] = dates["flight_date"].dt.day
dates["month"] = dates["flight_date"].dt.month
dates["month_name"] = dates["flight_date"].dt.month_name()
dates["quarter"] = dates["flight_date"].dt.quarter
dates["year"] = dates["flight_date"].dt.year
dates["day_of_week"] = dates["flight_date"].dt.dayofweek + 1
dates["day_name"] = dates["flight_date"].dt.day_name()
dates["is_weekend"] = dates["flight_date"].dt.dayofweek >= 5

flights["flight_date"] = flights["flight_date"].dt.date

connection = None

try:
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    print("Connected to Supabase.")

    execute_values(
        cursor,
        """
        INSERT INTO analytics.dim_airlines
            (airline_code, airline_name, airline_type, country)
        VALUES %s
        ON CONFLICT (airline_code) DO UPDATE SET
            airline_name = EXCLUDED.airline_name,
            airline_type = EXCLUDED.airline_type,
            country = EXCLUDED.country;
        """,
        dataframe_rows(
            airlines,
            ["airline_code", "airline_name", "type", "country"]
        )
    )

    print(f"Loaded airlines: {len(airlines):,}")

    execute_values(
        cursor,
        """
        INSERT INTO analytics.dim_airports
            (
                airport_code,
                airport_name,
                city,
                country,
                domestic,
                latitude,
                longitude
            )
        VALUES %s
        ON CONFLICT (airport_code) DO UPDATE SET
            airport_name = EXCLUDED.airport_name,
            city = EXCLUDED.city,
            country = EXCLUDED.country,
            domestic = EXCLUDED.domestic,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude;
        """,
        dataframe_rows(
            airports,
            [
                "airport_code",
                "airport_name",
                "city",
                "country",
                "domestic",
                "lat",
                "lon"
            ]
        )
    )

    print(f"Loaded airports: {len(airports):,}")

    execute_values(
        cursor,
        """
        INSERT INTO analytics.dim_routes
            (origin, destination, domestic, distance_km)
        VALUES %s
        ON CONFLICT (origin, destination) DO UPDATE SET
            domestic = EXCLUDED.domestic,
            distance_km = EXCLUDED.distance_km;
        """,
        dataframe_rows(
            routes,
            ["origin", "destination", "domestic", "distance_km"]
        )
    )

    print(f"Loaded routes: {len(routes):,}")

    execute_values(
        cursor,
        """
        INSERT INTO analytics.dim_date
            (
                date_key,
                full_date,
                day,
                month,
                month_name,
                quarter,
                year,
                day_of_week,
                day_name,
                is_weekend
            )
        VALUES %s
        ON CONFLICT (date_key) DO NOTHING;
        """,
        dataframe_rows(
            dates,
            [
                "date_key",
                "full_date",
                "day",
                "month",
                "month_name",
                "quarter",
                "year",
                "day_of_week",
                "day_name",
                "is_weekend"
            ]
        )
    )

    print(f"Loaded dates: {len(dates):,}")

    fact_columns = [
        "flight_id",
        "flight_date",
        "date_key",
        "airline_code",
        "flight_number",
        "origin",
        "destination",
        "aircraft_type",
        "scheduled_departure",
        "actual_departure",
        "scheduled_arrival",
        "actual_arrival",
        "departure_delay_min",
        "arrival_delay_min",
        "delay_reason",
        "cancelled",
        "traveller_class",
        "seats_booked",
        "load_factor"
    ]

    execute_values(
        cursor,
        """
        INSERT INTO analytics.fact_flights
            (
                flight_id,
                flight_date,
                date_key,
                airline_code,
                flight_number,
                origin,
                destination,
                aircraft_type,
                scheduled_departure,
                actual_departure,
                scheduled_arrival,
                actual_arrival,
                departure_delay_min,
                arrival_delay_min,
                delay_reason,
                cancelled,
                traveller_class,
                seats_booked,
                load_factor
            )
        VALUES %s
        ON CONFLICT (flight_id) DO UPDATE SET
            actual_departure = EXCLUDED.actual_departure,
            actual_arrival = EXCLUDED.actual_arrival,
            departure_delay_min = EXCLUDED.departure_delay_min,
            arrival_delay_min = EXCLUDED.arrival_delay_min,
            delay_reason = EXCLUDED.delay_reason,
            cancelled = EXCLUDED.cancelled,
            seats_booked = EXCLUDED.seats_booked,
            load_factor = EXCLUDED.load_factor,
            loaded_at = NOW();
        """,
        dataframe_rows(flights, fact_columns),
        page_size=1000
    )

    print(f"Loaded flights: {len(flights):,}")

    connection.commit()
    print("\nWarehouse loading completed successfully.")

except Exception as error:
    if connection:
        connection.rollback()

    print(f"\nWarehouse loading failed: {error}")
    raise

finally:
    if connection:
        connection.close()
        print("Database connection closed.")