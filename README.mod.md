# Twitch Drops Miner (Mod v0.6 by Murr)

An automated, bandwidth-free Twitch drops miner with **Start/Pause controls**, **dual-stack IPv4/IPv6 Docker support**, and **web dashboard authentication**.

<p align="center">
  <a href="https://github.com/vtstv"><img src="https://img.shields.io/badge/Mod%20v0.6-by%20Murr-blueviolet?style=flat-square&logo=github" alt="Mod v0.6 by Murr"></a>
  <a href="https://hub.docker.com/r/vtstv/twitch-drops-miner"><img src="https://img.shields.io/docker/pulls/vtstv/twitch-drops-miner?style=flat-square&color=blue" alt="Docker Pulls"></a>
  <a href="https://github.com/rangermix/TwitchDropsMiner"><img src="https://img.shields.io/badge/Upstream-rangermix-green?style=flat-square" alt="Upstream"></a>
  <a href="https://github.com/vtstv/TwitchDropsMinerMod/blob/main/LICENSE"><img src="https://img.shields.io/github/license/vtstv/TwitchDropsMinerMod?style=flat-square&color=orange" alt="License"></a>
</p>

![Web Dashboard](./screenshot.png)

---

## ⚡ What's New in this Mod

- **⏸ Pause / Resume Mining**: Start or pause drop mining anytime from the web UI header button or REST API without closing the container.
- **🌐 IPv4 & IPv6 Dual-Stack**: Binds to `::` on Linux/Docker, enabling native IPv6 and IPv4 traffic, host networking (`--network host`), and NAT64 compatibility.
- **🔐 Dashboard Password Protection**: Protect the web interface and API with a password in **Settings** (salted scrypt hashing, session tokens).
- **🔑 Headless Twitch OAuth**: Displays the Twitch activation URL and device code directly in terminal / `docker logs` for easy remote VPS setup.
- **🎁 All-Drops Games Whitelist**: Specify games to collect all drops and in-game items for, even when global Direct Entitlement is disabled.
- **🔄 Campaign Auto-Reload & Game Discovery**: Periodically reloads active campaigns at configurable intervals, automatically adds newly discovered games to the watch list, and optionally allows mining unlinked campaigns.
- **🤖 Anti-Bot Behavior Simulation**: Adds human-like watch beacon jitter, channel switch delays, and optional periodic breaks to mimic authentic viewer habits.
- **📡 Mining Control API**: Simple REST endpoints to automate pausing and resuming mining via scripts or Home Assistant.

---

## 🚀 Quick Start

### Local Docker Compose
1. Clone the repository:
   ```bash
   git clone https://github.com/vtstv/TwitchDropsMinerMod.git
   cd TwitchDropsMinerMod
   ```
2. Start the container:
   ```bash
   docker compose up -d
   ```
3. Open **<http://localhost:28088>**.
4. To stop: `docker compose down`.

### Linux / Remote VPS (Docker)
Run with host networking (supports IPv4 and IPv6):
```bash
docker run -d \
  --name twitch-drops-miner \
  --network host \
  --restart unless-stopped \
  -v /opt/twitch-drops-miner/data:/app/data \
  -v /opt/twitch-drops-miner/logs:/app/logs \
  vtstv/twitch-drops-miner:latest
```
Open **`http://<server-ip>:8080`**.  
To retrieve the Twitch login code, run:
```bash
docker logs -f twitch-drops-miner
```

### From Source (Python 3.12+)
```bash
pip install -e .
python main.py
```
Open **<http://localhost:8080>**.

---

## 📡 Mining API

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/mining/toggle` | Toggle mining (pause / resume) |
| `POST` | `/api/mining/start`  | Resume mining |
| `POST` | `/api/mining/stop`   | Pause mining |
| `GET`  | `/api/mining/status` | Current state (`{"mining_enabled": true/false}`) |

---

## 📜 Credits

- Mod by [Murr (vtstv)](https://github.com/vtstv)
- Upstream: [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner)
- Original: [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner)
- License: [MIT](LICENSE)
