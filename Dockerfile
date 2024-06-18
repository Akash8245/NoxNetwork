# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Command to run migrations, migrate database, and start server
CMD ["sh", "-c", ". /app/.env && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
