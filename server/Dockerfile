# Use the official Python image as the base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /server

# Copy dependency files first to leverage Docker caching
COPY requirements.txt /server/

# Install dependencies before copying the entire application (to improve build efficiency)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /server/

# Expose the FastAPI port
EXPOSE 8000

# ✅ Ensure hot reload works with file changes inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/server"]