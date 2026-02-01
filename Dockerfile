# Lightweight Dockerfile for Flask Backend (Hugging Face Spaces)
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install backend requirements first (Flask, CORS)
COPY backend/requirements.txt backend_requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt

# Install AI dependencies separately with correct sources
RUN pip install --no-cache-dir \
    numpy \
    pillow \
    opencv-python-headless

# Install PyTorch CPU-only version from official CPU index
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    --index-url https://download.pytorch.org/whl/cpu

# Copy application files
COPY backend/ backend/
COPY *.py ./
COPY yolov8n.pt ./

# Create necessary directories
RUN mkdir -p uploads outputs

# Expose Hugging Face standard port
EXPOSE 7860

# Run the Flask app on port 7860
CMD ["sh", "-c", "sed -i 's/port=5000/port=7860/' backend/app.py && python backend/app.py"]
