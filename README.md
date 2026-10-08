# Twitch Drops Miner (Mod v0.11 by Murr)

An automated, bandwidth-free Twitch drops miner with **Start/Pause controls**, **All-Drops Games Whitelist**, **dual-stack IPv4/IPv6 Docker support**, and **web dashboard authentication**, updated to upstream **v2.2.1** with **HEAD-segment watch requests**, **account-link filters & optional unlinked mining**, **in-dashboard browser sign-in**, and **automatic session renewal**.

<p align="center">
  <a href="https://github.com/vtstv/TwitchDropsMinerMod"><img src="https://img.shields.io/badge/Mod%20v0.11-by%20Murr-blueviolet?style=flat-square&logo=github" alt="Mod v0.11 by Murr"></a>
  <a href="https://hub.docker.com/r/vtstv/twitch-drops-miner"><img src="https://img.shields.io/docker/pulls/vtstv/twitch-drops-miner?style=flat-square&color=blue" alt="Docker Pulls"></a>
  <a href="https://github.com/rangermix/TwitchDropsMiner"><img src="https://img.shields.io/badge/Upstream-v2.2.1-green?style=flat-square" alt="Upstream v2.2.1"></a>
  <a href="https://github.com/vtstv/TwitchDropsMinerMod/blob/main/LICENSE"><img src="https://img.shields.io/github/license/vtstv/TwitchDropsMinerMod?style=flat-square&color=orange" alt="License"></a>
</p>

![Web Dashboard](./screenshot.png)

---

## ⚡ What's New in this Mod

- **⏸ Pause / Resume Mining**: Start or pause drop mining anytime from the web UI header button or REST API without closing the container.
- **🎁 All-Drops Games Whitelist**: Interactive two-pane selector to specify games where all drops and in-game items are collected, even when global Direct Entitlement is disabled.
- **🌐 IPv4 & IPv6 Dual-Stack**: Binds to `::` on Linux/Docker, enabling native IPv6 and IPv4 traffic, host networking (`--network host`), and NAT64 compatibility.
- **📡 Restored Drop Progress (v2.2.1)**: Upstream v2.2.1 polls stream playlists and sends HEAD requests for new media segments, restoring drop progress without downloading video or audio data.
- **🔗 Account-Link Filters & Optional Unlinked Mining**: Official upstream integration allows filtering campaigns by All / Linked / Not Linked and optional mining of campaigns reported as Not Linked.
- **🔄 Campaign Auto-Reload & Game Discovery**: Periodically reloads active campaigns at configurable intervals, automatically adds newly discovered games to the watch list, and optionally allows mining unlinked campaigns.
- **🤖 Anti-Bot Behavior Simulation**: Adds human-like watch beacon jitter, channel switch delays, and optional periodic breaks to mimic authentic viewer habits.
- **📡 Mining Control API**: Simple REST endpoints to automate pausing and resuming mining via scripts or Home Assistant.
- **🔐 Dashboard Password Protection**: Protect the web interface and API with a password at the bottom of **Settings** (salted scrypt hashing, session tokens).
- **🖥️ In-Dashboard Container Browser Sign In**: Integrated upstream browser sign-in directly in the dashboard using Chromium inside the container, with optional desktop login helper fallback.
- **🖼️ Optional Stream Preview & Avatar**: Upstream responsive layout improvements, Twitch user avatar, and optional opt-in stream thumbnail preview.
- **⚡ VFS Storage Optimization**: Docker build layers flattened for lightweight deployment on container hosts running the Docker VFS storage driver.

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
3. Open **<http://localhost:28088>** (or custom port configured in `docker-compose.yml`).
4. To stop: `docker compose down`.

### Linux / Remote VPS (Docker)
Run with host networking (supports native IPv4 and IPv6):
```bash
docker pull vtstv/twitch-drops-miner:latest
docker run -d \
  --name twitch-drops-miner --init --stop-timeout 30 --shm-size 256m \
  --network host \
  --restart unless-stopped \
  -e TZ=UTC \
  -v /opt/twitch-drops-miner/data:/app/data \
  -v /opt/twitch-drops-miner/logs:/app/logs \
  vtstv/twitch-drops-miner:latest
```
Open **`http://<server-ip>:8080`**.

