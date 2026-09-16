# Twitch Drops Miner (Mod by Murr)

> A high-performance, automated Twitch drops miner with **Start/Pause mining controls**, **dual-stack IPv4 & IPv6 Docker networking**, **web dashboard authentication**, and **headless remote deployment support**.

<p align="center">
  <a href="https://github.com/vtstv"><img src="https://img.shields.io/badge/Mod%20by-Murr-blueviolet?style=for-the-badge&logo=github" alt="Mod by Murr"></a>
  <a href="https://hub.docker.com/r/vtstv/twitch-drops-miner"><img src="https://img.shields.io/docker/pulls/vtstv/twitch-drops-miner?style=for-the-badge&color=blue" alt="Docker Pulls"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python 3.12 or newer"></a>
  <a href="https://github.com/rangermix/TwitchDropsMiner"><img src="https://img.shields.io/badge/Upstream-rangermix%2FTwitchDropsMiner-green?style=for-the-badge" alt="Upstream"></a>
  <a href="https://github.com/vtstv/TwitchDropsMinerMod/blob/main/LICENSE"><img src="https://img.shields.io/github/license/vtstv/TwitchDropsMinerMod?style=for-the-badge&color=orange" alt="License"></a>
</p>

Twitch Drops Miner is a low-bandwidth, headless application that discovers eligible
campaigns, selects an appropriate live channel, and tracks drop progress from a web
dashboard. It sends Twitch watch events without downloading the stream itself.

![Twitch Drops Miner web dashboard showing campaign progress, output, and channels](./screenshot.png)

---

## 🌟 Mod Enhancements & Key Features

This fork extends the upstream [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner) with features specifically crafted for server hosting, VPS environments, containerization, and full mining control:

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

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for issue reporting, development setup,
pull requests, required unit and regression checks, and independent adversarial review.
Coding agents must follow the mandatory workflow in [AGENTS.md](./AGENTS.md), also
available through the `CLAUDE.md` and `GEMINI.md` symlinks. The pull request template
records validation and review evidence.

## Contributors

Contributors are credited automatically when their pull requests are merged into `main`.

