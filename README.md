# weather-data-pipeline

Dự án sử dụng OpenWeather API để xây dụng 1 ETL pipeline trích xuất dữ liệu, biến đổi dữ liệu bằng Apache Spark và load vào data warehouse.

## Tổng quan

Dự án này mô tả 1 vài kỹ năng chính của DE trong việc tạo 1 pipeline, cụ thể là:

1. Trích xuất dữ liệu từ OpenWeather API
2. Biến đổi dữ liệu thô sử dụng Apache Spark 
3. Load dữ liệu đã xử lý vào PostgreSQL database
4. Orchestrate toàn bộ ETL pipeline bằng Apache Airflow

## Tính năng

- Trích xuất dữ liệu từ API với thư viện Requests
- Biến đổi dữ liệu lớn bằng Apache Spark
- Lưu dữ liệu vào PostgreSQL với Spark JDBC
- ETL workflow orchestration với Apache Airflow
- Xử lý lỗi và ghi log 
- Kiểm tra từng thành phần

## Tech Stack

- Python
- Apache Spark
- PostgreSQL
- Apache Airflow
- PySpark
- Requests