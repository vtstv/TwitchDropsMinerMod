# Twitch Drops Miner (Mod by Murr)

> A high-performance, automated Twitch drops miner with **Start/Pause mining controls**, **dual-stack IPv4 & IPv6 Docker networking**, **web dashboard authentication**, and **headless remote deployment support**.

<p align="center">
  <a href="https://github.com/vtstv"><img src="https://img.shields.io/badge/Mod%20by-Murr-blueviolet?style=for-the-badge&logo=github" alt="Mod by Murr"></a>
  <a href="https://hub.docker.com/r/vtstv/twitch-drops-miner"><img src="https://img.shields.io/docker/pulls/vtstv/twitch-drops-miner?style=for-the-badge&color=blue" alt="Docker Pulls"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python 3.12 or newer"></a>
  <a href="https://github.com/rangermix/TwitchDropsMiner"><img src="https://img.shields.io/badge/Upstream-rangermix%2FTwitchDropsMiner-green?style=for-the-badge" alt="Upstream"></a>
</p>

---

## 🌟 Mod Enhancements & Key Features

This fork extends the upstream [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner) with features designed for server hosting, VPS environments, containerization, and granular mining control.

### 1. ⏸ Interactive Mining Controls (Start / Pause)
Upstream operates in an always-on loop whenever eligible campaigns exist. This mod introduces complete control over the mining process without having to stop the web dashboard or container:
- **Header Toggle Button**: One-click **Pause Mining** (red/amber) and **Start Mining** (glowing green) directly from the web navigation bar.
- **Visual Status Badges**: Real-time status indicator (`⛏ MINING ACTIVE` vs. `⏸ MINING PAUSED`) in the status bar.
- **Resource-Efficient Idle Mode**: When paused, channel stream watching and spade watch payload transmissions immediately cease while keeping the WebSocket connections, campaign listeners, and dashboard responsive.
- **REST & WebSocket API**: Full programmatic control via `/api/mining/*` endpoints and live `mining_state` WebSocket broadcasts.

### 2. 🌐 Dual-Stack IPv4 & IPv6 Docker Networking
Engineered for modern hosting providers, cloud VPS, and dual-stack / IPv6-only environments:
- **Dynamic Interface Binding**: The web server binds via the `HOST` environment variable, defaulting to `::` on Linux/Alpine containers (enabling dual-stack IPv6 & IPv4 listening) and `0.0.0.0` on Windows.
- **Host Network Mode Support**: Supports running with `--net=host` on Linux servers, eliminating Docker IPv6 NAT and port-forwarding issues.
- **NAT64 / DNS64 Compatibility**: Works seamlessly on IPv6-only cloud instances accessing Twitch IPv4 endpoints via NAT64 gateways.
- **Local Bridge Support**: Preconfigured for local development on Windows via Docker Desktop using port mapping `28088:8080`.

### 3. 🔐 Dashboard Web Authentication
- **Secure Web Panel Password**: Integrated dashboard password protection using scrypt password hashing, session tokens (`tdm_auth`), rate limiting (5 attempts/min per IP), and CSRF protection (`X-TDM-Request: 1`).
- **Clean Single-Auth Architecture**: Removed conflicting HTTP Basic Auth popups to prevent browser re-authentication loops.
- **Public Health Endpoints**: `/health` and `/healthz` endpoints remain accessible for Docker container health checks and reverse proxy monitoring without triggering authentication prompts.

### 4. 🔑 Headless Twitch OAuth Device Activation
- Displays the Twitch activation URL (`https://www.twitch.tv/activate`) and user code (e.g. `ABCD-EFGH`) directly in standard output (`stdout`) and the console log buffer.
- Perfect for remote servers and headless VPS deployments: authenticate your Twitch account directly from an SSH terminal or `docker logs` without needing to immediately load the web interface.

### 5. ⚡ Windows 1-Click Management Scripts
- **`start.bat`**: Verifies Docker Desktop is running, starts the container in the background (`docker compose up -d`), and outputs the local dashboard URL (`http://localhost:28088`).
- **`stop.bat`**: Gracefully stops the container with `docker compose down`.

