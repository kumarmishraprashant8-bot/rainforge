# RainForge ML Service Dockerfile
# ================================
# Separate container for ML inference

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-ml.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-ml.txt

# Copy ML code
COPY app/ml/ ./app/ml/
COPY app/__init__.py ./app/

# Create empty __init__.py if needed
RUN touch app/__init__.py app/ml/__init__.py

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the ML service
CMD ["uvicorn", "app.ml.ml_api:app", "--host", "0.0.0.0", "--port", "8001"]
