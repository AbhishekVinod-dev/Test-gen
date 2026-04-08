FROM python:3.11-slim

WORKDIR /app

LABEL maintainer="TestGen Team"
LABEL description="TestGen - Mutation Testing Challenge"
LABEL version="1.0.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py env.py grader.py mutations.py inference.py ./
COPY models.py ./
COPY index.html landing.html game.html ./
COPY server/ ./server/
COPY fixtures/ ./fixtures/

# Create non-root user
RUN useradd -m -u 1000 testgen && chown -R testgen:testgen /app
USER testgen

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
