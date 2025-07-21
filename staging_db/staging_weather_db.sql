CREATE TABLE IF NOT EXISTS staging_weather_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name NVARCHAR(100),
    forecast_time DATETIME,
    temperature FLOAT NULL,
    temperatureApparent FLOAT NULL,
    dewPoint FLOAT NULL,
    humidity FLOAT NULL,
    windSpeed FLOAT NULL,
    windDirection FLOAT NULL,
    windGust FLOAT NULL,
    pressureSurfaceLevel FLOAT NULL,
    cloudCover FLOAT NULL,
    precipitationProbability FLOAT NULL,
    uvIndex FLOAT NULL,
    ezHeatStressIndex FLOAT NULL,
    fetch_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name,forecast_time) -- Ngăn duplicate nếu gọi lại API 
)