-- ============================================================
-- Bangladesh Aviation Analytics
-- Analytical Data Marts
-- ============================================================


-- ============================================================
-- Airline Performance Data Mart
-- ============================================================

CREATE OR REPLACE VIEW analytics.mart_airline_performance AS
SELECT
    f.airline_code,
    a.airline_name,
    a.airline_type,
    a.country,

    COUNT(*) AS total_flights,

    COUNT(*) FILTER (
        WHERE NOT f.cancelled
    ) AS completed_flights,

    COUNT(*) FILTER (
        WHERE f.cancelled
    ) AS cancelled_flights,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE f.cancelled)
        / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate_percent,

    ROUND(
        AVG(f.departure_delay_min),
        2
    ) AS avg_departure_delay_min,

    ROUND(
        AVG(f.arrival_delay_min),
        2
    ) AS avg_arrival_delay_min,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE NOT f.cancelled
              AND COALESCE(f.arrival_delay_min, 0) <= 15
        )
        / NULLIF(
            COUNT(*) FILTER (WHERE NOT f.cancelled),
            0
        ),
        2
    ) AS on_time_arrival_percent,

    SUM(f.seats_booked) AS total_seats_booked,

    ROUND(
        AVG(f.load_factor) * 100,
        2
    ) AS avg_load_factor_percent

FROM analytics.fact_flights AS f

INNER JOIN analytics.dim_airlines AS a
    ON f.airline_code = a.airline_code

GROUP BY
    f.airline_code,
    a.airline_name,
    a.airline_type,
    a.country;


-- ============================================================
-- Route Performance Data Mart
-- ============================================================

CREATE OR REPLACE VIEW analytics.mart_route_performance AS
SELECT
    f.origin,
    origin_airport.airport_name AS origin_airport,
    origin_airport.city AS origin_city,

    f.destination,
    destination_airport.airport_name AS destination_airport,
    destination_airport.city AS destination_city,

    r.domestic,
    r.distance_km,

    COUNT(*) AS total_flights,

    COUNT(*) FILTER (
        WHERE f.cancelled
    ) AS cancelled_flights,

    ROUND(
        AVG(f.departure_delay_min),
        2
    ) AS avg_departure_delay_min,

    ROUND(
        AVG(f.arrival_delay_min),
        2
    ) AS avg_arrival_delay_min,

    ROUND(
        AVG(f.load_factor) * 100,
        2
    ) AS avg_load_factor_percent,

    SUM(f.seats_booked) AS total_seats_booked

FROM analytics.fact_flights AS f

INNER JOIN analytics.dim_routes AS r
    ON f.origin = r.origin
   AND f.destination = r.destination

INNER JOIN analytics.dim_airports AS origin_airport
    ON f.origin = origin_airport.airport_code

INNER JOIN analytics.dim_airports AS destination_airport
    ON f.destination = destination_airport.airport_code

GROUP BY
    f.origin,
    origin_airport.airport_name,
    origin_airport.city,
    f.destination,
    destination_airport.airport_name,
    destination_airport.city,
    r.domestic,
    r.distance_km;


-- ============================================================
-- Daily Operations Data Mart
-- ============================================================

CREATE OR REPLACE VIEW analytics.mart_daily_operations AS
SELECT
    d.full_date,
    d.day_name,
    d.month,
    d.month_name,
    d.quarter,
    d.year,
    d.is_weekend,

    COUNT(*) AS total_flights,

    COUNT(*) FILTER (
        WHERE NOT f.cancelled
    ) AS completed_flights,

    COUNT(*) FILTER (
        WHERE f.cancelled
    ) AS cancelled_flights,

    ROUND(
        AVG(f.departure_delay_min),
        2
    ) AS avg_departure_delay_min,

    ROUND(
        AVG(f.arrival_delay_min),
        2
    ) AS avg_arrival_delay_min,

    ROUND(
        AVG(f.load_factor) * 100,
        2
    ) AS avg_load_factor_percent,

    SUM(f.seats_booked) AS total_seats_booked

FROM analytics.fact_flights AS f

INNER JOIN analytics.dim_date AS d
    ON f.date_key = d.date_key

GROUP BY
    d.full_date,
    d.day_name,
    d.month,
    d.month_name,
    d.quarter,
    d.year,
    d.is_weekend;


-- ============================================================
-- Executive Summary Data Mart
-- ============================================================

CREATE OR REPLACE VIEW analytics.mart_executive_summary AS
SELECT
    COUNT(*) AS total_flights,

    COUNT(*) FILTER (
        WHERE NOT cancelled
    ) AS completed_flights,

    COUNT(*) FILTER (
        WHERE cancelled
    ) AS cancelled_flights,

    ROUND(
        100.0 * COUNT(*) FILTER (WHERE cancelled)
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
