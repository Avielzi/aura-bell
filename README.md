# 🛎️ Dori-Bell: The $0 Smart Doorbell Template
[![GitHub license](https://img.shields.io/github/license/Avielzi/Dori-Bell)](https://github.com/Avielzi/Dori-Bell/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Avielzi/Dori-Bell)](https://github.com/Avielzi/Dori-Bell/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Avielzi/Dori-Bell)](https://github.com/Avielzi/Dori-Bell/network)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-F38020?logo=cloudflare&logoColor=white)](https://workers.cloudflare.com/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)

> **Dori-Bell** is a professional-grade, serverless smart doorbell system that runs **100% free** on Cloudflare Workers. It replaces traditional hardware with a secure QR code, providing instant Telegram notifications and a sleek, multi-lingual interface.

---

## 🚀 Why Dori-Bell?
*   **$0 Monthly Cost:** Runs entirely on Cloudflare Workers' generous free tier.
*   **Serverless & Secure:** No servers to manage. Powered by Cloudflare Turnstile for bot protection.
*   **Instant Notifications:** Get rich Telegram alerts with custom icons and messages.
*   **Multi-lingual & RTL:** Full support for 🇮🇱 **Hebrew**, 🇺🇸 **English**, 🇸🇦 **Arabic**, 🇷🇺 **Russian**, and 🇫🇷 **French**.
*   **Direct Call:** Guests can call you directly from the browser with a single tap.
*   **Ultra-Customizable:** Define your own buttons, icons, and logic via a simple config.

---

## ✨ Features at a Glance
| Feature | Description |
| :--- | :--- |
| 📞 **Direct Call** | Tap-to-call functionality for immediate contact. |
| 🚀 **Auto-Setup** | Includes a `setup.py` script for painless configuration. |
| 🌍 **Global UI** | Seamlessly switches between RTL (Hebrew/Arabic) and LTR languages. |
| 🎨 **Premium Design** | Modern dark-mode UI with smooth animations and mobile-first responsiveness. |
| 🛡️ **Privacy First** | You own the data. No third-party tracking or expensive subscriptions. |

---

## 📸 UI Preview
![Mobile Mockup](https://private-us-east-1.manuscdn.com/sessionFile/oKAC8MwL6Sd8ZPtGQQDxV5/sandbox/QPIlAC6OM7HhpX9WJWmDOV-images_1770825505760_na1fn_L2hvbWUvdWJ1bnR1L3JlcG8vYXNzZXRzL21vYmlsZV9tb2NrdXA.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvb0tBQzhNd0w2U2Q4WlB0R1FRRHhWNS9zYW5kYm94L1FQSWxBQzZPTTdIaHBYOVdKV21ET1YtaW1hZ2VzXzE3NzA4MjU1MDU3NjBfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzSmxjRzh2WW1sc1pWOXRiMk5yZFhBLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=PRXm6OGJnaW385CJWl1BWm4ivTWHgNERy~txSJKmHfm3lG0SAgaqZFC6w7Ga6MmIXW4mvjP2-ISchD891Fpma~4-brNGAXvOeESNfQKPGgWciK9IpgBBKWmvwZNtk952r1wTvkeMKMRJdoFwehTjmZem9gVB8gtTFma7BA68kyhCT3y6Sm09VbTlteH05SRU2acDmLCC9jOayLghcOkZHEmGR4EVWt~TlsK112xFsjGVw~XVEbYCKxb5cbMFtz9FfJ5M64SuTrzY9zo96B~1R11PlLb638EQJjXlWd4j2SFv7fVMSpEjBDFAGYClcCytyyh3AyL0-wuS7hhNTHnGag__)
*Modern, responsive, and ready for your front door.*

---

## 🛠️ Quick Start (Deploy in 5 Minutes)

### Option A: The Easy Way (Recommended)
1. **Clone the repo:**
   ```bash
   git clone https://github.com/Avielzi/Dori-Bell.git
   cd Dori-Bell
   ```
2. **Run the Setup Script:**
   ```bash
   python3 setup.py
   ```
   *Follow the interactive prompts to configure your bot token, chat ID, and preferences.*
3. **Deploy:** Run `wrangler deploy` to push your doorbell to the cloud!

### Option B: Manual Deployment
1. Copy the content of `worker.js`.
2. Create a new Worker in your [Cloudflare Dashboard](https://dash.cloudflare.com/).
3. Paste the code and set your environment variables (see table below).

---

## ⚙️ Configuration
| Variable | Description |
| :--- | :--- |
| `TG_BOT_TOKEN` | Your Telegram Bot API token from @BotFather. |
| `TG_CHAT_ID` | Your Telegram Chat ID (use @userinfobot to find it). |
| `PHONE_NUMBER` | Your phone number for the "Direct Call" feature. |
| `FAMILY_NAME` | The name displayed on your doorbell's home screen. |
| `TURNSTILE_SITE_KEY` | Your Cloudflare Turnstile Site Key for security. |

---

## 📄 Documentation & Guides
- 🇮🇱 [מדריך מלא בעברית (Hebrew Guide)](./README.he.md)
- 🛠️ [Detailed Installation Guide](./GUIDE.he.md)
- 🤖 [The "Roby" Guide (Simplified)](./GUIDE_FOR_ROBY.md)

---

## 🤝 Contributing
Contributions are welcome! Whether it's adding a new language, improving the UI, or fixing a bug, feel free to open a Pull Request. Check out [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

---
*Built with ❤️ for the DIY and Open Source community by [Aviel.AI](https://github.com/Avielzi).*
