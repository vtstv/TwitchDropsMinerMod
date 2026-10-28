# Twitch Drops Miner (Mod v0.13 by Murr)

An automated, bandwidth-free Twitch drops miner with **Start/Pause controls**, **All-Drops Games Whitelist**, **dual-stack IPv4/IPv6 Docker support**, and **web dashboard authentication**, updated to upstream **v2.4.0** with **organized Settings tabs**, **timed mining pauses**, **reward type priorities**, **Discord webhook notifications**, **daily mining hours**, **priority fallback mode**, **channel ban filtering**, **diagnosis data dumps**, **HEAD-segment watch requests**, **account-link filters & optional unlinked mining**, **in-dashboard browser sign-in**, and **automatic session renewal**.

<p align="center">
  <a href="https://github.com/vtstv/TwitchDropsMinerMod"><img src="https://img.shields.io/badge/Mod%20v0.13-by%20Murr-blueviolet?style=flat-square&logo=github" alt="Mod v0.13 by Murr"></a>
  <a href="https://hub.docker.com/r/vtstv/twitch-drops-miner"><img src="https://img.shields.io/docker/pulls/vtstv/twitch-drops-miner?style=flat-square&color=blue" alt="Docker Pulls"></a>
  <a href="https://github.com/rangermix/TwitchDropsMiner"><img src="https://img.shields.io/badge/Upstream-v2.4.0-green?style=flat-square" alt="Upstream v2.4.0"></a>
  <a href="https://github.com/vtstv/TwitchDropsMinerMod/blob/main/LICENSE"><img src="https://img.shields.io/github/license/vtstv/TwitchDropsMinerMod?style=flat-square&color=orange" alt="License"></a>
</p>

![Web Dashboard](./screenshot.png)

---

## ⚡ What's New in this Mod

- **⏸ Native Timed Pause & Mining API**: Upstream's flexible pause menu (10 minutes, 1 hour, until tomorrow / midnight, or until resumed) integrated seamlessly with REST API endpoints (`/api/mining/toggle`, `/api/mining/start`, `/api/mining/stop`, `/api/mining/status`) for automation or Home Assistant.
- **📑 5-Tab Settings Organization**: Settings are neatly organized into **General**, **Mining**, **Games**, **Notifications**, and **Account & Maintenance**. Mod settings are fully integrated into their respective tabs.
- **🎯 Reward Types Priority**: Draggable and configurable priority list for reward types (**Direct Entitlement / Item**, **Badge**, **Emote**, **Unknown**).
- **🎁 All-Drops Games Whitelist**: Interactive two-pane selector (in the **Games** tab) to specify games where all drops and in-game items are collected, even when global Direct Entitlement is disabled.
- **🌐 IPv4 & IPv6 Dual-Stack**: Binds to `::` on Linux/Docker, enabling native IPv6 and IPv4 traffic, host networking (`--network host`), and NAT64 compatibility.
- **⏰ Daily Mining Hours**: Set daily mining schedules using local time; watching pauses and resumes automatically outside configured hours.
- **🔔 Discord & Telegram Notifications**: Real-time notifications for claimed drops, with Discord alerts including reward artwork.
- **🔄 Priority Fallback Mode**: Automatically mine other eligible campaigns when all prioritized games are completed or offline.
- **🚫 Channel Ban Filtering**: Automatically skip channels reporting active or temporary bans.
- **🩺 Diagnosis Dumps**: Deidentified miner state and sanitized API diagnostics exportable from Settings for easy troubleshooting.
- **📡 Restored Drop Progress**: Polling stream playlists and sending HEAD requests for new media segments, restoring drop progress without downloading stream video or audio data.
- **🔗 Account-Link Filters & Optional Unlinked Mining**: Filter campaigns by All / Linked / Not Linked and optionally allow mining campaigns reported as Not Linked.
- **🔄 Campaign Auto-Reload & Game Discovery**: Periodically reloads active campaigns at configurable intervals and automatically adds newly discovered games to the watch list.
- **🤖 Anti-Bot Behavior Simulation**: Adds human-like watch beacon jitter, channel switch delays, and optional periodic breaks to mimic authentic viewer habits.
- **🔐 Dashboard Password Protection**: Protect the web interface and API with a password at the bottom of the **Account & Maintenance** tab (salted scrypt hashing, session tokens).
- **🖥️ In-Dashboard Container Browser Sign In**: Embedded Chromium sign-in directly in the dashboard, with automatic background session renewal and desktop login helper fallback.
- **🖼️ Optional Stream Preview & Avatar**: Responsive layout improvements, Twitch user avatar, and optional opt-in stream thumbnail preview.
- **⚡ VFS Storage Optimization**: Docker build layers flattened for lightweight deployment on container hosts running the Docker VFS storage driver.

