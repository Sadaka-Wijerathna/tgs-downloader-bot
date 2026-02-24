<p style="text-align:center;" align="center">
  <img align="center" src="./assets/logo.png" alt="TGS Downloader Bot" width="320px" height="320px"/>
</p>
<h1 align="center">📦 TGS Emoji Downloader Bot</h1>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&style=flat)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-01CC1D?logo=telegram&style=flat)](https://t.me/SadadakaWijerathna)

</div>

<h4 align="center">Download Animated Stickers & Custom Emojis in TGS Format! 🚀✨</h4>

<div align="center">
  - High-performance Telegram bot to convert animated content into downloadable TGS files -
  <br/>
  <sup><sub>Built with Python and python-telegram-bot ツ</sub></sup>
</div>

## 🎯 Features

- 🖼️ **Single Sticker Conversion** - Instantly convert any animated sticker to a `.tgs` file.
- 🌟 **Custom Emoji Support** - Download premium animated custom emojis as `.tgs`.
- 📦 **Bulk Pack Download** - Download entire emoji or sticker packs as a single ZIP archive.
- 📊 **Real-time Progress** - Visual progress bars and ETA for large pack downloads.
- 🗜️ **Optimized Packaging** - Efficient ZIP compression and file naming.
- 💾 **Disk Management** - Smart cleanup of old files and disk space monitoring.
- ☁️ **Cloud Ready** - Easy deployment to Railway, Heroku, and generic VPS.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Option 1: Local Setup

```bash
# Clone the repository
git clone https://github.com/Sadaka-Wijerathna/tgs-downloader-bot.git
cd tgs-downloader-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your TELEGRAM_BOT_TOKEN
```

### Option 2: Running the Bot

```bash
python bot.py
```

## ☁️ Deploy to Cloud

### 🚀 One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/nixpacks?referrer=https://github.com/Sadaka-Wijerathna/tgs-downloader-bot)
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy?template=https://github.com/Sadaka-Wijerathna/tgs-downloader-bot)

### 🔨 Manual Deployment (Generic VPS)

1. Clone the repo and install dependencies (as shown in Quick Start).
2. Set up a process manager like **PM2** or a **Systemd** service to keep the bot running.
3. Ensure the `downloads/` directory has write permissions.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | Your bot token from [@BotFather](https://t.me/BotFather) |
| `DOWNLOADS_DIR` | ❌ No | Directory where files are stored (default: `downloads`) |
| `CLEANUP_AGE_HOURS` | ❌ No | Automatic deletion threshold (default: `1 hour`) |

---

## 📖 Usage

### Private Chat

1. **Send an animated sticker** to get the TGS file instantly.
2. **Send an animated custom emoji** to get its TGS file.
3. **Send a pack URL** to download the whole pack:
   - `t.me/addemoji/PackName`
   - `t.me/addstickers/PackName`

### Bot Commands

- `/start` - Welcome message & feature overview
- `/help` - In-depth guide on how to use the bot
- `/about` - Technical details and developer info
- `/history` - View your recent bulk download history

---

## 🔬 How Does It Work?

1. **Fetch**: The bot uses the Telegram API to retrieve the file path for animated stickers/emojis.
2. **Download**: Content is fetched as `.tgs` (Gzipped JSON).
3. **Process**: 
   - For single files, it renames and delivers them.
   - For packs, it fetches all stickers in parallel using `asyncio.Semaphore` to stay within API limits.
4. **Deliver**: Files are zipped and sent to the user, with temporary storage automatically cleaned up.

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Concurrency**: `asyncio` for parallel downloads
- **Storage**: JSON-based history management

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👨‍💻 Developer

**Sadadaka Wijerathna**
- 🐦 Telegram: [@SadadakaWijerathna](https://t.me/SadadakaWijerathna)

---

<div align="center">
  <b>If you find this project useful, please consider giving it a ⭐!</b>
</div>
