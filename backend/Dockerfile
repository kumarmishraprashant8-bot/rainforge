# RainForge Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# libgl1-mesa-glx and libglib2.0-0 needed for opencv or similar image libs if used later
# but for now basic is fine
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads/pdfs
RUN mkdir -p uploads generated_pdfs

# Command to run the demo app
CMD ["uvicorn", "app.main_demo:app", "--host", "0.0.0.0", "--port", "8000"]
