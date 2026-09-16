FROM python:3-alpine

# Build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION="1.2.6-mod"

# Labels following OCI Image Format Specification
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.authors="Murr (https://github.com/vtstv), rangermix" \
      org.opencontainers.image.url="https://github.com/vtstv/TwitchDropsMiner" \
      org.opencontainers.image.documentation="https://github.com/vtstv/TwitchDropsMiner/blob/main/README.md" \
      org.opencontainers.image.source="https://github.com/vtstv/TwitchDropsMiner" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="Murr" \
      org.opencontainers.image.title="Twitch Drops Miner (Mod by Murr)" \
      org.opencontainers.image.description="Automated Twitch drops miner with web dashboard auth and mining start/stop controls"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=:: \
    PORT=8080

# Set working directory
WORKDIR /app

# Copy project metadata and install dependencies
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir .

# Copy application code
COPY main.py ./
COPY src/ ./src/
COPY lang/ ./lang/
COPY icons/ ./icons/
COPY web/ ./web/

# Create data directory for persistent storage
RUN mkdir -p /app/data && chmod 777 /app/data
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Expose web port
EXPOSE 8080

# Health check (uses /health which does not require basic auth)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# Run the application
CMD ["python", "main.py"]