---

## 🔑 Sign In (v2.1.1 Dashboard Browser Login & Helper Fallback)

1. Open the dashboard. When Twitch login is required, TDM displays its container browser with the Twitch sign-in page automatically.
2. Sign in and complete any two-factor or email verification inside that browser. Select **Finish sign in** after Twitch confirms you are signed in.
3. If Twitch rejects the embedded browser, select **Use desktop helper** and run the matching helper from releases on your PC to complete sign-in.
4. TDM verifies your account and campaign access, saves the session, and returns to the normal dashboard.
5. TDM automatically renews the session in the background with its bundled Chromium engine.
6. To switch accounts, use **Settings → Log out of Twitch** at the bottom of the Settings tab.

*Existing users:* If you have an active session in `data/cookies.jar` or `data/imported-session.json`, TDM restores it automatically on startup without needing to re-login.

---

## 📡 Mining API

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
- [Telegram notifications](docs/notifications.md)
- [Troubleshooting](docs/troubleshooting.md)

<<<<<<< HEAD
=======
## Help and contributions

Search [existing issues](https://github.com/rangermix/TwitchDropsMiner/issues) before
reporting a problem. Use the [bug-report form](https://github.com/rangermix/TwitchDropsMiner/issues/new?template=bug_report.yml)
with the running app version, hosting environment, reproduction steps, and redacted evidence.
See [CONTRIBUTING.md](CONTRIBUTING.md) for bug reports, translations,
and development. This fork uses AI-assisted development with automated checks and
independent review. Agents acknowledge work in the relevant issue or PR before starting
and post the outcome there when work ends or pauses.

Based on [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner).
See [credits](docs/credits.md) for the original project and translation contributors.
You can support this fork by [starring it](https://github.com/rangermix/TwitchDropsMiner)
or [buying the maintainer a coffee](https://buymeacoffee.com/rangermix).

>>>>>>> main
## Contributors

<details>
<summary>People who contributed merged pull requests</summary>

<!-- contributors:start -->
| Contributor | Merged pull requests |
| --- | --- |
| [@0zLloen](https://github.com/0zLloen) | [#152](https://github.com/rangermix/TwitchDropsMiner/pull/152) |
| [@3lb0z0](https://github.com/3lb0z0) | [#110](https://github.com/rangermix/TwitchDropsMiner/pull/110) |
| [@birdhimself](https://github.com/birdhimself) | [#41](https://github.com/rangermix/TwitchDropsMiner/pull/41) |
| [@capkz](https://github.com/capkz) | [#70](https://github.com/rangermix/TwitchDropsMiner/pull/70) |
| [@EthanBlazkowicz](https://github.com/EthanBlazkowicz) | [#33](https://github.com/rangermix/TwitchDropsMiner/pull/33) |
| [@Klages](https://github.com/Klages) | [#94](https://github.com/rangermix/TwitchDropsMiner/pull/94) · [#95](https://github.com/rangermix/TwitchDropsMiner/pull/95) |
| [@Knight-sys](https://github.com/Knight-sys) | [#3](https://github.com/rangermix/TwitchDropsMiner/pull/3) |
| [@rangermix](https://github.com/rangermix) | [#1](https://github.com/rangermix/TwitchDropsMiner/pull/1) · [#2](https://github.com/rangermix/TwitchDropsMiner/pull/2) · [#7](https://github.com/rangermix/TwitchDropsMiner/pull/7) · [#8](https://github.com/rangermix/TwitchDropsMiner/pull/8) · [#9](https://github.com/rangermix/TwitchDropsMiner/pull/9) · [#13](https://github.com/rangermix/TwitchDropsMiner/pull/13) · [#20](https://github.com/rangermix/TwitchDropsMiner/pull/20) · [#24](https://github.com/rangermix/TwitchDropsMiner/pull/24) · [#29](https://github.com/rangermix/TwitchDropsMiner/pull/29) · [#32](https://github.com/rangermix/TwitchDropsMiner/pull/32) · [#45](https://github.com/rangermix/TwitchDropsMiner/pull/45) · [#74](https://github.com/rangermix/TwitchDropsMiner/pull/74) · [#79](https://github.com/rangermix/TwitchDropsMiner/pull/79) · [#80](https://github.com/rangermix/TwitchDropsMiner/pull/80) · [#84](https://github.com/rangermix/TwitchDropsMiner/pull/84) · [#86](https://github.com/rangermix/TwitchDropsMiner/pull/86) · [#88](https://github.com/rangermix/TwitchDropsMiner/pull/88) · [#93](https://github.com/rangermix/TwitchDropsMiner/pull/93) · [#89](https://github.com/rangermix/TwitchDropsMiner/pull/89) · [#90](https://github.com/rangermix/TwitchDropsMiner/pull/90) · [#91](https://github.com/rangermix/TwitchDropsMiner/pull/91) · [#92](https://github.com/rangermix/TwitchDropsMiner/pull/92) · [#104](https://github.com/rangermix/TwitchDropsMiner/pull/104) · [#105](https://github.com/rangermix/TwitchDropsMiner/pull/105) · [#116](https://github.com/rangermix/TwitchDropsMiner/pull/116) · [#119](https://github.com/rangermix/TwitchDropsMiner/pull/119) · [#120](https://github.com/rangermix/TwitchDropsMiner/pull/120) · [#124](https://github.com/rangermix/TwitchDropsMiner/pull/124) · [#125](https://github.com/rangermix/TwitchDropsMiner/pull/125) · [#126](https://github.com/rangermix/TwitchDropsMiner/pull/126) · [#127](https://github.com/rangermix/TwitchDropsMiner/pull/127) · [#131](https://github.com/rangermix/TwitchDropsMiner/pull/131) · [#133](https://github.com/rangermix/TwitchDropsMiner/pull/133) · [#145](https://github.com/rangermix/TwitchDropsMiner/pull/145) · [#146](https://github.com/rangermix/TwitchDropsMiner/pull/146) · [#149](https://github.com/rangermix/TwitchDropsMiner/pull/149) · [#153](https://github.com/rangermix/TwitchDropsMiner/pull/153) · [#154](https://github.com/rangermix/TwitchDropsMiner/pull/154) · [#159](https://github.com/rangermix/TwitchDropsMiner/pull/159) · [#160](https://github.com/rangermix/TwitchDropsMiner/pull/160) · [#161](https://github.com/rangermix/TwitchDropsMiner/pull/161) · [#164](https://github.com/rangermix/TwitchDropsMiner/pull/164) |
| [@Sean-Destefano](https://github.com/Sean-Destefano) | [#49](https://github.com/rangermix/TwitchDropsMiner/pull/49) |
| [@SimpliAj](https://github.com/SimpliAj) | [#72](https://github.com/rangermix/TwitchDropsMiner/pull/72) |
| [@Stein-N](https://github.com/Stein-N) | [#71](https://github.com/rangermix/TwitchDropsMiner/pull/71) |
| [@vurmil](https://github.com/vurmil) | [#12](https://github.com/rangermix/TwitchDropsMiner/pull/12) · [#17](https://github.com/rangermix/TwitchDropsMiner/pull/17) · [#18](https://github.com/rangermix/TwitchDropsMiner/pull/18) · [#100](https://github.com/rangermix/TwitchDropsMiner/pull/100) · [#150](https://github.com/rangermix/TwitchDropsMiner/pull/150) |
<!-- contributors:end -->

</details>

## 📜 Credits

- Mod by [Murr (vtstv)](https://github.com/vtstv/TwitchDropsMinerMod)
- Upstream: [rangermix/TwitchDropsMiner](https://github.com/rangermix/TwitchDropsMiner)
- Original: [DevilXD/TwitchDropsMiner](https://github.com/DevilXD/TwitchDropsMiner)
- License: [MIT](LICENSE)
