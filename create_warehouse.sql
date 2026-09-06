-- ============================================================
-- Bangladesh Aviation Analytics
-- Dimensional Data Warehouse Schema
-- ============================================================

CREATE SCHEMA IF NOT EXISTS analytics;


-- ============================================================
-- Airline Dimension
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_airlines (
    airline_code VARCHAR(10) PRIMARY KEY,
    airline_name VARCHAR(150) NOT NULL,
    airline_type VARCHAR(50),
    country VARCHAR(100)
);


-- ============================================================
-- Airport Dimension
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_airports (
    airport_code VARCHAR(10) PRIMARY KEY,
    airport_name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    domestic BOOLEAN,
    latitude NUMERIC(10, 6),
    longitude NUMERIC(10, 6)
);


-- ============================================================
-- Route Dimension
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_routes (
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    domestic BOOLEAN,
    distance_km NUMERIC(10, 2),

    PRIMARY KEY (origin, destination),

    CONSTRAINT fk_route_origin
        FOREIGN KEY (origin)
        REFERENCES analytics.dim_airports(airport_code),

    CONSTRAINT fk_route_destination
        FOREIGN KEY (destination)
        REFERENCES analytics.dim_airports(airport_code),

    CONSTRAINT different_route_airports
        CHECK (origin <> destination)
);


-- ============================================================
-- Date Dimension
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);


-- ============================================================
-- Flight Fact Table
-- ============================================================

CREATE TABLE IF NOT EXISTS analytics.fact_flights (
    flight_id BIGINT PRIMARY KEY,
    flight_date DATE NOT NULL,
    date_key INTEGER NOT NULL,
    airline_code VARCHAR(10) NOT NULL,
    flight_number VARCHAR(20) NOT NULL,
    origin VARCHAR(10) NOT NULL,
    destination VARCHAR(10) NOT NULL,
    aircraft_type VARCHAR(100),

    scheduled_departure TIME,
    actual_departure TIME,
    scheduled_arrival TIME,
    actual_arrival TIME,

    departure_delay_min NUMERIC(10, 2),
    arrival_delay_min NUMERIC(10, 2),
    delay_reason VARCHAR(200),

    cancelled BOOLEAN NOT NULL DEFAULT FALSE,
    traveller_class VARCHAR(50),
    seats_booked INTEGER,
    load_factor NUMERIC(6, 4),

    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_flight_date
        FOREIGN KEY (date_key)
        REFERENCES analytics.dim_date(date_key),

    CONSTRAINT fk_flight_airline
        FOREIGN KEY (airline_code)
        REFERENCES analytics.dim_airlines(airline_code),

    CONSTRAINT fk_flight_origin
        FOREIGN KEY (origin)
        REFERENCES analytics.dim_airports(airport_code),

    CONSTRAINT fk_flight_destination
        FOREIGN KEY (destination)
        REFERENCES analytics.dim_airports(airport_code),

    CONSTRAINT fk_flight_route
        FOREIGN KEY (origin, destination)
        REFERENCES analytics.dim_routes(origin, destination),

    CONSTRAINT valid_load_factor
        CHECK (load_factor BETWEEN 0 AND 1),

    CONSTRAINT valid_seats_booked
        CHECK (seats_booked >= 0)
);


-- ============================================================
-- Analytical Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_flights_date
    ON analytics.fact_flights(flight_date);

CREATE INDEX IF NOT EXISTS idx_fact_flights_airline
    ON analytics.fact_flights(airline_code);

CREATE INDEX IF NOT EXISTS idx_fact_flights_route
    ON analytics.fact_flights(origin, destination);

CREATE INDEX IF NOT EXISTS idx_fact_flights_cancelled
    ON analytics.fact_flights(cancelled);
