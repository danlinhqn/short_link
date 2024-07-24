# Sử dụng image Python chính thức làm base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép tệp requirements.txt và cài đặt các phụ thuộc
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn ứng dụng vào container
COPY . .

# Mở cổng 8080 cho ứng dụng Flask
EXPOSE 5000

# Thiết lập biến môi trường FLASK_APP để chạy ứng dụng Flask
ENV FLASK_APP=app.py

# Chạy ứng dụng Flask
CMD ["flask", "run", "--host=0.0.0.0"]
