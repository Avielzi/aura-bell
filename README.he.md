<div dir="rtl">

# 🛎️ דורי-בל (Dori-Bell): פעמון דלת חכם ב-$0

> **תיאור:** פעמון דלת חכם ב-$0. ללא שרת (Serverless), מאובטח, ושולח התראות לטלגרם. רץ על Cloudflare Workers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by Cloudflare](https://img.shields.io/badge/Cloudflare-Workers-orange.svg?logo=cloudflare)](https://workers.cloudflare.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Avielzi/dori-bell-serverless-template/pulls)

<p align="center">
  <img src="assets/logo.png" alt="Dori-Bell Logo" width="600" />
</p>

[English](./README.md) | **עברית**

## 🤯 למה זה קיים?

בעידן של בתים חכמים, הבנתי שפעמון הדלת הפיזי שלי היה נקודת כשל יחידה - קופסה טיפשה ורועשת שלא ידעה להבחין בין שליח לבין איש מכירות עקשן. הייתי צריך פתרון חכם יותר, שקט יותר, והכי חשוב - חינמי.

**דורי-בל** הוא התוצאה: פעמון דלת חכם מבוסס קוד QR, ללא שרת (Serverless) לחלוטין, שרץ כולו על Cloudflare Workers. זהו השילוב המושלם בין ארכיטקטורת ענן מודרנית לבין אבסורד DIY מהנה.

## ✨ תכונות

| אייקון | תכונה | תיאור |
| :--- | :--- | :--- |
| 🚀 | **Serverless ועלות $0** | רץ לחלוטין על Cloudflare Workers, תוך ניצול השכבה החינמית למספר כמעט בלתי מוגבל של צלצולים. אין שרתים לתחזוקה, אין דמי מנוי חודשיים. |
| 🛡️ | **הגנת בוטים** | משולב עם **Cloudflare Turnstile** כדי להבטיח שרק בני אדם (או בוטים חכמים מאוד) יוכלו לצלצל בפעמון. |
| 🎨 | **כפתורים מותאמים אישית** | הגדרת כל מספר של כפתורים (למשל: **משלוח**, **אורח**, **דחוף**) עם תוויות מותאמות, אייקונים והודעות טלגרם באמצעות אובייקט קונפיגורציה פשוט. הדוגמאות ניתנות להתאמה מלאה. |
| 🌙 | **שעות שקט** | "דורי" ישן בלילה. הגדרת טווח זמנים שבו ההתראות מושתקות באופן אוטומטי. |
| 📱 | **אינטגרציה עם טלגרם** | התראות פוש עשירות ומיידיות שנשלחות ישירות לצ'אט הטלגרם שלך דרך ה-Bot API. |

## 🖼️ דמו וצילומי מסך

| מסך ראשי (תצוגת מובייל) | התראת טלגרם |
| :---: | :---: |
| <img src="assets/mobile_mockup.png" alt="Mobile Screen Mockup" width="300" /> | <img src="assets/telegram_mockup.png" alt="Telegram Notification Mockup" width="500" /> |

## 🚀 מדריך מהיר (התקנה)

### דרישות קדם

1.  חשבון **Cloudflare**.
2.  **בוט טלגרם** ו-**Chat ID** שלך.
3.  מפתח אתר (Site Key) ומפתח סודי (Secret Key) של **Cloudflare Turnstile**.

### אפשרות א': דרך ההאקרים (שימוש ב-Wrangler CLI)

זוהי הדרך המומלצת למפתחים.

1.  **שכפול המאגר:**
    ```bash
    git clone https://github.com/Avielzi/dori-bell-serverless-template.git
    cd dori-bell-serverless-template
    ```

2.  **התקנת Wrangler:**
    ```bash
    npm install -g wrangler
    wrangler login
    ```

3.  **הגדרת משתני סביבה:**
    העתק את הקובץ `.env.example` ל-`.env` ומלא את הסודות שלך.
    ```bash
    cp .env.example .env
    # ערוך את .env עם הסודות שלך
    ```
    קובץ ה-`wrangler.toml` מוגדר לקרוא סודות מהסביבה שלך או מלוח הבקרה של Cloudflare, מה שמבטיח ששום סוד לא יישמר במאגר.

4.  **פריסה (Deploy):**
    ```bash
    wrangler deploy
    ```

### אפשרות ב': הדרך הקלה (הגדרה ידנית)

1.  עבור ללוח הבקרה של Cloudflare -> Workers & Pages -> Create Application -> Create Worker.
2.  תן שם ל-Worker שלך: `dori-bell-serverless`.
3.  העתק את כל התוכן של `worker.js` והדבק אותו בעורך ה-Worker.
4.  עבור ללשונית **Settings** -> **Variables** -> **Environment Variables** והוסף את המשתנים הנדרשים (ראה סעיף הגדרות להלן).
5.  לחץ על **Save and Deploy**.

## ⚙️ הגדרות (Configuration)

ה-Worker מסתמך על משתני הסביבה הבאים (מוגדרים בקובץ `.env` מקומי לפיתוח, או בלוח הבקרה של Cloudflare לפריסה):

| משתנה | תיאור | דוגמה | חובה |
| :--- | :--- | :--- | :--- |
| `TG_BOT_TOKEN` | טוקן ה-API של בוט הטלגרם שלך. | `123456:ABC-DEF123456` | **כן** |
| `TG_CHAT_ID` | מזהה הצ'אט (Chat ID) שאליו יישלחו ההתראות. | `-123456789` | **כן** |
| `TURNSTILE_SITE_KEY` | ה-**Site Key** עבור וידג'ט ה-Turnstile (בשימוש ב-HTML). | `0x4AAAAAA...A` | **כן** |
| `TURNSTILE_SECRET` | ה-**Secret Key** עבור אימות ה-API של Turnstile (בשימוש ב-Worker). | `1x0AAAAAA...A` | **כן** |
| `FAMILY_NAME` | השם שיוצג על מסך פעמון הדלת. | `Cohen-Ziso Family` | לא (ברירת מחדל: `The Innovation Lab`) |
| `TIMEZONE_OFFSET` | היסט אזור הזמן המקומי שלך מ-UTC בשעות (למשל: `2` לישראל). | `2` | לא (ברירת מחדל: `2`) |
| `QUIET_HOURS_START` | שעה (0-23) לתחילת השתקת ההתראות. מוגדר באובייקט `CONFIG` ב-`worker.js`. | `22` (10 בערב) | לא (ברירת מחדל: `22`) |
| `QUIET_HOURS_END` | שעה (0-23) לסיום השתקת ההתראות. מוגדר באובייקט `CONFIG` ב-`worker.js`. | `7` (7 בבוקר) | לא (ברירת מחדל: `7`) |

## 🎨 התאמה אישית

ה-Worker של דורי-בל הוא כעת תבנית הניתנת להתאמה מלאה הנשלטת על ידי אובייקט `CONFIG` יחיד בראש הקובץ `worker.js`.

### 1. הגדרת כפתורים

ליבת ההתאמה האישית היא המערך `CONFIG.buttons`. ניתן להוסיף, להסיר או לשנות כל כפתור.

```javascript
const CONFIG = {
  // ...
  buttons: [
    {
      id: "delivery", // מזהה ייחודי לכפתור
      label: "משלוח (דוגמה: וולט)", // טקסט שיוצג על הכפתור
      icon: "🛵", // אימוג'י, מחרוזת SVG או URL לתמונה
      message: "🛵 *התראת משלוח!* צא לקחת את האוכל." // הודעת טלגרם (תומך ב-Markdown)
    },
    
  ],
  // ...
};
```

*   **ID:** חייב להיות מחרוזת ייחודית באותיות קטנות.
*   **Icon:** יכול להיות אימוג'י יוניקוד (מומלץ לפשטות), SVG בקידוד Base64, או קישור לתמונה חיצונית.
*   **Message:** הטקסט שיישלח לטלגרם. השתמש ב-Markdown לעיצוב עשיר.

### 2. שעות שקט ושם משפחה

ניתן גם להתאים אישית את השם המוצג ואת שעות השקט ישירות באובייקט `CONFIG`, שמושך את ערכיו ממשתני הסביבה:

```javascript
const CONFIG = {
  familyName: env.FAMILY_NAME || "The Innovation Lab", // מוצג על המסך
  // ...
  quietHours: {
    start: parseInt(env.QUIET_HOURS_START) || 22,
    end: parseInt(env.QUIET_HOURS_END) || 7,
    timezoneOffset: parseInt(env.TIMEZONE_OFFSET) || 2
  }
};
```

</div>
