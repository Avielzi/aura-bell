/**
 * Dori-Bell: The Professional Smart Doorbell
 * Serverless, secure, and multi-lingual.
 */

const translations = {
  en: {
    title: "Dori-Bell",
    subtitle: "Smart Access System",
    securityCheck: "Please solve the security check to ring the doorbell.",
    ringing: "Ringing the bell...",
    notified: "Host notified! Please wait.",
    error: "Error: ",
    connFailed: "Connection failed.",
    callHost: "Call Host",
    setupTitle: "Dori-Bell Setup",
    familyName: "Family Name",
    tgToken: "Telegram Bot Token",
    tgChatId: "Telegram Chat ID",
    save: "Save Configuration",
    delivery: "Delivery",
    guest: "Guest",
    urgent: "Urgent",
    deliveryMsg: "🛵 *Delivery Alert!* Food or package at the door.",
    guestMsg: "🔔 *Ding Dong!* A guest is waiting for you.",
    urgentMsg: "🚨 *URGENT!* Someone needs immediate attention at the door."
  },
  he: {
    title: "Dori-Bell",
    subtitle: "מערכת גישה חכמה",
    securityCheck: "אנא עברו את בדיקת האבטחה כדי לצלצל בפעמון.",
    ringing: "מצלצל בפעמון...",
    notified: "המארח קיבל הודעה! נא להמתין.",
    error: "שגיאה: ",
    connFailed: "התחברות נכשלה.",
    callHost: "התקשר למארח",
    setupTitle: "הגדרת Dori-Bell",
    familyName: "שם המשפחה",
    tgToken: "טוקן בוט טלגרם",
    tgChatId: "מזהה צ'אט טלגרם",
    save: "שמור הגדרות",
    delivery: "משלוח",
    guest: "אורח",
    urgent: "דחוף",
    deliveryMsg: "🛵 *התראת משלוח!* אוכל או חבילה בדלת.",
    guestMsg: "🔔 *דינג דונג!* אורח ממתין לך.",
    urgentMsg: "🚨 *דחוף!* מישהו זקוק לתשומת לב מיידית בדלת."
  },
  ar: {
    title: "Dori-Bell",
    subtitle: "نظام الوصول الذكي",
    securityCheck: "يرجى حل التحقق الأمني لقرع الجرس.",
    ringing: "يرن الجرس...",
    notified: "تم إخطار المضيف! يرجى الانتظار.",
    error: "خطأ: ",
    connFailed: "فشل الاتصال.",
    callHost: "اتصل بالمضيف",
    setupTitle: "إعداد Dori-Bell",
    familyName: "اسم العائلة",
    tgToken: "رمز بوت تلغرام",
    tgChatId: "معرف دردشة تلغرام",
    save: "حفظ الإعدادات",
    delivery: "توصيل",
    guest: "ضيف",
    urgent: "عاجل",
    deliveryMsg: "🛵 *تنبيه توصيل!* طعام أو طرد عند الباب.",
    guestMsg: "🔔 *دينغ دونغ!* ضيف ينتظرك.",
    urgentMsg: "🚨 *עاجל!* شخص ما يحتاج إلى اهتمام فوري عند الباب."
  },
  ru: {
    title: "Dori-Bell",
    subtitle: "Умная система доступа",
    securityCheck: "Пожалуйста, пройдите проверку безопасности, чтобы позвонить в звонок.",
    ringing: "Звоним в звонок...",
    notified: "Хозяин уведомлен! Пожалуйста, подождите.",
    error: "Ошибка: ",
    connFailed: "Ошибка подключения.",
    callHost: "Позвонить хозяину",
    setupTitle: "Настройка Dori-Bell",
    familyName: "Фамилия",
    tgToken: "Токен бота Telegram",
    tgChatId: "ID чата Telegram",
    save: "Сохранить настройки",
    delivery: "Доставка",
    guest: "Гость",
    urgent: "Срочно",
    deliveryMsg: "🛵 *Оповещение о доставке!* Еда или посылка у двери.",
    guestMsg: "🔔 *Динь-дон!* Вас ждет гость.",
    urgentMsg: "🚨 *СРОЧНО!* Кому-то требуется немедленное внимание у двери."
  },
  fr: {
    title: "Dori-Bell",
    subtitle: "Système d'Accès Intelligent",
    securityCheck: "Veuillez résoudre le contrôle de sécurité pour sonner.",
    ringing: "Appel en cours...",
    notified: "Hôte prévenu ! Veuillez patienter.",
    error: "Erreur : ",
    connFailed: "Échec de la connexion.",
    callHost: "Appeler l'hôte",
    setupTitle: "Configuration Dori-Bell",
    familyName: "Nom de famille",
    tgToken: "Jeton du bot Telegram",
    tgChatId: "ID du chat Telegram",
    save: "Enregistrer la configuration",
    delivery: "Livraison",
    guest: "Invité",
    urgent: "Urgent",
    deliveryMsg: "🛵 *Alerte Livraison !* Nourriture ou colis à la porte.",
    guestMsg: "🔔 *Ding Dong !* Un invité vous attend.",
    urgentMsg: "🚨 *URGENT !* Quelqu'un a besoin d'une attention immédiate à la porte."
  }
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle Setup/Config (Simplified for Template - usually uses KV or D1)
    if (url.pathname === "/setup") {
        return serveSetup(env);
    }

    const CONFIG = {
      familyName: env.FAMILY_NAME || "Dori-Bell Home",
      phone: env.PHONE_NUMBER || "", // Added for direct call
      buttons: [
        { id: "delivery", icon: "🛵" },
        { id: "guest", icon: "👤" },
        { id: "urgent", icon: "🚨" }
      ],
      quietHours: {
        start: parseInt(env.QUIET_HOURS_START) || 22,
        end: parseInt(env.QUIET_HOURS_END) || 7,
        timezoneOffset: parseInt(env.TIMEZONE_OFFSET) || 2
      }
    };

    if (request.method === "POST" && url.pathname === "/notify") {
      return handleNotify(request, env, CONFIG);
    }

    return serveFrontend(env, CONFIG);
  },
};

