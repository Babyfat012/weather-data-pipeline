from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time, requests, pandas as pd
import os

LOCATIONS = [
    {"lat": 10.762622, "lon": 106.660172, "name":"Ho Chi Minh"},
    {"lat": 21.028511, "lon": 105.804817, "name":"Ha Noi"},
    {"lat": 16.047079, "lon": 108.206230, "name":"Da Nang"},
    {"lat": 16.46190000, "lon": 107.59546000, "name":"Hue"},
    {"lat": 20.84491150, "lon": 106.68808410, "name":"Hai Phong"},
    {"lat": 10.03418510, "lon": 105.72255070, "name":"Can Tho"},
    {"lat": 10.964112, "lon": 106.856461, "name":"Bien Hoa"},
    {"lat": 21.00638200, "lon": 107.29251440, "name":"Quang Ninh"},
    {"lat": 19.23424890, "lon": 104.92003650, "name":"Nghe An"},
    {"lat": 20.25061490, "lon": 105.97445360, "name":"Ninh Binh"}
]



def fetch_weather_data():
    api_key = "OiPvDJBdnu3RPHoQq9LQ7QHfnQjd1pxx"
    timesteps = "1h"
    units="metric"
    all_data = []

    for loc in LOCATIONS:
        latitude = loc["lat"]
        longitude = loc["lon"]
        name = loc["name"]
        url = (
            f"https://api.tomorrow.io/v4/weather/forecast?"
            f"location={latitude},{longitude}&timesteps={timesteps}&units={units}&apikey={api_key}"
        )
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for entry in data["timelines"]["hourly"]:
                    record = {
                        "name": name,
                        "time": entry["time"],
                        "temperature": entry["values"].get("temperature"),
                        "temperatureApparent": entry["values"].get("temperatureApparent"),
                        "dewPoint": entry["values"].get("dewPoint"),
                        "humidity": entry["values"].get("humidity"),
                        "windSpeed": entry["values"].get("windSpeed"),
                        "windDirection": entry["values"].get("windDirection"),
                        "windGust": entry["values"].get("windGust"),
                        "pressureSurfaceLevel": entry["values"].get("pressureSurfaceLevel"),
                        "cloudCover": entry["values"].get("cloudCover"),
                        "precipitationProbability": entry["values"].get("precipitationProbability"),
                        "uvIndex": entry["values"].get("uvIndex"),
                        "ezHeatStressIndex": entry["values"].get("ezHeatStressIndex")
                    }
                    all_data.append(record)
            else:
                print(f"Failed for {loc['name']}: {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error for {loc['name']}: {e}")
            
    df = pd.DataFrame(all_data)

    os.makedirs("/opt/airflow/data", exist_ok=True)
    filename = datetime.now().strftime("/opt/airflow/data/weather_%Y%m%d_%H%M%S.csv")
    df.to_csv(filename, index=False)


with DAG (
    dag_id = "fetch_weather_forecast",
    start_date = datetime(2025, 7, 18),
    schedule_interval="0 */6 * * *", # mỗi 6h
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:
    fetch_task = PythonOperator(
        task_id = "fetch_forecast",
        python_callable=fetch_weather_data
    )
