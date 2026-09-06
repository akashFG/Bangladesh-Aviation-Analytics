from pathlib import Path
import pandas as pd

RAW_ROOT = Path("pipeline_data/raw")
PROCESSED_ROOT = Path("pipeline_data/processed")

date_folders = sorted(
    [folder for folder in RAW_ROOT.iterdir() if folder.is_dir()],
    reverse=True
)

if not date_folders:
    raise FileNotFoundError("No raw-data folder found.")

latest_raw_folder = date_folders[0]
run_date = latest_raw_folder.name
processed_folder = PROCESSED_ROOT / run_date
processed_folder.mkdir(parents=True, exist_ok=True)

print(f"Processing data from: {latest_raw_folder}")

flights = pd.read_csv(latest_raw_folder / "bd_flights_2024.csv")
airlines = pd.read_csv(latest_raw_folder / "dim_airlines.csv")
airports = pd.read_csv(latest_raw_folder / "dim_airports.csv")
routes = pd.read_csv(latest_raw_folder / "dim_routes.csv")

# Remove exact duplicate rows
before = len(flights)
flights = flights.drop_duplicates()
removed_duplicates = before - len(flights)

# Convert data types
flights["flight_date"] = pd.to_datetime(
    flights["flight_date"],
    errors="coerce"
)

boolean_columns = ["domestic", "cancelled"]

for column in boolean_columns:
    flights[column] = flights[column].astype("boolean")

numeric_columns = [
    "distance_km",
    "departure_delay_min",
    "arrival_delay_min",
    "seats_booked",
    "load_factor",
]

for column in numeric_columns:
    flights[column] = pd.to_numeric(
        flights[column],
        errors="coerce"
    )

# Clean text columns
text_columns = [
    "airline_code",
    "airline_name",
    "flight_number",
    "origin",
    "destination",
    "aircraft_type",
    "traveller_class",
    "delay_reason",
]

for column in text_columns:
    flights[column] = flights[column].astype("string").str.strip()

# Data-quality checks
errors = []

if flights["flight_id"].isna().any():
    errors.append("flight_id contains null values")

if flights["flight_id"].duplicated().any():
    errors.append("flight_id contains duplicate values")

if flights["flight_date"].isna().any():
    errors.append("flight_date contains invalid or missing values")

if (flights["distance_km"] <= 0).any():
    errors.append("distance_km contains zero or negative values")

if (flights["seats_booked"] < 0).any():
    errors.append("seats_booked contains negative values")

if ((flights["load_factor"] < 0) | (flights["load_factor"] > 1)).any():
    errors.append("load_factor must be between 0 and 1")

valid_airlines = set(airlines["airline_code"])
invalid_airlines = flights.loc[
    ~flights["airline_code"].isin(valid_airlines),
    "airline_code"
].unique()

if len(invalid_airlines) > 0:
    errors.append(f"Invalid airline codes: {invalid_airlines.tolist()}")

valid_airports = set(airports["airport_code"])

invalid_origins = flights.loc[
    ~flights["origin"].isin(valid_airports),
    "origin"
].unique()

invalid_destinations = flights.loc[
    ~flights["destination"].isin(valid_airports),
    "destination"
].unique()

if len(invalid_origins) > 0:
    errors.append(f"Invalid origin airports: {invalid_origins.tolist()}")

if len(invalid_destinations) > 0:
    errors.append(
        f"Invalid destination airports: "
        f"{invalid_destinations.tolist()}"
    )

# Save transformed data
flights.to_csv(
    processed_folder / "fact_flights.csv",
    index=False
)

airlines.drop_duplicates().to_csv(
    processed_folder / "dim_airlines.csv",
    index=False
)

airports.drop_duplicates().to_csv(
    processed_folder / "dim_airports.csv",
    index=False
)

routes.drop_duplicates().to_csv(
    processed_folder / "dim_routes.csv",
    index=False
)

print(f"Removed exact duplicates: {removed_duplicates}")
print(f"Final flight rows: {len(flights):,}")
print(f"Processed files saved to: {processed_folder}")

if errors:
    print("\nDATA QUALITY CHECK FAILED:")

    for error in errors:
        print(f"- {error}")
else:
    print("\nAll critical data-quality checks passed.")