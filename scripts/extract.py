import json
import requests
import pandas as pd 
from datetime import datetime
# import matplotlib.pyplot as plt
# import seaborn as sns

api_key = "OiPvDJBdnu3RPHoQq9LQ7QHfnQjd1pxx"

latitude = 10.7758439
longitude = 106.7017555
cnt = 5

url = f"https://api.tomorrow.io/v4/weather/forecast?location={latitude},{longitude}&apikey={api_key}"
response = requests.get(url)

data = response.json()
json_str = json.dumps(data, indent=4)
print(json_str)