CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    name TEXT,
    forecast_time TIMESTAMP,
    temperature FLOAT,
    temperature_apparent FLOAT,
    dew_point FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    wind_direction FLOAT,
    wind_gust FLOAT,
    pressure_surface_level FLOAT,
    cloud_cover FLOAT,
    precipitation_probability FLOAT,
    uv_index FLOAT,
    ez_heat_stress_index FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

