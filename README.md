<p style="text-align:center;" align="center">
  <img align="center" src="./assets/logo.png" alt="TGS Downloader Bot" width="320px" height="320px"/>
</p>
<h1 align="center">📦 TGS Downloader Bot</h1>

<div align="center">

[![Telegram](https://img.shields.io/badge/Telegram-Demo-01CC1D?logo=telegram&style=flat)](https://t.me/tgs_emoji_downloader_bot)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg?logo=python&style=flat)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

<h4 align="center">Download Animated Stickers & Premium Custom Emojis as <code>.tgs</code> files 📥</h4>

<div align="center">
  - A Telegram bot that converts animated stickers / custom emojis to <b>.tgs</b> and can download entire packs as a <b>ZIP</b>. -
  <br/>
  <sup><sub>Fast downloads • Progress updates • Auto-cleanup • History tracking</sub></sup>
</div>

## 🎯 Features

- 🎭 **Animated Sticker → .tgs** — send an animated sticker and get the `.tgs` file back
- 😎 **Premium Custom Emoji → .tgs** — supports Telegram custom emoji entities (`custom_emoji`)
- 🔗 **Pack URL Detection** — paste `t.me/addstickers/<pack>` or `t.me/addemoji/<pack>`
- 📦 **Pack → ZIP** — downloads all animated items in the pack and returns a ZIP
- 📊 **Progress + ETA** — live progress bar while downloading packs
- 🧵 **Parallel Downloads** — controlled concurrency for faster pack downloads
- 🧹 **Auto Cleanup** — periodically removes old files from `downloads/`
- 🕘 **Download History** — `/history` shows recent downloads and lets users clear entries
- 🛡️ **Retry on Network Errors** — retries on `NetworkError` / `TimedOut` with backoff

## 🎬 Demo

> Add your own demo GIF/screenshot here (optional)

```text
1) Send an animated sticker ➜ bot replies with .tgs
2) Send a pack link ➜ tap Download ➜ receive ZIP
```

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Clone
# git clone <your-repo-url>
cd "tgs downloader"

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_TOKEN

# Run
python bot.py
```

### Option 2: Deploy to Cloud (Heroku/Render style)

This repo already includes:
- `Procfile`
- `runtime.txt`

Set the environment variable:
- `TELEGRAM_BOT_TOKEN`

Then deploy and run the worker.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | Telegram bot token from [@BotFather](https://t.me/BotFather) | - |

### Useful Settings (config.py)

| Setting | Description | Default |
|---|---|---|
| `DOWNLOADS_DIR` | Folder used for temporary downloads | `downloads` |
| `MAX_CONCURRENT_DOWNLOADS` | Max parallel sticker downloads when fetching packs | `5` |
| `CLEANUP_AGE_HOURS` | Remove downloads older than N hours | `1` |
| `CLEANUP_INTERVAL_HOURS` | Run cleanup job every N hours | `6` |
| `MIN_FREE_SPACE_MB` | Minimum required free space before pack downloads | `100` |

---

## 📖 Usage

### In Private Chat

**Download a single animated sticker**
1. Send an **animated** sticker
2. The bot replies with a `.tgs` file

**Download a premium custom emoji**
1. Send a message containing premium custom emojis
2. The bot detects `custom_emoji` entities and replies with `.tgs`

**Download a pack**
1. Send a pack URL:
   - `https://t.me/addstickers/<pack_name>`
   - `https://t.me/addemoji/<pack_name>`
2. Tap **Download**
3. Receive the ZIP containing all animated items

### All Commands

- `/start` — Start the bot + buttons
- `/help` — Usage instructions
- `/about` — About
- `/history` — Recent downloads

---

## 🛠 Tech Stack

- **Language**: Python
- **Framework**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Config**: `python-dotenv`

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Your Name**
- 🐦 Telegram: [@YourUsername](https://t.me/YourUsername)
- 🌐 GitHub: https://github.com/yourname

<div align="center">

**If you find this project useful, please consider giving it a ⭐!**

[🚀 Try the Bot](https://t.me/tgs_emoji_downloader_bot)

</div>
