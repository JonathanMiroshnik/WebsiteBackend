FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# The app uses config.PORT (default 5000) from app/core/config.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
