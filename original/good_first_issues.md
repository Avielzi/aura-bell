# 💡 Good First Issues for Dori-Bell

Welcome to the Dori-Bell project! We've curated a list of issues that are perfect for first-time contributors to get familiar with the codebase, the Cloudflare Workers environment, and our unique brand of over-engineering.

These tasks are self-contained, have a clear scope, and are designed to be a gentle introduction to the project.

| ID | Title | Description | Skills Required |
| :--- | :--- | :--- | :--- |
| **#1** | **Implement a Dedicated "Thank You" Screen** | Currently, after a successful ring, the buttons are just disabled. Enhance the user experience by replacing the button container with a simple, friendly message like "✅ Host Notified! Please wait a moment." for 10 seconds before resetting the screen. | HTML, JavaScript (Frontend DOM manipulation) |
| **#2** | **Add a Simple Light/Dark Mode Toggle** | Introduce a new variable to the `CONFIG` object (e.g., `theme: 'dark'`) and add a small block of CSS in `worker.js` to define a light theme. The frontend should use this variable to apply the correct theme classes to the `<body>` tag. | JavaScript, CSS (Variables) |
| **#3** | **Translate Frontend Text to a New Language** | The frontend HTML contains hardcoded English strings (e.g., "Please solve the security check..."). Choose a language (e.g., Spanish, French, or Hebrew) and translate all user-facing text within the HTML template in `worker.js`. | HTML, Localization |
| **#4** | **Enhance Telegram Message with Local Time** | The Telegram notification currently uses `now.toISOString()`. Refactor the notification logic in `handleNotify` to use the `TIMEZONE_OFFSET` from the `CONFIG` object to calculate and display the user's local time (e.g., "Time: 10:30 PM IST") in the Telegram message for better context. | JavaScript (Date/Time manipulation) |
| **#5** | **Create a `CODE_OF_CONDUCT.md` File** | To foster a welcoming community, create a `CODE_OF_CONDUCT.md` file. We recommend adopting the [Contributor Covenant](https://www.contributor-covenant.org/) (Version 2.1 is standard). This is a simple copy-paste task. | Documentation, Community |

We encourage you to comment on the issue you'd like to work on to let others know you've claimed it! Happy coding!
