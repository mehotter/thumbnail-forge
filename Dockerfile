# Use an official Python runtime with PyTorch support
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (needed for OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
COPY backend/requirements.txt backend_requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r backend_requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -front uploads outputs

# Expose port (Hugging Face Spaces uses 7860 by default for some SDKs, but we can configure it.
# We'll use 5000 as configured in app.py, but usually HF expects us to listen on port 7860.
# We will modify the command to run on 7860 or change app.py via env var.
# For simplicity, let's try to pass PORT env var.

# Expose the port
EXPOSE 7860

# Run the application
# We use 'python backend/app.py' but we need to ensure it listens on 0.0.0.0 and port 7860 (standard for unmodified HF Spaces)
# We will override the port in the CMD or ensure app.py respects PORT env var.
# app.py has `app.run(..., port=5000)`. We can use gunicorn or just python.
# Let's use a wrapper command to sed the port or just assume we can map 5000->7860?
# Actually HF Spaces Docker SDK allows 5000 if we expose it? No, standard is 7860.
# Safest: Use Gunicorn or modify app behavior.
# Let's use a CMD that patches app.py or relies on an ENV var check if I add it.
# I will NOT edit app.py yet to avoid breaking local dev. I will use `sed` to change port in Docker.
CMD ["sh", "-c", "sed -i 's/port=5000/port=7860/' backend/app.py && python backend/app.py"]
