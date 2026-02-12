# Introducing Dori-Bell: The $0 Smart Doorbell That's Smart, Useless, and Now a Template!

We've all been there. You want a smart home, but you also want to prove you can build something entirely ridiculous with modern cloud infrastructure. Enter **Dori-Bell**, the serverless smart doorbell that runs 100% free on Cloudflare Workers.

When we first built Dori-Bell, our wives called it "Smart and useless at the same time." We call it **Innovation**. It replaces your noisy, dumb physical doorbell with a secure QR code that opens a web page, verifies you're not a bot with Cloudflare Turnstile, and sends an instant, rich notification to Telegram. It even has "Quiet Hours" because Dori needs her beauty sleep.

Today, we're thrilled to announce the Dori-Bell project is officially released as a **fully customizable template** on GitHub!

## The Over-Engineered Doorbell Just Got Flexible

The original Dori-Bell was hardcoded for "Wolt Delivery" and "Guests." But what if you need a button for "The Neighbor Who Always Asks for Sugar" or "The Cat Who Learned to Scan QR Codes"?

We've refactored the entire project to be controlled by a single, beautiful `CONFIG` object in `worker.js`.

> **Now, you can define any number of buttons, with custom labels, icons, and Telegram messages, all without touching the core logic.**

Want a button with a 🚨 icon that sends a message in all caps? Go for it. Want to change the family name displayed on the screen? It's a simple environment variable change. We've made the most over-engineered doorbell on the internet the easiest to customize.

### Why Serverless? Why Cloudflare?

Because we believe in the $0 smart home. By leveraging Cloudflare Workers' generous free tier, Dori-Bell can handle virtually unlimited rings without ever costing you a dime. It's fast, secure, and delightfully unnecessary.

Ready to embrace the "Smart, Over-Engineered, yet slightly useless but fun DIY" life?

**Check out the full repository and start customizing your Dori-Bell today!**

[**➡️ View the Dori-Bell Repository on GitHub**](https://github.com/your-username/dori-bell-serverless)
