# Extract only noVNC's browser library, without installing its websockify server.
FROM alpine:latest AS novnc-assets
RUN apk add --no-cache novnc

FROM python:alpine

# Build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION="2.2.0-mod"

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

# Copy noVNC browser library
COPY --from=novnc-assets /usr/share/novnc/ /usr/share/novnc/

# Copy application files and metadata
COPY pyproject.toml main.py ./
COPY src/ ./src/
COPY lang/ ./lang/
COPY icons/ ./icons/
COPY web/ ./web/

# Login and renewal use private browsers; only the dashboard port is exposed.
RUN apk upgrade --no-cache && \
    apk add --no-cache chromium xvfb openbox x11vnc xdotool tzdata && \
    addgroup -g 10001 -S tdm-browser && \
    adduser -u 10001 -S -D -H -h /nonexistent -s /sbin/nologin -G tdm-browser tdm-browser && \
    pip install --no-cache-dir . && \
    pip uninstall --yes pip && \
    mkdir -p /app/data /app/logs && \
    chmod 700 /app/data /app/logs

# Expose web port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://[::1]:8080/healthz')" || exit 1

# Run the application
CMD ["python", "main.py"]