---

## 🚀 Quick Start

With Docker installed, choose one setup below.

### With Docker Compose (Recommended)

1. Save the following as `docker-compose.yml` (or `compose.yaml`) in a dedicated folder:
   ```yaml
   services:
     twitch-drops-miner:
       image: vtstv/twitch-drops-miner:latest
       container_name: twitch-drops-miner
       init: true
       stop_grace_period: 30s
       shm_size: 256m
       ports:
         - "8080:8080"
       volumes:
         - ./data:/app/data
         - ./logs:/app/logs
       environment:
         TZ: Europe/Berlin
       restart: unless-stopped
   ```
   *(Set `TZ` to your home internet connection's timezone, e.g. `Europe/Berlin`).*

2. Start the container:
   ```bash
   docker compose up -d
   ```

3. Open **<http://localhost:8080>** in your browser.

4. To stop:
   ```bash
   docker compose down
   ```

### With Docker Run

```bash
docker run -d \
  --name twitch-drops-miner --init --stop-timeout 30 --shm-size 256m \
  -p 8080:8080 -e TZ=Europe/Berlin \
  -v "${PWD}/data:/app/data" \
  -v "${PWD}/logs:/app/logs" \
  --restart unless-stopped \
  vtstv/twitch-drops-miner:latest
```

### Linux / Remote VPS (Host Networking)

Run with host networking to enable native dual-stack IPv4 and IPv6 support:
```bash
docker pull vtstv/twitch-drops-miner:latest
docker run -d \
  --name twitch-drops-miner --init --stop-timeout 30 --shm-size 256m \
  --network host \
  --restart unless-stopped \
  -e TZ=Europe/Berlin \
  -v /opt/twitch-drops-miner/data:/app/data \
  -v /opt/twitch-drops-miner/logs:/app/logs \
  vtstv/twitch-drops-miner:latest
```
Open **`http://<server-ip>:8080`**.

---

## 🔑 Sign In (In-Dashboard Browser Sign-In & Helper Fallback)

1. Open the dashboard. When Twitch login is required, TDM displays its container browser with the Twitch sign-in page automatically.
2. Sign in and complete any two-factor or email verification inside that browser. Expand **Copy and paste** to transfer text to or from the browser. The browser closes automatically after sign in; **Finish sign in** remains available if it stays open.
3. If Twitch rejects the embedded browser, select **Use desktop helper** and run the matching helper from releases on your PC to complete sign-in.
4. TDM verifies your account and campaign access, saves the session, and returns to the normal dashboard.
5. TDM automatically renews the session in the background with its bundled Chromium engine.
6. To switch accounts, use **Settings → Account & Maintenance → Log out of Twitch**.

*Existing users:* If you have an active session in `data/cookies.jar` or `data/imported-session.json`, TDM restores it automatically on startup without needing to re-login.

---

## 📡 Mining API

Control mining state programmatically via REST API:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/mining/toggle` | Toggle mining (pause / resume) |
| `POST` | `/api/mining/start`  | Resume mining |
| `POST` | `/api/mining/stop`   | Pause mining |
| `GET`  | `/api/mining/status` | Current state (`{"mining_enabled": true/false}`) |

---

## 📖 Documentation & User Guides

Browse the documentation in [docs](docs/README.md) or the [GitHub wiki](https://github.com/rangermix/TwitchDropsMiner/wiki):
- [Installation and updates](docs/installation.md)
- [Login, migration, and recovery](docs/authentication.md)
- [Games, campaigns, inventory, and history](docs/usage.md)
- [Dashboard password and reverse proxies](docs/dashboard-access.md)
- [Telegram and Discord notifications](docs/notifications.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 🤝 Help and contributions

Search [existing issues](https://github.com/rangermix/TwitchDropsMiner/issues) before reporting a problem. Use the [bug-report form](https://github.com/rangermix/TwitchDropsMiner/issues/new?template=bug_report.yml) with the running app version, hosting environment, reproduction steps, and redacted evidence.
See [CONTRIBUTING.md](CONTRIBUTING.md) for bug reports, translations, and development.

Based on [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner) and [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner).

## Contributors

<details>
<summary>People who contributed merged pull requests</summary>

<!-- contributors:start -->
| Contributor | Merged pull requests |
| --- | --- |
| [@0zLloen](https://github.com/0zLloen) | [#152](https://github.com/rangermix/TwitchDropsMiner/pull/152) · [#185](https://github.com/rangermix/TwitchDropsMiner/pull/185) · [#191](https://github.com/rangermix/TwitchDropsMiner/pull/191) · [#188](https://github.com/rangermix/TwitchDropsMiner/pull/188) · [#192](https://github.com/rangermix/TwitchDropsMiner/pull/192) · [#193](https://github.com/rangermix/TwitchDropsMiner/pull/193) · [#194](https://github.com/rangermix/TwitchDropsMiner/pull/194) · [#186](https://github.com/rangermix/TwitchDropsMiner/pull/186) · [#189](https://github.com/rangermix/TwitchDropsMiner/pull/189) · [#175](https://github.com/rangermix/TwitchDropsMiner/pull/175) · [#176](https://github.com/rangermix/TwitchDropsMiner/pull/176) |
| [@3lb0z0](https://github.com/3lb0z0) | [#110](https://github.com/rangermix/TwitchDropsMiner/pull/110) |
| [@andreluisfc](https://github.com/andreluisfc) | [#76](https://github.com/rangermix/TwitchDropsMiner/pull/76) |
| [@birdhimself](https://github.com/birdhimself) | [#41](https://github.com/rangermix/TwitchDropsMiner/pull/41) |
| [@brk275](https://github.com/brk275) | [#171](https://github.com/rangermix/TwitchDropsMiner/pull/171) · [#172](https://github.com/rangermix/TwitchDropsMiner/pull/172) · [#179](https://github.com/rangermix/TwitchDropsMiner/pull/179) |
| [@capkz](https://github.com/capkz) | [#70](https://github.com/rangermix/TwitchDropsMiner/pull/70) |
| [@Dolverin](https://github.com/Dolverin) | [#142](https://github.com/rangermix/TwitchDropsMiner/pull/142) |
| [@EthanBlazkowicz](https://github.com/EthanBlazkowicz) | [#33](https://github.com/rangermix/TwitchDropsMiner/pull/33) |
| [@Klages](https://github.com/Klages) | [#94](https://github.com/rangermix/TwitchDropsMiner/pull/94) · [#95](https://github.com/rangermix/TwitchDropsMiner/pull/95) · [#183](https://github.com/rangermix/TwitchDropsMiner/pull/183) |
| [@Knight-sys](https://github.com/Knight-sys) | [#3](https://github.com/rangermix/TwitchDropsMiner/pull/3) |
| [@rangermix](https://github.com/rangermix) | [#1](https://github.com/rangermix/TwitchDropsMiner/pull/1) · [#2](https://github.com/rangermix/TwitchDropsMiner/pull/2) · [#7](https://github.com/rangermix/TwitchDropsMiner/pull/7) · [#8](https://github.com/rangermix/TwitchDropsMiner/pull/8) · [#9](https://github.com/rangermix/TwitchDropsMiner/pull/9) · [#13](https://github.com/rangermix/TwitchDropsMiner/pull/13) · [#20](https://github.com/rangermix/TwitchDropsMiner/pull/20) · [#24](https://github.com/rangermix/TwitchDropsMiner/pull/24) · [#29](https://github.com/rangermix/TwitchDropsMiner/pull/29) · [#32](https://github.com/rangermix/TwitchDropsMiner/pull/32) · [#45](https://github.com/rangermix/TwitchDropsMiner/pull/45) · [#74](https://github.com/rangermix/TwitchDropsMiner/pull/74) · [#79](https://github.com/rangermix/TwitchDropsMiner/pull/79) · [#80](https://github.com/rangermix/TwitchDropsMiner/pull/80) · [#84](https://github.com/rangermix/TwitchDropsMiner/pull/84) · [#86](https://github.com/rangermix/TwitchDropsMiner/pull/86) · [#88](https://github.com/rangermix/TwitchDropsMiner/pull/88) · [#93](https://github.com/rangermix/TwitchDropsMiner/pull/93) · [#89](https://github.com/rangermix/TwitchDropsMiner/pull/89) · [#90](https://github.com/rangermix/TwitchDropsMiner/pull/90) · [#91](https://github.com/rangermix/TwitchDropsMiner/pull/91) · [#92](https://github.com/rangermix/TwitchDropsMiner/pull/92) · [#104](https://github.com/rangermix/TwitchDropsMiner/pull/104) · [#105](https://github.com/rangermix/TwitchDropsMiner/pull/105) · [#116](https://github.com/rangermix/TwitchDropsMiner/pull/116) · [#119](https://github.com/rangermix/TwitchDropsMiner/pull/119) · [#120](https://github.com/rangermix/TwitchDropsMiner/pull/120) · [#124](https://github.com/rangermix/TwitchDropsMiner/pull/124) · [#125](https://github.com/rangermix/TwitchDropsMiner/pull/125) · [#126](https://github.com/rangermix/TwitchDropsMiner/pull/126) · [#127](https://github.com/rangermix/TwitchDropsMiner/pull/127) · [#131](https://github.com/rangermix/TwitchDropsMiner/pull/131) · [#133](https://github.com/rangermix/TwitchDropsMiner/pull/133) · [#145](https://github.com/rangermix/TwitchDropsMiner/pull/145) · [#146](https://github.com/rangermix/TwitchDropsMiner/pull/146) · [#149](https://github.com/rangermix/TwitchDropsMiner/pull/149) · [#153](https://github.com/rangermix/TwitchDropsMiner/pull/153) · [#154](https://github.com/rangermix/TwitchDropsMiner/pull/154) · [#159](https://github.com/rangermix/TwitchDropsMiner/pull/159) · [#160](https://github.com/rangermix/TwitchDropsMiner/pull/160) · [#161](https://github.com/rangermix/TwitchDropsMiner/pull/161) · [#164](https://github.com/rangermix/TwitchDropsMiner/pull/164) · [#167](https://github.com/rangermix/TwitchDropsMiner/pull/167) · [#169](https://github.com/rangermix/TwitchDropsMiner/pull/169) |
| [@Sean-Destefano](https://github.com/Sean-Destefano) | [#49](https://github.com/rangermix/TwitchDropsMiner/pull/49) |
| [@SimpliAj](https://github.com/SimpliAj) | [#72](https://github.com/rangermix/TwitchDropsMiner/pull/72) |
| [@Stein-N](https://github.com/Stein-N) | [#71](https://github.com/rangermix/TwitchDropsMiner/pull/71) |
| [@vurmil](https://github.com/vurmil) | [#12](https://github.com/rangermix/TwitchDropsMiner/pull/12) · [#17](https://github.com/rangermix/TwitchDropsMiner/pull/17) · [#18](https://github.com/rangermix/TwitchDropsMiner/pull/18) · [#100](https://github.com/rangermix/TwitchDropsMiner/pull/100) · [#150](https://github.com/rangermix/TwitchDropsMiner/pull/150) · [#102](https://github.com/rangermix/TwitchDropsMiner/pull/102) · [#101](https://github.com/rangermix/TwitchDropsMiner/pull/101) |
<!-- contributors:end -->

</details>

## 📜 Credits

- Mod by [Murr (vtstv)](https://github.com/vtstv/TwitchDropsMinerMod)
- Upstream: [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner)
- Original: [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner)
- License: [MIT](LICENSE)
