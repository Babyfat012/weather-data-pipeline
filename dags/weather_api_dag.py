from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time, requests, panda as pd

LOCATIONS = [
    {lat: 10.762622, lon: 106.660172, name:"Ho_Chi_Minh"},
]

def fetch_weather_data():
    all_data = []