async function handleNotify(request, env, CONFIG) {
  try {
    const { type, token, lang } = await request.json();
    const t = translations[lang] || translations.en;

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
    const isQuiet = end > start ? (hour >= start && hour < end) : (hour >= start || hour < end);

    if (isQuiet) {
      return new Response(JSON.stringify({ message: "Quiet hours active. Notification suppressed." }), { status: 200 });
    }

    // 3. Send Telegram Message
    const msgKey = type + "Msg";
    const message = (t[msgKey] || t.guestMsg) + `\n\n_Time: ${now.toLocaleString()}_`;
    
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

function serveFrontend(env, CONFIG) {
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
            --primary: #00c2e8;
            --bg: #0f172a;
            --card: #1e293b;
            --text: #f8fafc;
            --accent: #38bdf8;
        }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
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
            padding: 3rem 2rem;
            border-radius: 32px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            text-align: center;
            max-width: 400px;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .logo {
            width: 120px;
            height: 120px;
            margin: 0 auto 1.5rem;
            animation: pulse 2s infinite;
            display: block;
        }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
        h1 { margin: 0; font-size: 2rem; font-weight: 800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #94a3b8; margin-bottom: 2rem; font-size: 1rem; }
        .lang-selector { margin-bottom: 1.5rem; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
        .lang-btn { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 4px 10px; border-radius: 8px; cursor: pointer; font-size: 0.8rem; }
        .lang-btn.active { background: var(--primary); border-color: var(--primary); }
        .btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 1.2rem;
            margin: 12px 0;
            border: none;
            border-radius: 20px;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(255,255,255,0.03);
            color: white;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .btn:hover:not(:disabled) { background: rgba(255,255,255,0.1); border-color: var(--accent); transform: translateY(-2px); }
        .btn-call { background: linear-gradient(135deg, #0ea5e9, #2563eb); border: none; margin-top: 20px; }
        .btn .icon { margin-right: 12px; font-size: 1.5rem; }
        .btn:disabled { opacity: 0.3; cursor: not-allowed; }
        #status { margin-top: 1.5rem; font-weight: 500; min-height: 1.5em; }
        .footer { margin-top: 2.5rem; font-size: 0.8rem; color: #475569; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663282152489/UNpfETksVmNMDxrQ.png" alt="Aura Bell Logo" class="logo">
        <h1 id="ui-title">Dori-Bell</h1>
        <div class="subtitle" id="ui-subtitle">Smart Access System</div>
        
        <div class="lang-selector">
            <button class="lang-btn active" onclick="setLang('en')">EN</button>
            <button class="lang-btn" onclick="setLang('he')">HE</button>
            <button class="lang-btn" onclick="setLang('ar')">AR</button>
            <button class="lang-btn" onclick="setLang('ru')">RU</button>
            <button class="lang-btn" onclick="setLang('fr')">FR</button>
        </div>

        <p id="ui-security">${translations.en.securityCheck}</p>
        
        <div class="cf-turnstile" data-sitekey="${env.TURNSTILE_SITE_KEY || ''}" data-callback="onTurnstileSuccess"></div>

        <div id="button-container">
            <button id="btn-delivery" class="btn" onclick="ring('delivery')" disabled>
                <span class="icon">🛵</span> <span class="label" id="ui-delivery">Delivery</span>
            </button>
            <button id="btn-guest" class="btn" onclick="ring('guest')" disabled>
                <span class="icon">👤</span> <span class="label" id="ui-guest">Guest</span>
            </button>
            <button id="btn-urgent" class="btn" onclick="ring('urgent')" disabled>
                <span class="icon">🚨</span> <span class="label" id="ui-urgent">Urgent</span>
            </button>
            ${CONFIG.phone ? `
            <button class="btn btn-call" onclick="window.location.href='tel:${CONFIG.phone}'">
                <span class="icon">📞</span> <span id="ui-call">Call Host</span>
            </button>` : ''}
        </div>
        
        <div id="status"></div>
        <div class="footer">AURA BELL &copy; 2026</div>
    </div>

    <script>
        const translations = ${JSON.stringify(translations)};
        let currentLang = 'en';

        function setLang(lang) {
            currentLang = lang;
            const t = translations[lang];
            document.getElementById('ui-title').innerText = t.title;
            document.getElementById('ui-subtitle').innerText = t.subtitle;
            document.getElementById('ui-security').innerText = t.securityCheck;
            document.getElementById('ui-delivery').innerText = t.delivery;
            document.getElementById('ui-guest').innerText = t.guest;
            document.getElementById('ui-urgent').innerText = t.urgent;
            if(document.getElementById('ui-call')) document.getElementById('ui-call').innerText = t.callHost;
            
            document.querySelectorAll('.lang-btn').forEach(b => {
                b.classList.toggle('active', b.innerText.toLowerCase() === lang);
            });
            document.body.dir = lang === 'he' || lang === 'ar' ? 'rtl' : 'ltr';
        }

        function onTurnstileSuccess() {
            document.querySelectorAll('.btn').forEach(b => b.disabled = false);
        }

        async function ring(type) {
            const status = document.getElementById('status');
            const token = turnstile.getResponse();
            const t = translations[currentLang];
            
            if (!token) {
                status.innerText = "⚠️ " + t.securityCheck;
                return;
            }

            status.innerHTML = "⏳ <span style='color: var(--accent)'>" + t.ringing + "</span>";
            
            try {
                const res = await fetch('/notify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type, token, lang: currentLang })
                });
                
                const data = await res.json();
                if (res.ok) {
                    status.innerHTML = "✅ <span style='color: #4ade80'>" + t.notified + "</span>";
                    document.querySelectorAll('.btn').forEach(b => b.disabled = true);
                } else {
                    status.innerHTML = "❌ <span style='color: #f87171'>" + t.error + (data.message || data.error) + "</span>";
                }
            } catch (e) {
                status.innerHTML = "❌ <span style='color: #f87171'>" + t.connFailed + "</span>";
            }
        }
    </script>
</body>
</html>
  `;
  return new Response(html, { headers: { "Content-Type": "text/html;charset=UTF-8" } });
}

function serveSetup(env) {
    const html = `
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dori-Bell Setup</title>
        <style>
            body { font-family: sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .card { background: #1e293b; padding: 2rem; border-radius: 1rem; width: 100%; max-width: 400px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #0ea5e9; border: none; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 Dori-Bell Setup</h2>
            <p>Enter your environment variables below:</p>
            <input type="text" placeholder="Family Name (e.g. Cohen Family)" id="name">
            <input type="text" placeholder="Telegram Bot Token" id="token">
            <input type="text" placeholder="Telegram Chat ID" id="chatid">
            <input type="text" placeholder="Phone Number (for direct calls)" id="phone">
            <button onclick="alert('In a real deployment, these would be saved to your Cloudflare Worker environment!')">Save Configuration</button>
            <p style="font-size: 0.8rem; color: #64748b; margin-top: 1rem;">Note: For security, variables must be set in your Wrangler/Cloudflare dashboard.</p>
        </div>
    </body>
    </html>
    `;
    return new Response(html, { headers: { "Content-Type": "text/html;charset=UTF-8" } });
}
