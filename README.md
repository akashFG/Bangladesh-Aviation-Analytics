# Bangladesh Aviation Data Engineering & Analytics Pipeline

An end-to-end aviation analytics project that extracts, validates, transforms, and loads flight data into a PostgreSQL dimensional warehouse and presents operational insights through an executive Tableau dashboard.

![Bangladesh Aviation Analytics Dashboard](Bangladesh_Aviation_Analytics.png)

## Project Overview

This project demonstrates a complete data-engineering and analytics workflow using Bangladesh flight operations data from 2024.

The pipeline processes more than 27,000 flight records and produces business insights related to:

- Flight volume
- Completed and cancelled flights
- Airline performance
- Route performance
- Departure and arrival delays
- On-time arrival performance
- Passenger load factor
- Daily operational trends

## Key Results

| Metric | Result |
|---|---:|
| Raw flight records | 27,322 |
| Exact duplicates removed | 55 |
| Final warehouse flight records | 27,267 |
| Completed flights | 26,673 |
| Cancelled flights | 594 |
| Average load factor | 61.3% |
| Airlines | 10 |
| Airports | 15 |
| Routes | 30 |
| Date records | 366 |

## Architecture

```mermaid
flowchart LR
    A[CSV Sources] --> B[Python Extraction]
    B --> C[Raw Data Layer]
    C --> D[Transformation and Validation]
    D --> E[Processed Data Layer]
    E --> F[PostgreSQL Warehouse]
    F --> G[Analytical Data Marts]
    G --> H[Tableau Dashboard]
```

## Technology Stack

- Python
- Pandas
- SQL
- PostgreSQL
- Supabase
- Psycopg2
- Tableau
- GitHub

## Data Warehouse Model

The dimensional warehouse contains the following tables:

### Fact table

- `analytics.fact_flights`

### Dimension tables

- `analytics.dim_airlines`
- `analytics.dim_airports`
- `analytics.dim_routes`
- `analytics.dim_date`

### Analytical data marts

- `analytics.mart_airline_performance`
- `analytics.mart_route_performance`
- `analytics.mart_daily_operations`
- `analytics.mart_executive_summary`

## Pipeline Components

### `extract_and_test_connection.py`

- Tests the PostgreSQL/Supabase connection
- Creates a date-partitioned raw-data directory
- Stages source CSV files in the raw layer
- Produces pipeline execution logs

### `inspect_raw_data.py`

- Displays row and column counts
- Identifies duplicate records
- Reports missing values
- Displays data types and sample records

### `transform_data.py`

- Removes exact duplicates
- Converts fields into appropriate data types
- Cleans text values
- Validates airline and airport reference codes
- Checks flight IDs, dates, distances, seats, and load factors
- Writes validated records to the processed layer

### `load_warehouse.py`

- Connects securely using an environment variable
- Loads dimension tables before the fact table
- Generates the date dimension
- Performs conflict-aware upserts
- Uses transactions and rollback for safe loading

### `export_tableau_data.py`

- Queries analytical data marts
- Exports dashboard-ready CSV datasets
- Produces airline, route, daily operations, and executive KPI extracts

## Data-Quality Controls

The transformation pipeline checks:

- Duplicate flight records
- Null flight IDs
- Duplicate flight IDs
- Invalid flight dates
- Invalid airline codes
- Invalid origin and destination airport codes
- Zero or negative route distances
- Negative seat counts
- Load factors outside the range of 0 to 1

Missing actual departure, actual arrival, and delay values are retained where they represent valid cancelled or non-delayed flight scenarios.

## Dashboard

The Tableau dashboard includes:

- Executive KPI summary
- Daily flight volume trend
- Daily cancellation trend
- Airline performance by flight volume
- Top routes by flight volume
- Cancellation-rate comparison
- Average arrival-delay comparison
- Passenger load-factor analysis

The packaged Tableau workbook can be opened with Tableau Public or Tableau Desktop.

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── create_warehouse.sql
├── create_data_marts.sql
├── extract_and_test_connection.py
├── inspect_raw_data.py
├── transform_data.py
├── load_warehouse.py
├── export_tableau_data.py
├── bd_flights_2024.csv
├── dim_airlines.csv
├── dim_airports.csv
├── dim_routes.csv
├── Bangladesh_Aviation_Analytics.png
└── Bangladesh_Aviation_Analytics.twbx
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/bangladesh-aviation-analytics.git
cd bangladesh-aviation-analytics
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`:

```env
SUPABASE_DB_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE?sslmode=require
```

Never commit the `.env` file or database credentials.

### 5. Create the warehouse

Run the SQL files in the following order:

```text
1. create_warehouse.sql
2. create_data_marts.sql
```

The data marts should be created after warehouse data has been loaded.

### 6. Run the pipeline

```bash
python extract_and_test_connection.py
python inspect_raw_data.py
python transform_data.py
python load_warehouse.py
python export_tableau_data.py
```

## Security

Database credentials are loaded from the `SUPABASE_DB_URL` environment variable. Actual credentials and generated pipeline data are excluded through `.gitignore`.

## Future Improvements

- Apache Airflow orchestration
- PySpark-based transformations
- AWS S3 raw-data storage
- AWS RDS or managed PostgreSQL deployment
- Terraform infrastructure provisioning
- Automated tests
- CI/CD pipeline
- Data-quality monitoring and SLA alerts
- Incremental loading
- Tableau extract refresh automation

## Author

Developed as a portfolio project demonstrating practical skills in data engineering, dimensional modelling, SQL analytics, data quality, and business intelligence.
