FROM python:3.10-slim

# Install system dependencies
# Use libgl1 instead of libgl1-mesa-glx for Debian Trixie compatibility
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway sets $PORT dynamically)
EXPOSE 8000

# Run the application using shell form to expand $PORT variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
