# Sử dụng Python 3.10 làm base image
FROM python:3.10-slim

WORKDIR /slm_api

# Cài đặt các dependencies hệ thống
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 8080

# Chạy lệnh tạo bảng trước khi khởi động API
CMD ["sh", "-c", "python app/model/model.py && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
