from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time, requests, pandas as pd
import os
import mysql.connector
import logging
import numpy as np
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

def create_staging_table():
    with open('/opt/airflow/staging_db/staging_weather_db.sql', 'r') as f:
        create_sql = f.read()

    conn = mysql.connector.connect(
        host="mysql",
        user="admin",
        password="admin",
        database="staging_db"
    )
    cursor = conn.cursor() # thứ gì đó có thể thực thi các lệnh SQL

    try:
        cursor.execute(create_sql) # thực thi lệnh SQL đọc từ file
        conn.commit() # đảm bảo thay đổi được ghi nhận
        logging.info("Bảng staging đã được tạo hoặc đã tồn tại!")
    except Exception as e:
        logging.error(f"Lỗi khi tạo bảng {e}")

    cursor.close()
    conn.close()

def fetch_weather_data():
    api_key = "OiPvDJBdnu3RPHoQq9LQ7QHfnQjd1pxx"
    timesteps = "1h"
    units="metric"
    all_data = []

    logging.info("Bắt đầu gọi API thời tiết...")
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
                data = response.json() # trả về toàn bộ
                for entry in data["timelines"]["hourly"]:
                    record = {
                        "name": name,
                        "forecast_time": entry["time"],
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
            elif response.status_code == 429:
                logging.warning(f"Rate limit cho {name}. Bỏ qua")
                continue
            else:
                logging.error(f" Lỗi {response.status_code} khi gọi API cho {name}: {response.text}")
            time.sleep(0.5) # đợi 0.5s mỗi lần fetch
        except Exception as e:
            logging.warning(f"Exception cho {name}: {e}")

    if not all_data:
        raise ValueError(" Không có dữ liệu nào được lấy từ API. Dừng pipeline để tránh lỗi tiếp theo.")        
            
    # Insert vào MySQL
    df = pd.DataFrame(all_data)
    logging.info(f"Các cột có giá trị None: {df.isnull().sum()}")

    for col in df.columns:
        if df[col].astype(str).str.contains("nan", case=False).any():
            logging.warning(f"Cột {col} vẫn chứa chuỗi 'nan'!")
            
    df = df.replace("nan", None)         # chuỗi
    df = df.replace({np.nan: None})      # NaN kiểu số

    conn = mysql.connector.connect(
        host="mysql",
        user="admin",
        password="admin",
        database="staging_db"
    )
    cursor = conn.cursor()
    logging.info(df.dtypes)
    query = """ 
        INSERT IGNORE INTO staging_weather_data (
            name, forecast_time, temperature, temperatureApparent, dewPoint,
            humidity, windSpeed, windDirection, windGust, pressureSurfaceLevel,
            cloudCover, precipitationProbability, uvIndex, ezHeatStressIndex
        ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        for _, row in df.iterrows():
            values = (
                row["name"], row["forecast_time"], row["temperature"], row["temperatureApparent"], row["dewPoint"],
                row["humidity"], row["windSpeed"], row["windDirection"], row["windGust"], 
                row["pressureSurfaceLevel"], row["cloudCover"], row["precipitationProbability"], row["uvIndex"], 
                row["ezHeatStressIndex"]
            )
            cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        logging.error(f"Lỗi khi ghi dữ liệu vào DB {e}")
    finally:
        cursor.close()
        conn.close()
    logging.info(f"Đã insert {len(df)} dòng dữ liệu thời tiết")
# tạo 1 DAG có nhiệm vụ gọi hàm fetch_weather_data 
with DAG (
    dag_id = "fetch_weather_foreacst_dag",
    start_date = datetime(2025, 7, 18),
    schedule_interval="0 */6 * * *", # mỗi 6h
    catchup=False, # DAG chỉ chạy từ hiện tại trở đi
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)}, # task vẫn bút, 
) as dag:
    
    create_table_task = PythonOperator(
        task_id = "create_staging_table",
        python_callable=create_staging_table
    )

    fetch_task = PythonOperator(
        task_id = "fetch_forecast",
        python_callable=fetch_weather_data
    )
    create_table_task >> fetch_task   # thiết lập thứ tự tasks