### 6. 🎨 Streamlined UI & Attribution
- Clean, uncluttered UI footer with single credit attribution: `Mod by Murr`.
- Responsive badges and controls with smooth transition animations.

---

## 🚀 Quick Start

### Option A: Local Docker (Windows / macOS / Linux)

1. Clone this repository:
   ```bash
   git clone -b mod https://github.com/vtstv/TwitchDropsMinerMod.git
   cd TwitchDropsMinerMod
   ```
2. **On Windows**: Simply double-click `start.bat` (or run it from CMD/PowerShell).
3. **On Linux / macOS**: Run Docker Compose:
   ```bash
   docker compose up -d
   ```
4. Open the web interface at **<http://localhost:28088>**.
5. Log in to your Twitch account using the OAuth device code displayed on the screen or in `docker compose logs`.

To stop the miner:
- **Windows**: Double-click `stop.bat`.
- **Linux / macOS**: Run `docker compose down`.

---

### Option B: Remote Linux VPS Deployment

For a remote server (e.g. Ubuntu, Debian, Alpine VPS with IPv4/IPv6):

```bash
docker run -d \
  --name twitch-drops-miner \
  --network host \
  --restart unless-stopped \
  -e HOST=:: \
  -e PORT=8080 \
  -v /opt/twitch-drops-miner/data:/app/data \
  -v /opt/twitch-drops-miner/logs:/app/logs \
  vtstv/twitch-drops-miner:latest
```

> **Note**: Using `--network host` allows the container to bind directly to `[::]:8080`, accepting incoming traffic on both public IPv4 and IPv6 addresses. Ensure port `8080` is allowed in your firewall (`ufw allow 8080/tcp`).

View container logs to retrieve the Twitch OAuth code:
```bash
docker logs -f twitch-drops-miner
```

---

### Option C: Run from Source

Requires **Python 3.12+**:

```bash
# Clone the repository
git clone -b mod https://github.com/vtstv/TwitchDropsMinerMod.git
cd TwitchDropsMinerMod

# Install dependencies
pip install -e .

# Run the application
python main.py
```

Then navigate to **<http://localhost:8080>**.

---

## 📡 API Reference

In addition to standard TwitchDropsMiner endpoints, this mod adds endpoints for external monitoring, home automation (Home Assistant, scripts), and integration:

| Method | Endpoint | Description | Public / Auth |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/mining/status` | Returns `{"mining_enabled": true/false}` | Protected |
| `POST` | `/api/mining/toggle` | Toggles mining between active and paused | Protected |
| `POST` | `/api/mining/start` | Resumes mining activity | Protected |
| `POST` | `/api/mining/stop` | Pauses mining activity | Protected |
| `GET` | `/api/status` | Application status (includes `mining_enabled` field) | Protected |
| `GET` | `/health` | Simple health check `{"status": "ok"}` | Public |
| `GET` | `/healthz` | Container health check endpoint | Public |

### WebSocket Events
- **`mining_state`**: Emitted to connected clients on status changes:
  ```json
  { "mining_enabled": true }
  ```
- **`initial_state`**: Includes `mining_enabled: boolean` upon connection.

---

## 🛡️ Security & Privacy Notice

- **Zero Credentials in Git**: All sensitive credentials, server configurations, SSH keys, and tokens are strictly excluded from source control via `.gitignore`.
- **Protected Endpoints**: When Dashboard Password Protection is enabled in **Settings**, all API endpoints and WebSocket operations require valid session authentication.
- **Reverse Proxy Recommended for Public Web**: When exposing port `8080` to the internet, use HTTPS via a reverse proxy (e.g. Caddy, Nginx, or Traefik) and enable password protection in the Settings tab.

---

## 📜 Credits & Acknowledgments

- **Mod Author**: [Murr (vtstv)](https://github.com/vtstv)
- **Upstream Project**: [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner) by [@rangermix](https://github.com/rangermix)
- **Original Application**: [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner) by [@DevilXD](https://github.com/DevilXD)
- Distributed under the [MIT License](LICENSE).
