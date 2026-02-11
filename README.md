# 🔔 Aura Bell v2.0: The Professional Smart Doorbell

> **Aura Bell** is a serverless, multi-lingual, and secure smart doorbell system. It provides instant Telegram notifications, direct calling capabilities, and a sleek modern interface—all running for $0 on Cloudflare Workers.

---

## 🌍 Multi-lingual Support
Aura Bell is designed for a global audience with full support for:
- 🇮🇱 **Hebrew** (עברית)
- 🇺🇸 **English**
- 🇸🇦 **Arabic** (العربية)
- 🇷🇺 **Russian** (Русский)
- 🇫🇷 **French** (Français)

---

## ✨ New in Version 2.0
| Feature | Description |
| :--- | :--- |
| 📞 **Direct Call** | Guests can call the host directly from the browser with one tap. |
| 🚀 **Auto-Setup Script** | New `setup.py` script to configure everything without touching code. |
| 🌍 **RTL/LTR Support** | Seamless switching between Right-to-Left and Left-to-Right languages. |
| 🎨 **Premium UI** | Modern dark-mode design with smooth animations and a professional look. |
| 🛡️ **Bot Protection** | Powered by Cloudflare Turnstile for maximum security. |

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
   git clone https://github.com/Avielzi/dori-bell-serverless-template.git aura-bell
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

## 🖼️ UI Preview
*Aura Bell features a responsive, mobile-first design that adapts to any screen size and language preference.*

---

## 📄 Documentation
- [Hebrew Guide / מדריך בעברית](./README.he.md)
- [Roby's Simple Guide / המדריך של רובי](./GUIDE_FOR_ROBY.md)

---
*Aura Bell - Elevating your home entrance experience.*
