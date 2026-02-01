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

# Copy requirements files
COPY requirements.txt ./
RUN pip install --no-cache-dir \
    numpy \
    pillow \
    opencv-python-headless

# Install PyTorch CPU-only version
RUN pip install --no-cache-dir \
    torch \
    torchvision \
    --index-url https://download.pytorch.org/whl/cpu

# Copy ALL Python files to root (so imports work)
COPY *.py ./
COPY yolov8n.pt ./

# Copy backend folder
COPY backend/ ./backend/

# Install backend requirements (Flask, CORS)
RUN pip install --no-cache-dir -r backend/requirements.txt

# Create necessary directories
RUN mkdir -p uploads outputs

# Expose Hugging Face standard port
EXPOSE 7860

# Run the Flask app on port 7860 (change port in the command)
CMD ["python", "-c", "import sys; sys.path.insert(0, '.'); exec(open('backend/app.py').read().replace('port=5000', 'port=7860'))"]
