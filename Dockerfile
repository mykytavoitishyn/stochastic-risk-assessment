# ── Stage: runtime ────────────────────────────────────────────────────────────
# We use a slim Python image — "slim" means no build tools, docs, or test suites.
# This cuts the base image from ~1GB to ~150MB.
FROM python:3.12-slim

# Set working directory inside the container.
# All subsequent paths are relative to this.
WORKDIR /app

# Copy ONLY the requirements file first.
# Docker caches each layer. If requirements.api.txt hasn't changed,
# the next RUN (pip install) is served from cache — fast rebuilds.
COPY requirements.api.txt .

# Install dependencies.
# --no-cache-dir: don't store pip's download cache (saves ~50MB in the image).
# --upgrade pip: avoids pip version warnings.
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.api.txt

# Now copy the application code.
# This layer changes often (every code edit), but pip install above is cached.
COPY src/       src/
COPY api/       api/
COPY backtesting/ backtesting/

# data/ and results/ are NOT copied — they are mounted as volumes at runtime.
# This keeps the image small and lets you update data without rebuilding.

# The container will listen on port 8000.
# EXPOSE is documentation — it doesn't actually publish the port.
# The actual publishing happens in docker-compose.yml.
EXPOSE 8000

# Default command to start the API.
# "0.0.0.0" makes it listen on all interfaces inside the container
# (not just localhost), so docker-compose can reach it.
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
