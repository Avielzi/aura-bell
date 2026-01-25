# 🛎️ Dori-Bell: The $0 Smart Doorbell

> **Description:** The $0 Smart Doorbell. Serverless, secure, and notifies you on Telegram. Runs on Cloudflare Workers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by Cloudflare](https://img.shields.io/badge/Cloudflare-Workers-orange.svg?logo=cloudflare)](https://workers.cloudflare.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/your-username/dori-bell-serverless/pulls)


<p align="center">
  <img src="assets/logo.png" alt="Dori-Bell Logo" width="600" />
</p>

## 🤯 Why does this exist?

In the age of smart homes, I realized my physical doorbell was a single point of failure—a dumb, noisy box that couldn't tell the difference between a delivery driver and a persistent salesman. I needed a solution that was smarter, quieter, and, most importantly, free.

**Dori-Bell** is the result: an over-engineered, 100% serverless, QR-code-activated smart doorbell that runs entirely on Cloudflare Workers. It's the perfect blend of modern cloud architecture and delightful DIY absurdity.

> **Quote:** "My wife called it 'Smart and useless at the same time'. I call it Innovation. (Credit: Aviel.AI)"

## ✨ Features

| Icon | Feature | Description |
| :--- | :--- | :--- |
| 🚀 | **Serverless & $0 Cost** | Runs entirely on Cloudflare Workers, leveraging the free tier for virtually unlimited rings. No servers to maintain, no monthly fees. |
| 🛡️ | **Bot Protection** | Integrated with **Cloudflare Turnstile** to ensure only humans (or very smart bots) can ring the bell. |
| 🎨 | **Customizable Buttons** | Define any number of buttons (e.g., **Delivery**, **Guest**, **Urgent**) with custom labels, icons, and Telegram messages via a simple configuration object. The examples are fully customizable. |
| 🌙 | **Quiet Hours** | "Dori" sleeps at night. Configure a time range where notifications are automatically suppressed. |
| 📱 | **Telegram Integration** | Instant, rich push notifications sent directly to your Telegram chat via the Bot API. |

## 🖼️ Demo & Screenshots

| Main Screen (Mobile View) | Telegram Notification |
| :---: | :---: |
| <img src="assets/mobile_mockup.png" alt="Mobile Screen Mockup" width="300" /> | <img src="assets/telegram_mockup.png" alt="Telegram Notification Mockup" width="500" /> |

## 🚀 Quick Start (Installation)

### Prerequisites

1.  A **Cloudflare** account.
2.  A **Telegram Bot** and your **Chat ID**.
3.  A **Cloudflare Turnstile** Site and Secret Key.

### Option A: The Hacker Way (Using Wrangler CLI)

This is the recommended path for developers.

1.  **Clone the repository:**
    \`\`\`bash
    git clone https://github.com/your-username/dori-bell-serverless-template.git
    cd dori-bell-serverless-template
    \`\`\`

2.  **Install Wrangler:**
    \`\`\`bash
    npm install -g wrangler
    wrangler login
    \`\`\`

3.  **Configure Environment Variables:**
    Copy the `.env.example` file to `.env` and fill in your secrets.
    \`\`\`bash
    cp .env.example .env
    # Edit .env with your secrets
    \`\`\`
    The `wrangler.toml` file is configured to read secrets from your environment or the Cloudflare dashboard, ensuring no secrets are committed to the repository.

4.  **Deploy:**
    \`\`\`bash
    wrangler deploy
    \`\`\`

### Option B: The Easy Way (Manual Setup)

1.  Go to your Cloudflare Dashboard -> Workers & Pages -> Create Application -> Create Worker.
2.  Name your Worker \`dori-bell-serverless\`.
3.  Copy the entire content of \`worker.js\` and paste it into the Worker editor.
4.  Go to the **Settings** tab -> **Variables** -> **Environment Variables** and add the required variables (see Configuration below).
5.  Click **Save and Deploy**.

## ⚙️ Configuration

The Worker relies on the following Environment Variables (set in a local `.env` file for development, or the Cloudflare Dashboard for deployment):

| Variable | Description | Example | Required |
| :--- | :--- | :--- | :--- |
| \`TG_BOT_TOKEN\` | Your Telegram Bot's API token. | \`123456:ABC-DEF123456\` | **Yes** |
| \`TG_CHAT_ID\` | The Chat ID where the notifications should be sent. | \`-123456789\` | **Yes** |
| \`TURNSTILE_SITE_KEY\` | The **Site Key** for the Turnstile widget (used in the HTML). | \`0x4AAAAAA...A\` | **Yes** |
| \`TURNSTILE_SECRET\` | The **Secret Key** for the Turnstile API verification (used in the Worker). | \`1x0AAAAAA...A\` | **Yes** |
| \`FAMILY_NAME\` | The name displayed on the doorbell screen. | \`Cohen-Ziso Family\` | No (Default: \`The Innovation Lab\`) |
| \`TIMEZONE_OFFSET\` | Your local timezone offset from UTC in hours (e.g., \`2\` for Israel). | \`2\` | No (Default: \`2\`) |
| \`QUIET_HOURS_START\` | Hour (0-23) to start suppressing notifications. Configured in \`worker.js\`'s \`CONFIG\` object. | \`22\` (10 PM) | No (Default: \`22\`) |
| \`QUIET_HOURS_END\` | Hour (0-23) to resume notifications. Configured in \`worker.js\`'s \`CONFIG\` object. | \`7\` (7 AM) | No (Default: \`7\`) |

## 🎨 Customization

The Dori-Bell worker is now a fully customizable template controlled by a single \`CONFIG\` object at the top of \`worker.js\`.

### 1. Defining Buttons

The core of the customization is the \`CONFIG.buttons\` array. You can add, remove, or modify any button.

\`\`\`javascript
const CONFIG = {
  // ...
  buttons: [
    {
      id: "delivery", // Unique ID for the button
      label: "Delivery (Example: Wolt)", // Text displayed on the button
      icon: "🛵", // Emoji, SVG string, or Image URL
      message: "🛵 *Delivery Alert!* Go get the food." // Telegram message (supports Markdown) - This is a customizable example.
    },
    
  ],
  // ...
};
\`\`\`

*   **ID:** Must be a unique, lowercase string.
*   **Icon:** Can be a Unicode emoji (recommended for simplicity), a Base64-encoded SVG, or a link to an external image.
*   **Message:** The text sent to Telegram. Use Markdown for rich formatting.

### 2. Quiet Hours and Family Name

You can also customize the displayed name and the quiet hours directly in the \`CONFIG\` object, which pulls its values from the environment variables:

\`\`\`javascript
const CONFIG = {
  familyName: env.FAMILY_NAME || "The Innovation Lab", // Displayed on the screen
  // ...
  quietHours: {
    start: parseInt(env.QUIET_HOURS_START) || 22,
    end: parseInt(env.QUIET_HOURS_END) || 7,
    timezoneOffset: parseInt(env.TIMEZONE_OFFSET) || 2
  }
};
\`\`\`
