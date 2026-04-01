# Fast Docker build for development
FROM python:3.12-slim

WORKDIR /app

# Minimal setup
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements-hf.txt .
RUN pip install --no-cache-dir -r requirements-hf.txt

# Copy application
COPY . .

EXPOSE 7860

CMD ["python", "app_hf.py"]
