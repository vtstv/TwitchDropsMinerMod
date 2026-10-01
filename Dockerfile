FROM python:3-alpine

# Build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION="2.1.0-mod"

# Labels following OCI Image Format Specification
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.authors="Murr (https://github.com/vtstv), rangermix" \
      org.opencontainers.image.url="https://github.com/vtstv/TwitchDropsMinerMod" \
      org.opencontainers.image.documentation="https://github.com/vtstv/TwitchDropsMinerMod/blob/main/README.md" \
      org.opencontainers.image.source="https://github.com/vtstv/TwitchDropsMinerMod" \
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

# Copy application files and metadata in a single layer
COPY pyproject.toml main.py ./
COPY src/ ./src/
COPY lang/ ./lang/
COPY icons/ ./icons/
COPY web/ ./web/

# Login and renewal use private browsers; only the dashboard port is exposed.
# Install dependencies, setup tdm-browser user, and prepare runtime directories in a single layer
# to minimize layer count and disk footprint for environments using the vfs storage driver.
RUN apk add --no-cache chromium xvfb openbox x11vnc xdotool novnc tzdata && \
    addgroup -g 10001 -S tdm-browser && \
    adduser -u 10001 -S -D -H -h /nonexistent -s /sbin/nologin -G tdm-browser tdm-browser && \
    pip install --no-cache-dir . && \
    mkdir -p /app/data /app/logs && \
    chmod 700 /app/data /app/logs

# Expose web port
EXPOSE 8080

# Health check (uses /health which does not require basic auth)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# Run the application
CMD ["python", "main.py"]
