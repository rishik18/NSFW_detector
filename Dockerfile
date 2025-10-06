FROM python:3.11-slim

# ---- System dependencies for OpenCV ----

RUN apt-get update && apt-get install -y --no-install-recommends \
	libgl1 libglib2.0-0 curl \
	&& rm -rf /var/lib/apt/lists/*

# --- App setup ---

WORKDIR /app 
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# NudeNet downloads
ENV NUDENET_HOME=/models
RUN mkdir -p /models

# Pre-download weights
RUN python - <<'PY'
from nudenet import NudeDetector
NudeDetector()
print("NudeNet model preloadedd")
PY

# Copy application code
COPY . .

# Non-root user for safety
RUN useradd -m appuser
USER appuser

# Expose port for server to listen on
EXPOSE 8080

# Gunicorn 
CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:8080", "app:app"]