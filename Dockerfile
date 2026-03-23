FROM nvidia/cuda:12.1-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-venv \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.10 /usr/bin/python

# Copy requirements first for better caching
COPY requirements.txt .
# Install PyTorch with CUDA support
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY run.py .

# Copy model inference source code (from HydroPredict-model)
COPY model_src/ ./model_src/

# Copy model checkpoints and configs
COPY checkpoints/ ./checkpoints/
COPY configs/ ./configs/
COPY data/ ./data/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/model_src
ENV MODEL_CHECKPOINT_PATH=checkpoints/final_model.ckpt
ENV MODEL_CONFIG_PATH=configs/model_config.json
ENV HISTORICAL_DATA_PATH=data/input/hourly-data-2024-2025.csv
ENV WEATHERBIT_CONFIG_PATH=configs/weatherbit.json

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "run.py"]

