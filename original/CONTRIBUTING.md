# 🛎️ Contributing to Dori-Bell: The Over-Engineered Doorbell

First off, thank you for considering contributing to Dori-Bell! This project thrives on the spirit of "Smart, Over-Engineered, yet slightly useless but fun DIY," and we welcome all contributions, big or small.

Whether you're fixing a typo, adding a new feature, or suggesting a completely absurd integration, your involvement is what makes this serverless smart doorbell truly special.

## 🤝 How to Contribute

We follow a standard GitHub workflow. Please ensure you have read the [README.md](README.md) and understand the project's core architecture (Cloudflare Workers, Telegram Bot API, Turnstile).

### 1. Reporting Bugs

If you find a bug, please check the existing [Issues](https://github.com/Aviel.AI/dori-bell-serverless/issues) to see if it has already been reported. If not, open a new issue and include:

*   A clear, descriptive title.
*   The steps to reproduce the bug.
*   The expected behavior vs. the actual behavior.
*   Any relevant error messages or logs.

### 2. Suggesting Enhancements

We love absurd and over-engineered ideas! If you have a suggestion for a new feature, integration, or even a better way to structure the code, please open an issue with the label `enhancement`.

Examples of welcome enhancements:
*   **New Integrations:** Slack, Discord, or even a physical light-up sign.
*   **Frontend Improvements:** Better CSS, animations, or accessibility features.
*   **Localization:** Translations for the frontend HTML (beyond the current English/Hebrew README).

### 3. Submitting Code Changes (Pull Requests)

We use the "fork and pull request" model.

1.  **Fork** the repository.
2.  **Clone** your fork locally:
    \`\`\`bash
    git clone https://github.com/Aviel.AI/dori-bell-serverless.git
    cd dori-bell-serverless
    \`\`\`
3.  **Create a new branch** for your feature or fix:
    \`\`\`bash
    git checkout -b feature/my-awesome-feature
    # or
    git checkout -b fix/bug-in-quiet-hours
    \`\`\`
4.  **Make your changes.** Remember that the core logic is in `worker.js`.
5.  **Test your changes** locally using `wrangler dev`.
6.  **Commit your changes** with a clear, descriptive commit message.
7.  **Push** your branch to your fork.
8.  **Open a Pull Request** (PR) against the `main` branch of the original repository.

#### Pull Request Guidelines

*   **One feature/fix per PR:** Keep your changes focused.
*   **Code Style:** Follow the existing JavaScript style in `worker.js`.
*   **Documentation:** If you add a new configuration option or feature, please update the `README.md` accordingly (both English and Hebrew sections).
*   **Wrangler:** Ensure your changes work with the latest version of Cloudflare's Wrangler CLI.

## 💡 DevRel Focus: Why Contribute?

Contributing to Dori-Bell is a fantastic way to:

*   **Learn Cloudflare Workers:** Get hands-on experience with serverless development, KV storage (future feature?), and Cloudflare's ecosystem.
*   **Master the Telegram Bot API:** Deepen your understanding of rich push notifications and Markdown formatting in Telegram.
*   **Build Your Portfolio:** Showcase your ability to contribute to a fun, modern, and highly visible open-source project.
*   **Join the Fun:** Help us make this the most delightfully unnecessary smart home project on the internet!

We look forward to seeing your contributions! Thank you for helping us keep Dori-Bell over-engineered.