<!-- contributors:start -->
| Contributor | Merged pull requests |
| --- | --- |
| [@birdhimself](https://github.com/birdhimself) | [#41](https://github.com/rangermix/TwitchDropsMiner/pull/41) |
| [@capkz](https://github.com/capkz) | [#70](https://github.com/rangermix/TwitchDropsMiner/pull/70) |
| [@EthanBlazkowicz](https://github.com/EthanBlazkowicz) | [#33](https://github.com/rangermix/TwitchDropsMiner/pull/33) |
| [@Klages](https://github.com/Klages) | [#94](https://github.com/rangermix/TwitchDropsMiner/pull/94) · [#95](https://github.com/rangermix/TwitchDropsMiner/pull/95) |
| [@Knight-sys](https://github.com/Knight-sys) | [#3](https://github.com/rangermix/TwitchDropsMiner/pull/3) |
| [@rangermix](https://github.com/rangermix) | [#1](https://github.com/rangermix/TwitchDropsMiner/pull/1) · [#2](https://github.com/rangermix/TwitchDropsMiner/pull/2) · [#7](https://github.com/rangermix/TwitchDropsMiner/pull/7) · [#8](https://github.com/rangermix/TwitchDropsMiner/pull/8) · [#9](https://github.com/rangermix/TwitchDropsMiner/pull/9) · [#13](https://github.com/rangermix/TwitchDropsMiner/pull/13) · [#20](https://github.com/rangermix/TwitchDropsMiner/pull/20) · [#24](https://github.com/rangermix/TwitchDropsMiner/pull/24) · [#29](https://github.com/rangermix/TwitchDropsMiner/pull/29) · [#32](https://github.com/rangermix/TwitchDropsMiner/pull/32) · [#45](https://github.com/rangermix/TwitchDropsMiner/pull/45) · [#74](https://github.com/rangermix/TwitchDropsMiner/pull/74) · [#79](https://github.com/rangermix/TwitchDropsMiner/pull/79) · [#80](https://github.com/rangermix/TwitchDropsMiner/pull/80) · [#84](https://github.com/rangermix/TwitchDropsMiner/pull/84) · [#86](https://github.com/rangermix/TwitchDropsMiner/pull/86) · [#88](https://github.com/rangermix/TwitchDropsMiner/pull/88) · [#93](https://github.com/rangermix/TwitchDropsMiner/pull/93) · [#89](https://github.com/rangermix/TwitchDropsMiner/pull/89) · [#90](https://github.com/rangermix/TwitchDropsMiner/pull/90) · [#91](https://github.com/rangermix/TwitchDropsMiner/pull/91) · [#92](https://github.com/rangermix/TwitchDropsMiner/pull/92) · [#104](https://github.com/rangermix/TwitchDropsMiner/pull/104) · [#105](https://github.com/rangermix/TwitchDropsMiner/pull/105) |
| [@Sean-Destefano](https://github.com/Sean-Destefano) | [#49](https://github.com/rangermix/TwitchDropsMiner/pull/49) |
| [@SimpliAj](https://github.com/SimpliAj) | [#72](https://github.com/rangermix/TwitchDropsMiner/pull/72) |
| [@Stein-N](https://github.com/Stein-N) | [#71](https://github.com/rangermix/TwitchDropsMiner/pull/71) |
| [@vurmil](https://github.com/vurmil) | [#12](https://github.com/rangermix/TwitchDropsMiner/pull/12) · [#17](https://github.com/rangermix/TwitchDropsMiner/pull/17) · [#18](https://github.com/rangermix/TwitchDropsMiner/pull/18) · [#100](https://github.com/rangermix/TwitchDropsMiner/pull/100) |
<!-- contributors:end -->

## 📜 Credits & Acknowledgments

- **Mod Author**: [Murr (vtstv)](https://github.com/vtstv)
- **Upstream Project**: [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner) by [@rangermix](https://github.com/rangermix)
- **Original Application**: [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner) by [@DevilXD](https://github.com/DevilXD)
- Distributed under the [MIT License](LICENSE).

<details>
<summary>Original project and translation credits</summary>

### Original project contributions

- [@guihkx](https://github.com/guihkx) — CI scripts, CI maintenance, and Linux builds
- [@kWAYTV](https://github.com/kWAYTV) — dark mode theme

### Translation credits

- **Arabic** — [@Bamboozul](https://github.com/Bamboozul)
- **Chinese (Simplified)** — [@Suz1e](https://github.com/Suz1e),
  [@wwj010](https://github.com/wwj010), and
  [@zhangminghao1989](https://github.com/zhangminghao1989)
- **Chinese (Traditional)** — [@Ricky103403](https://github.com/Ricky103403) and
  [@LusTerCsI](https://github.com/LusTerCsI)
- **Czech** — [@nwvh](https://github.com/nwvh)
- **Danish** — [@Kjerne](https://github.com/Kjerne)
- **French** — [@roobini-gamer](https://github.com/roobini-gamer) and
  [@Calvineries](https://github.com/Calvineries)
- **German** — [@ThisIsCyreX](https://github.com/ThisIsCyreX)
- **Hungarian** — [@centipederat](https://github.com/centipederat)
- **Indonesian** — [@Eriza-Z](https://github.com/Eriza-Z)
- **Italian** — [@casungo](https://github.com/casungo)
- **Japanese** — [@ShimadaNanaki](https://github.com/ShimadaNanaki)
- **Polish** — [@Patriot99](https://github.com/Patriot99), co-authored with
  [@DevilXD](https://github.com/DevilXD)
- **Portuguese** — [@zarigata](https://github.com/zarigata)
- **Russian** — [@Sergo1217](https://github.com/Sergo1217) and
  [@kilroy98](https://github.com/kilroy98)
- **Spanish** — [@Shofuu](https://github.com/Shofuu)
- **Turkish** — [@alikdb](https://github.com/alikdb)
- **Ukrainian** — [@Nollasko](https://github.com/Nollasko) and
  [@kilroy98](https://github.com/kilroy98)

</details>
