/**
 * Dori-Bell: The $0 Smart Doorbell (Template Version)
 * Serverless, secure, and fully customizable.
 */

export default {
  async fetch(request, env, ctx) {
    // --- USER CONFIGURATION ---
    const CONFIG = {
      familyName: env.FAMILY_NAME || "The Innovation Lab",
      buttons: [
        {
          id: "delivery",
          label: "Wolt / Delivery",
          icon: "🛵", // Can be Emoji, SVG string, or Image URL
          message: "🛵 *Delivery Alert!* Food or package at the door."
        },
        {
          id: "guest",
          label: "Guest / Friend",
          icon: "👤",
          message: "🔔 *Ding Dong!* A guest is waiting for you."
        },
        {
          id: "urgent",
          label: "Urgent",
          icon: "🚨",
          message: "🚨 *URGENT!* Someone needs immediate attention at the door."
        }
      ],
      quietHours: {
        start: parseInt(env.QUIET_HOURS_START) || 22,
        end: parseInt(env.QUIET_HOURS_END) || 7,
        timezoneOffset: parseInt(env.TIMEZONE_OFFSET) || 2
      }
    };
    // --------------------------

    const url = new URL(request.url);

    // Handle Telegram Notification Request
    if (request.method === "POST" && url.pathname === "/notify") {
      return handleNotify(request, env, CONFIG);
    }

    // Serve Frontend
    return serveFrontend(env, CONFIG);
  },
};

/**
 * Handle Notification Logic
 */
async function handleNotify(request, env, CONFIG) {
  try {
    const { type, token } = await request.json();

    // 1. Validate Turnstile Token
    if (env.TURNSTILE_SECRET) {
      const formData = new FormData();
      formData.append('secret', env.TURNSTILE_SECRET);
      formData.append('response', token);

      const result = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
        body: formData,
        method: 'POST',
      });

      const outcome = await result.json();
      if (!outcome.success) {
        return new Response(JSON.stringify({ error: "Invalid bot protection token" }), { status: 403 });
      }
    }

    // 2. Check Quiet Hours
    const now = new Date();
    const hour = (now.getUTCHours() + CONFIG.quietHours.timezoneOffset + 24) % 24;
    const { start, end } = CONFIG.quietHours;

    const isQuiet = end > start 
      ? (hour >= start && hour < end)
      : (hour >= start || hour < end);

    if (isQuiet) {
      return new Response(JSON.stringify({ message: "Shhh... Dori is sleeping. Notification suppressed." }), { status: 200 });
    }

    // 3. Find Button Config
    const button = CONFIG.buttons.find(b => b.id === type);
    if (!button) {
      return new Response(JSON.stringify({ error: "Invalid notification type" }), { status: 400 });
    }

    // 4. Send Telegram Message
    const message = `${button.message}\n\n_Time: ${now.toLocaleString()}_`;
    
    const tgUrl = `https://api.telegram.org/bot${env.TG_BOT_TOKEN}/sendMessage`;
    const res = await fetch(tgUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: env.TG_CHAT_ID,
        text: message,
        parse_mode: 'Markdown',
      }),
    });

    if (!res.ok) {
        const errorData = await res.json();
        throw new Error(`Telegram API Error: ${errorData.description}`);
    }

    return new Response(JSON.stringify({ success: true }), { status: 200 });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}

/**
 * Serve HTML/JS Frontend
 */
function serveFrontend(env, CONFIG) {
  const buttonsHtml = CONFIG.buttons.map(btn => `
    <button id="btn-${btn.id}" class="btn" onclick="ring('${btn.id}')" disabled>
        <span class="icon">${btn.icon}</span>
        <span class="label">${btn.label}</span>
    </button>
  `).join('');

  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${CONFIG.familyName} | Dori-Bell</title>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <style>
        :root {
            --primary: #f37021;
            --bg: #121212;
            --card: #1e1e1e;
            --text: #ffffff;
            --accent: #00c2e8;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: var(--card);
            padding: 2.5rem 2rem;
            border-radius: 24px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            text-align: center;
            max-width: 420px;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .logo {
            font-size: 4.5rem;
            margin-bottom: 1.5rem;
            filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
        }
        h1 { margin: 0 0 0.5rem 0; font-weight: 800; letter-spacing: -0.5px; }
        p { color: #888; margin-bottom: 2.5rem; line-height: 1.5; }
        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 1.2rem;
            margin: 12px 0;
            border: none;
            border-radius: 16px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255,255,255,0.05);
            color: white;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .btn:active { transform: scale(0.97); }
        .btn:hover:not(:disabled) {
            background: rgba(255,255,255,0.1);
            border-color: var(--accent);
        }
        .btn .icon { margin-right: 12px; font-size: 1.4rem; }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; }
        
        #status { 
            margin-top: 1.5rem; 
            font-size: 0.95rem; 
            font-weight: 500;
            min-height: 1.5em;
        }
        .cf-turnstile { margin: 25px 0; display: flex; justify-content: center; }
        
        .footer {
            margin-top: 2rem;
            font-size: 0.75rem;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🛎️</div>
        <h1>${CONFIG.familyName}</h1>
        <p>Please solve the security check to ring the doorbell.</p>
        
        <div class="cf-turnstile" data-sitekey="${env.TURNSTILE_SITE_KEY || ''}"></div>

        <div id="button-container">
            ${buttonsHtml}
        </div>
        
        <div id="status"></div>
        
        <div class="footer">Powered by Dori-Bell Serverless</div>
    </div>

    <script>
        function checkTurnstile() {
            const token = turnstile.getResponse();
            if (token) {
                document.querySelectorAll('.btn').forEach(b => b.disabled = false);
            }
        }
        setInterval(checkTurnstile, 1000);

        async function ring(type) {
            const status = document.getElementById('status');
            const token = turnstile.getResponse();
            
            if (!token) {
                status.innerText = "⚠️ Please complete the security check.";
                return;
            }

            status.innerHTML = "⏳ <span style='color: var(--accent)'>Ringing the bell...</span>";
            
            try {
                const res = await fetch('/notify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, token })
                });
                
                const data = await res.json();
                if (res.ok) {
                    status.innerHTML = "✅ <span style='color: #4ade80'>Host notified! Please wait.</span>";
                    document.querySelectorAll('.btn').forEach(b => b.disabled = true);
                } else {
                    status.innerHTML = "❌ <span style='color: #f87171'>Error: " + (data.message || data.error) + "</span>";
                }
            } catch (e) {
                status.innerHTML = "❌ <span style='color: #f87171'>Connection failed.</span>";
            }
        }
    </script>
</body>
</html>
  `;
  return new Response(html, {
    headers: { "Content-Type": "text/html;charset=UTF-8" },
  });
}
