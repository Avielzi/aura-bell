# 🔔 Aura Bell v2.0: The Professional Smart Doorbell

> **Aura Bell** is a professional-grade, serverless, multi-lingual, and secure smart doorbell system. It provides instant Telegram notifications, direct calling capabilities, and a sleek modern interface—all running for $0 on Cloudflare Workers.

---

## 🌍 Multi-lingual Support
Aura Bell is designed for a global audience with full support for:
- 🇮🇱 **Hebrew** (עברית) - Full RTL support
- 🇺🇸 **English** - Modern LTR interface
- 🇸🇦 **Arabic** (العربية) - Full RTL support
- 🇷🇺 **Russian** (Русский)
- 🇫🇷 **French** (Français)

---

## ✨ Why Aura Bell? (Features)
| Feature | Description |
| :--- | :--- |
| 📞 **Direct Call** | Guests can call the host directly from the browser with one tap. No app required. |
| 🚀 **Auto-Setup Script** | New `setup.py` script to configure your **smart home** doorbell without touching code. |
| 🌍 **RTL/LTR Support** | Seamless switching between Right-to-Left and Left-to-Right languages. |
| 🎨 **Premium UI** | Modern **dark-mode** design with smooth animations and a professional look. |
| 🛡️ **Bot Protection** | Powered by **Cloudflare Turnstile** for maximum security and anti-spam. |
| 💰 **$0 Monthly Cost** | 100% **free to run** on Cloudflare Workers' generous free tier. |
| 📱 **Telegram Alerts** | Instant push notifications with custom icons and rich text formatting. |

---

## 🚀 Quick Installation (Choose your path)

### Option A: The Easy Way (For Everyone)
1. **Download** the project files.
2. **Run Setup:** Open your terminal and run:
   ```bash
   python3 setup.py
   ```
   *The script will guide you through the configuration step-by-step.*
3. **Deploy:** Run `wrangler deploy` or copy the content of `worker.js` to a new Cloudflare Worker.

### Option B: The Developer Way
1. **Clone & Install:**
   ```bash
   git clone https://github.com/Avielzi/aura-bell.git
   cd aura-bell
   npm install -g wrangler
   ```
2. **Configure:** Edit `wrangler.toml` or set environment variables in the Cloudflare Dashboard.
3. **Deploy:** `wrangler deploy`

---

## ⚙️ Configuration Variables
| Variable | Description |
| :--- | :--- |
| `TG_BOT_TOKEN` | Your Telegram Bot API token. |
| `TG_CHAT_ID` | Your Telegram Chat ID. |
| `PHONE_NUMBER` | Your phone number for direct calls. |
| `FAMILY_NAME` | The name displayed on the screen. |
| `TURNSTILE_SITE_KEY` | Cloudflare Turnstile Site Key. |

---

## 📄 Documentation
- [Hebrew Guide / מדריך בעברית](./README.he.md)
- [Roby's Simple Guide / המדריך של רובי](./GUIDE_FOR_ROBY.md)

---
*Aura Bell - The best serverless smart doorbell for home automation and security.*
