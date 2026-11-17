# ==============================================================================
# Multi-Stage Enterprise Production Container for ADIDA Agent
# Stage 1: Builder (Compiler & Dependency Resolution)
# Stage 2: Runtime (Hardened, Non-Root Minimal Attack Surface)
# ==============================================================================

# ----------------- STAGE 1: BUILDER -----------------
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


# ----------------- STAGE 2: PRODUCTION RUNTIME -----------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/app:/install/lib/python3.12/site-packages"

# Install minimal runtime shared libraries (curl for healthcheck, MuPDF/freetype)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /install /install

# Create non-root system user for security compliance
RUN groupadd -g 10001 adidagroup && \
    useradd -u 10001 -g adidagroup -s /bin/bash -m adidauser

WORKDIR /app

# Copy application source code
COPY --chown=adidauser:adidagroup . /app

# Ensure writable directories for reports, logs, and sqlite storage
RUN mkdir -p /app/data/processed /app/data/evaluation /app/outputs/reports /app/outputs/charts /app/logs && \
    chown -R adidauser:adidagroup /app/data /app/outputs /app/logs

# Switch to unprivileged non-root user
USER adidauser

# Expose Streamlit (8501), FastAPI (8000), and Prometheus Metrics
EXPOSE 8501 8000

# Health check probing either the Streamlit UI or the FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || curl -f http://localhost:8501/_stcore/health || exit 1

# Default entrypoint: launch Streamlit Dashboard
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
