# 🔔 Aura Bell: The Professional Smart Doorbell

> **Description:** Aura Bell is a serverless, secure, and multi-lingual smart doorbell system. Notifies you on Telegram and allows direct calls. Runs on Cloudflare Workers for $0 cost.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by Cloudflare](https://img.shields.io/badge/Cloudflare-Workers-orange.svg?logo=cloudflare)](https://workers.cloudflare.com/)

**English** | [עברית](./README.he.md)

<p align="center">
  <img src="assets/logo.png" alt="Aura Bell Logo" width="600" />
</p>

## ✨ New in Version 2.0 (Aura Bell)

| Feature | Description |
| :--- | :--- |
| 🌍 **Multi-lingual** | Full support for **5 languages**: English, Hebrew, Arabic, Russian, and French. |
| 📞 **Direct Call** | Guests can call you directly from the interface with a single tap. |
| 🚀 **Setup Wizard** | New `/setup` interface for easy initial configuration. |
| 🎨 **Modern UI** | Sleek, professional dark-mode interface with smooth animations. |

## 🤯 Why Aura Bell?

In the age of smart homes, physical doorbells are often noisy and limited. **Aura Bell** provides a professional, serverless solution that is smarter, quieter, and entirely free to run. It's the perfect blend of modern cloud architecture and user-centric design.

## 🚀 Quick Start

1.  **Clone & Deploy:**
    ```bash
    git clone https://github.com/Avielzi/dori-bell-serverless-template.git aura-bell
    cd aura-bell
    wrangler deploy
    ```
2.  **Configure:** Visit `your-worker-url.workers.dev/setup` to see the configuration guide.
3.  **Environment Variables:** Set your `TG_BOT_TOKEN`, `TG_CHAT_ID`, and `PHONE_NUMBER` in the Cloudflare Dashboard.

## ⚙️ Configuration

| Variable | Description | Example |
| :--- | :--- | :--- |
| `TG_BOT_TOKEN` | Telegram Bot API token | `12345:ABC...` |
| `TG_CHAT_ID` | Your Telegram Chat ID | `-100...` |
| `PHONE_NUMBER` | Your phone number for direct calls | `+97250...` |
| `FAMILY_NAME` | Displayed name | `Aura Bell Home` |

## 🎨 Customization

The system is controlled by a single `translations` and `CONFIG` object in `worker.js`. You can easily add more languages or change button icons.

---
*Aura Bell - Elevating your home entrance experience.*
