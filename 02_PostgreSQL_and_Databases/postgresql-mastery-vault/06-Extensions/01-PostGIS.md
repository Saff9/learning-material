---
tags: [postgresql, extensions, postgis, geospatial]
---

# PostGIS — Geospatial Extension

PostGIS turns PostgreSQL into a spatial database for geographic information systems (GIS).

## Installation

```sql
CREATE EXTENSION postgis;

-- Verify
SELECT postgis_full_version();
```

## Basic Usage

```sql
-- Create a table with geometry
CREATE TABLE pois (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    geom geometry(Point, 4326) NOT NULL  -- SRID 4326 = WGS84 (GPS coordinates)
);

-- Create a spatial index
CREATE INDEX idx_pois_geom ON pois USING GIST (geom);

-- Insert points (longitude, latitude)
INSERT INTO pois (name, geom) VALUES
    ('Eiffel Tower', ST_SetSRID(ST_MakePoint(2.2945, 48.8584), 4326)),
    ('Louvre', ST_SetSRID(ST_MakePoint(2.3376, 48.8606), 4326));
```

## Spatial Queries

```sql
-- Find points within 1 km of a location
SELECT name FROM pois
WHERE ST_DWithin(
    geom::geography,
    ST_MakePoint(2.3522, 48.8566)::geography,  -- Paris center
    1000  -- 1 km
);

-- Distance between two points
SELECT ST_Distance(
    ST_MakePoint(2.2945, 48.8584)::geography,  -- Eiffel Tower
    ST_MakePoint(2.3376, 48.8606)::geography   -- Louvre
) AS distance_meters;

-- Points within a bounding box
SELECT name FROM pois
WHERE ST_Within(geom, ST_MakeEnvelope(2.29, 48.85, 2.34, 48.87, 4326));
```

## Use Cases

- Store finder ("find coffee shops within 5km")
- Routing and navigation
- Geofencing
- Coverage analysis
- Mapping and visualization

## Next

- [[06-Extensions/02-pg_stat_statements|pg_stat_statements]]
- [[06-Extensions/04-pgvector|pgvector for AI]]
