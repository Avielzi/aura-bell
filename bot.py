import asyncio
import time
import logging
import shutil
import io
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from groq import AsyncGroq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
import aiosqlite
from duckduckgo_search import DDGS

load_dotenv()

# ====================== CONFIG ======================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
ADMIN_IDS = set(int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit())
ALLOWED_IDS = set(int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip().isdigit())
BOT_NAME = os.getenv("BOT_NAME", "הבוט של אביאל")
MAX_HISTORY_DAYS = int(os.getenv("MAX_HISTORY_DAYS", 90))
RATE_MSGS = int(os.getenv("RATE_MSGS_PER_MIN", 12))
RATE_SEARCH = int(os.getenv("RATE_SEARCH_PER_HOUR", 5))
RATE_IMAGES = int(os.getenv("RATE_IMAGES_PER_HOUR", 4))

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
]
active_model = GROQ_MODELS[0]

# STT models for voice
WHISPER_MODEL = "whisper-large-v3"

storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)
groq_client = AsyncGroq(api_key=GROQ_API_KEY)
hf = InferenceClient(token=HF_TOKEN)

DB_FILE = "bot.db"
banned = set()
rate_limit = defaultdict(lambda: {"msgs": [], "search": [], "images": []})

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ====================== FSM STATES ======================
class ImageGen(StatesGroup):
    waiting_prompt = State()

class ReminderSet(StatesGroup):
    waiting_text = State()
    waiting_time = State()

# ====================== ACCESS ======================
def is_allowed(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    if ALLOWED_IDS and user_id in ALLOWED_IDS:
        return True
    if not ALLOWED_IDS:
        return user_id in ADMIN_IDS
    return False

# ====================== DATABASE ======================
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS history (
            user_id INTEGER, role TEXT, content TEXT, timestamp INTEGER
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS bans (
            user_id INTEGER PRIMARY KEY
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, remind_at INTEGER, text TEXT, created_at INTEGER
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, title TEXT, content TEXT, created_at INTEGER
        )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS user_memory (
            user_id INTEGER PRIMARY KEY,
            facts TEXT DEFAULT '{}',
            updated_at INTEGER
        )""")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_user_time ON history(user_id, timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_reminders ON reminders(remind_at)")
        await db.execute("PRAGMA journal_mode=WAL")
        await db.commit()
    logger.info("Database initialized")

async def load_bans():
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id FROM bans") as cursor:
            for row in await cursor.fetchall():
                banned.add(row[0])

async def save_message(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO history VALUES (?, ?, ?, ?)",
            (user_id, role, content, int(time.time())))
        await db.commit()

async def get_history(user_id: int, limit: int = 20):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT role, content FROM history WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

async def cleanup_old_history():
    cutoff = int((datetime.now() - timedelta(days=MAX_HISTORY_DAYS)).timestamp())
    async with aiosqlite.connect(DB_FILE) as db:
        result = await db.execute("DELETE FROM history WHERE timestamp < ?", (cutoff,))
        await db.commit()
        if result.rowcount > 0:
            logger.info(f"Cleaned {result.rowcount} old messages")

async def backup_before_wipe():
    os.makedirs("backups", exist_ok=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        await db.commit()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"backups/bot_backup_{ts}.db"
    await asyncio.to_thread(shutil.copy, DB_FILE, path)
    return path

# ====================== USER MEMORY ======================
async def get_user_facts(user_id: int) -> dict:
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT facts FROM user_memory WHERE user_id=?", (user_id,)) as c:
            row = await c.fetchone()
            return json.loads(row[0]) if row else {}

async def save_user_facts(user_id: int, facts: dict):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO user_memory (user_id, facts, updated_at) VALUES (?, ?, ?)",
            (user_id, json.dumps(facts, ensure_ascii=False), int(time.time()))
        )
        await db.commit()

async def extract_and_save_facts(user_id: int, text: str):
    """חלץ עובדות מהשיחה ושמור בזיכרון"""
    fact_patterns = [
        (r"אני גר ב(.+?)(?:\.|$)", "מיקום"),
        (r"אני עובד ב(.+?)(?:\.|$)", "עבודה"),
        (r"שמי הוא (.+?)(?:\.|$)", "שם"),
        (r"אני בן (\d+)", "גיל"),
        (r"הטלפון שלי (.+?)(?:\.|$)", "טלפון"),
    ]
    facts = await get_user_facts(user_id)
    changed = False
    for pattern, key in fact_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            facts[key] = match.group(1).strip()
            changed = True
    if changed:
        await save_user_facts(user_id, facts)

# ====================== RATE LIMITING ======================
def clean_old_timestamps(user_id: int, key: str, seconds: int):
    now = time.time()
    rate_limit[user_id][key] = [t for t in rate_limit[user_id][key] if now - t < seconds]

async def check_rate(user_id: int, key: str, limit: int, window_sec: int) -> bool:
    clean_old_timestamps(user_id, key, window_sec)
    if len(rate_limit[user_id][key]) >= limit:
        return False
    rate_limit[user_id][key].append(time.time())
    return True

# ====================== MODEL AUTO-UPDATE ======================
async def get_best_model() -> str:
    global active_model
    for model in GROQ_MODELS:
        try:
            test = await groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5
            )
            if test.choices:
                active_model = model
                return model
        except Exception:
            continue
    return active_model

# ====================== REMINDERS ======================
def parse_reminder_time(text: str) -> tuple:
    now = int(time.time())
    total_seconds = 0
    reminder_text = text
    patterns = [
        (r'(\d+)\s*(?:שעות?|ש\'?)', 3600),
        (r'(\d+)\s*(?:דקות?|ד\'?)', 60),
        (r'(\d+)\s*(?:ימים?)', 86400),
        (r'(\d+)h', 3600),
        (r'(\d+)m', 60),
        (r'(\d+)d', 86400),
    ]
    for pattern, multiplier in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            total_seconds += int(match.group(1)) * multiplier
            reminder_text = re.sub(pattern, '', reminder_text, flags=re.IGNORECASE).strip()

    time_match = re.search(r'(\d{1,2}):(\d{2})', text)
    if time_match and total_seconds == 0:
        h, m = int(time_match.group(1)), int(time_match.group(2))
        target = datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= datetime.now():
            target += timedelta(days=1)
        total_seconds = int(target.timestamp()) - now
        reminder_text = re.sub(r'\d{1,2}:\d{2}', '', reminder_text).strip()

    if total_seconds <= 0:
        return None, text

    for word in ['תזכיר לי', 'תזכור לי', 'תזכורת', 'remind', 'בעוד', 'תוך']:
        reminder_text = reminder_text.replace(word, '').strip()

    return now + total_seconds, reminder_text or "תזכורת"

async def reminder_checker():
    while True:
        try:
            now = int(time.time())
            async with aiosqlite.connect(DB_FILE) as db:
                async with db.execute(
                    "SELECT id, user_id, text FROM reminders WHERE remind_at <= ?", (now,)
                ) as cursor:
                    due = await cursor.fetchall()
                for r_id, user_id, text in due:
                    try:
                        kb = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(text="✅ בוצע", callback_data=f"done_reminder_{r_id}"),
                            InlineKeyboardButton(text="⏰ עוד 30 דק'", callback_data=f"snooze_{r_id}_30"),
                            InlineKeyboardButton(text="⏰ עוד שעה", callback_data=f"snooze_{r_id}_60"),
                        ]])
                        await bot.send_message(user_id, f"⏰ **תזכורת:**\n{text}", reply_markup=kb)
                    except Exception as e:
                        logger.error(f"Reminder send error: {e}")
                    await db.execute("DELETE FROM reminders WHERE id=?", (r_id,))
                await db.commit()
        except Exception as e:
            logger.error(f"Reminder checker error: {e}")
        await asyncio.sleep(30)

# ====================== VOICE ======================
async def transcribe_voice(file_bytes: bytes) -> str:
    """תמלול קול עם Groq Whisper"""
    try:
        audio_file = io.BytesIO(file_bytes)
        audio_file.name = "voice.ogg"
        transcription = await groq_client.audio.transcriptions.create(
            file=audio_file,
            model=WHISPER_MODEL,
            language="he",
            response_format="text"
        )
        return transcription.strip()
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""

async def text_to_voice(text: str) -> io.BytesIO | None:
    """המרת טקסט לקול עם Groq TTS"""
    try:
        response = await groq_client.audio.speech.create(
            model="playai-tts",
            voice="Cheyenne-PlayAI",
            input=text[:500],
            response_format="wav"
        )
        buf = io.BytesIO(response.content)
        buf.seek(0)
        return buf
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None

# ====================== SEARCH & IMAGE ======================
async def async_web_search(query: str) -> str:
    def sync_search():
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))
        return "\n".join([f"• {r['title']}: {r['body'][:200]}" for r in results])
    try:
        snippets = await asyncio.to_thread(sync_search)
        if not snippets:
            return "לא נמצאו תוצאות."
        resp = await groq_client.chat.completions.create(
            model=active_model,
            messages=[{"role": "user", "content": f"סכם בעברית בקצרה:\n\n{snippets}"}],
            max_tokens=600
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"Search error: {e}")
        return "שגיאה בחיפוש."

async def async_generate_flux(prompt: str, variant: str = "schnell") -> io.BytesIO:
    def sync_flux():
        return hf.text_to_image(
            prompt,
            model=f"black-forest-labs/FLUX.1-{variant}",
            num_inference_steps=4 if variant == "schnell" else 28,
            width=1024, height=1024
        )
    image = await asyncio.to_thread(sync_flux)
    buf = io.BytesIO()
    image.save(buf, "PNG")
    buf.seek(0)
    return buf

# ====================== KEYBOARDS ======================
def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎨 תמונה מהירה", callback_data="img_schnell"),
            InlineKeyboardButton(text="🖼 תמונה איכותית", callback_data="img_dev"),
        ],
        [
            InlineKeyboardButton(text="🔍 חיפוש", callback_data="search_mode"),
            InlineKeyboardButton(text="⏰ תזכורת", callback_data="remind_mode"),
        ],
        [
            InlineKeyboardButton(text="📋 פתקים", callback_data="show_notes"),
            InlineKeyboardButton(text="📋 תזכורות", callback_data="show_reminders"),
        ],
        [
            InlineKeyboardButton(text="🧠 זיכרון", callback_data="show_memory"),
            InlineKeyboardButton(text="📊 סטטוס", callback_data="show_status"),
        ],
    ])

def after_reply_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔄 המשך", callback_data="continue_chat"),
        InlineKeyboardButton(text="🔍 חפש", callback_data="search_mode"),
        InlineKeyboardButton(text="📝 שמור פתק", callback_data="save_as_note"),
        InlineKeyboardButton(text="🎤 השמע", callback_data="tts_last"),
    ]])

# ====================== HANDLERS ======================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return await message.answer("🔒 בוט פרטי.")
    await message.answer(
        f"👋 **{BOT_NAME}** מוכן\n\n"
        f"דבר איתי חופשי, או בחר מהתפריט:",
        reply_markup=main_menu_kb()
    )

@dp.message(Command("menu"))
async def menu_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    await message.answer("📱 תפריט ראשי:", reply_markup=main_menu_kb())

# ====================== CALLBACKS ======================
@dp.callback_query(F.data == "img_schnell")
async def cb_img_schnell(callback: CallbackQuery, state: FSMContext):
    if not is_allowed(callback.from_user.id):
        return await callback.answer("🔒 אין גישה")
    await state.set_state(ImageGen.waiting_prompt)
    await state.update_data(variant="schnell")
    await callback.message.answer("🎨 תאר את התמונה שתרצה:")
    await callback.answer()

@dp.callback_query(F.data == "img_dev")
async def cb_img_dev(callback: CallbackQuery, state: FSMContext):
    if not is_allowed(callback.from_user.id):
        return await callback.answer("🔒 אין גישה")
    await state.set_state(ImageGen.waiting_prompt)
    await state.update_data(variant="dev")
    await callback.message.answer("🖼 תאר את התמונה האיכותית שתרצה:")
    await callback.answer()

@dp.message(ImageGen.waiting_prompt)
async def process_image_prompt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    variant = data.get("variant", "schnell")
    await state.clear()
    prompt = message.text
    await message.answer(f"🎨 יוצר עם Flux {variant.upper()}...")
    try:
        buf = await async_generate_flux(prompt, variant)
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔄 גרסה חדשה", callback_data=f"regen_{variant}_{prompt[:30]}"),
            InlineKeyboardButton(text="🖼 גרסה איכותית", callback_data=f"regen_dev_{prompt[:30]}"),
        ]])
        await message.answer_photo(
            types.BufferedInputFile(buf.read(), filename="flux.png"),
            caption=f"🎨 Flux {variant.upper()}\n📝 {prompt}",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Flux error: {e}")
        await message.answer("❌ שגיאה ביצירת תמונה")

@dp.callback_query(F.data == "remind_mode")
async def cb_remind(callback: CallbackQuery, state: FSMContext):
    if not is_allowed(callback.from_user.id):
        return
    await state.set_state(ReminderSet.waiting_text)
    await callback.message.answer("📝 מה לזכור לך?")
    await callback.answer()

@dp.message(ReminderSet.waiting_text)
async def remind_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(ReminderSet.waiting_time)
    await message.answer(
        "⏰ מתי? (לדוגמה: `2h`, `30m`, `18:30`, `1d`)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="15 דקות", callback_data="rt_15m"),
            InlineKeyboardButton(text="שעה", callback_data="rt_1h"),
            InlineKeyboardButton(text="מחר", callback_data="rt_1d"),
        ]])
    )

@dp.callback_query(F.data.startswith("rt_"))
async def cb_remind_time(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "תזכורת")
    time_map = {"rt_15m": 15*60, "rt_1h": 3600, "rt_1d": 86400}
    seconds = time_map.get(callback.data, 3600)
    remind_at = int(time.time()) + seconds
    await state.clear()
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, remind_at, text, created_at) VALUES (?, ?, ?, ?)",
            (callback.from_user.id, remind_at, text, int(time.time()))
        )
        await db.commit()
    dt = datetime.fromtimestamp(remind_at).strftime('%d/%m %H:%M')
    await callback.message.answer(f"✅ תזכורת נקבעה:\n**{text}**\n⏰ {dt}")
    await callback.answer()

@dp.message(ReminderSet.waiting_time)
async def remind_time_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "תזכורת")
    remind_at, _ = parse_reminder_time(message.text)
    if not remind_at:
        return await message.answer("❌ לא הבנתי את הזמן. נסה: `2h`, `30m`, `18:30`")
    await state.clear()
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, remind_at, text, created_at) VALUES (?, ?, ?, ?)",
            (message.from_user.id, remind_at, text, int(time.time()))
        )
        await db.commit()
    dt = datetime.fromtimestamp(remind_at).strftime('%d/%m %H:%M')
    await message.answer(f"✅ תזכורת:\n**{text}**\n⏰ {dt}")

@dp.callback_query(F.data.startswith("snooze_"))
async def cb_snooze(callback: CallbackQuery):
    parts = callback.data.split("_")
    r_id = parts[1]
    minutes = int(parts[2])
    new_time = int(time.time()) + minutes * 60
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, remind_at, text, created_at) VALUES (?, ?, ?, ?)",
            (callback.from_user.id, new_time, "⏰ תזכורת נדחתה", int(time.time()))
        )
        await db.commit()
    await callback.answer(f"⏰ נדחה ב-{minutes} דקות")
    await callback.message.edit_reply_markup(reply_markup=None)

@dp.callback_query(F.data.startswith("done_reminder_"))
async def cb_done_reminder(callback: CallbackQuery):
    await callback.answer("✅ מעולה!")
    await callback.message.edit_reply_markup(reply_markup=None)

@dp.callback_query(F.data == "show_notes")
async def cb_show_notes(callback: CallbackQuery):
    if not is_allowed(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT id, title, content, created_at FROM notes WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
            (callback.from_user.id,)
        ) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        await callback.answer("📭 אין פתקים", show_alert=True)
        return
    lines = ["📋 **פתקים:**\n"]
    for n_id, title, content, created_at in rows:
        dt = datetime.fromtimestamp(created_at).strftime('%d/%m')
        preview = f" – {content[:40]}..." if content else ""
        lines.append(f"• `#{n_id}` [{dt}] **{title}**{preview}")
    lines.append("\nלמחיקה: `/delnote <מספר>`")
    await callback.message.answer("\n".join(lines))
    await callback.answer()

@dp.callback_query(F.data == "show_reminders")
async def cb_show_reminders(callback: CallbackQuery):
    if not is_allowed(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT id, remind_at, text FROM reminders WHERE user_id=? ORDER BY remind_at",
            (callback.from_user.id,)
        ) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        await callback.answer("📭 אין תזכורות", show_alert=True)
        return
    lines = ["⏰ **תזכורות פעילות:**\n"]
    for r_id, remind_at, text in rows:
        dt = datetime.fromtimestamp(remind_at).strftime('%d/%m %H:%M')
        lines.append(f"• `#{r_id}` {dt} – {text}")
    await callback.message.answer("\n".join(lines))
    await callback.answer()

@dp.callback_query(F.data == "show_memory")
async def cb_show_memory(callback: CallbackQuery):
    if not is_allowed(callback.from_user.id):
        return
    facts = await get_user_facts(callback.from_user.id)
    if not facts:
        await callback.answer("🧠 לא נצברו עובדות עדיין", show_alert=True)
        return
    lines = ["🧠 **מה שזכרתי עליך:**\n"]
    for key, val in facts.items():
        lines.append(f"• {key}: {val}")
    await callback.message.answer("\n".join(lines))
    await callback.answer()

@dp.callback_query(F.data == "show_status")
async def cb_show_status(callback: CallbackQuery):
    if not is_allowed(callback.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT COUNT(*) FROM history WHERE user_id=?", (callback.from_user.id,)) as c:
            msgs = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM reminders WHERE user_id=?", (callback.from_user.id,)) as c:
            reminders = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM notes WHERE user_id=?", (callback.from_user.id,)) as c:
            notes = (await c.fetchone())[0]
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    await callback.message.answer(
        f"📊 **הסטטוס שלך:**\n"
        f"• הודעות: {msgs:,}\n"
        f"• תזכורות פעילות: {reminders}\n"
        f"• פתקים: {notes}\n"
        f"• מודל: `{active_model}`\n"
        f"• שעה: {now_str}"
    )
    await callback.answer()

@dp.callback_query(F.data == "tts_last")
async def cb_tts_last(callback: CallbackQuery):
    if not is_allowed(callback.from_user.id):
        return
    await callback.answer("🎤 מכין הקלטה...")
    history = await get_history(callback.from_user.id, limit=2)
    if not history:
        return await callback.message.answer("❌ אין הודעה להשמיע")
    last_reply = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), None)
    if not last_reply:
        return await callback.message.answer("❌ אין תשובה להשמיע")
    audio = await text_to_voice(last_reply[:500])
    if audio:
        await callback.message.answer_voice(
            types.BufferedInputFile(audio.read(), filename="reply.wav"),
            caption="🔊 תשובה קולית"
        )
    else:
        await callback.message.answer("❌ שגיאה ביצירת קול")

@dp.callback_query(F.data == "search_mode")
async def cb_search(callback: CallbackQuery):
    await callback.message.answer("🔍 שלח `/search <מה לחפש>`")
    await callback.answer()

@dp.callback_query(F.data == "continue_chat")
async def cb_continue(callback: CallbackQuery):
    await callback.answer("💬 המשך לכתוב!")

@dp.callback_query(F.data == "save_as_note")
async def cb_save_note(callback: CallbackQuery):
    history = await get_history(callback.from_user.id, limit=2)
    last_reply = next((m["content"] for m in reversed(history) if m["role"] == "assistant"), None)
    if not last_reply:
        return await callback.answer("❌ אין מה לשמור", show_alert=True)
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO notes (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            (callback.from_user.id, f"תשובה {datetime.now().strftime('%d/%m %H:%M')}", last_reply[:500], int(time.time()))
        )
        await db.commit()
    await callback.answer("✅ נשמר כפתק!")

# ====================== VOICE HANDLER ======================
@dp.message(F.voice | F.audio)
async def voice_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return await message.answer("🔒 אין גישה")

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        file_obj = message.voice or message.audio
        file = await bot.get_file(file_obj.file_id)
        file_bytes = await bot.download_file(file.file_path)
        audio_data = file_bytes.read()

        # תמלול
        text = await transcribe_voice(audio_data)
        if not text:
            return await message.answer("❌ לא הצלחתי לתמלל. נסה שוב.")

        await message.answer(f"🎤 **שמעתי:** {text}")

        # תשובה מה-AI
        history = await get_history(message.from_user.id)
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        messages = [{"role": "system", "content": f"""אתה הבוט האישי של אביאל - איש IT ואוטומציה מישראל.
אופי: ציני, ישיר, לא מבזבז מילים. הומור יבש וסארקזם במינון נכון.
מומחיות: IT, Windows/Active Directory, Python, אוטומציה, AI, טלגרם בוטים, ענן.
השעה: {now_str}. עברית בלבד. תשובות קצרות וממוקדות.
אל תתחיל ב"בהחלט!" / "כמובן!" / "שאלה מצוינת!""""}
        ] + history + [{"role": "user", "content": text}]

        response = await groq_client.chat.completions.create(
            model=active_model, messages=messages, max_tokens=400, temperature=0.7
        )
        reply = response.choices[0].message.content

        # שלח תשובה קולית
        audio_reply = await text_to_voice(reply)
        if audio_reply:
            await message.answer_voice(
                types.BufferedInputFile(audio_reply.read(), filename="reply.wav"),
                caption=f"💬 {reply[:200]}{'...' if len(reply) > 200 else ''}"
            )
        else:
            await message.answer(reply, reply_markup=after_reply_kb())

        await save_message(message.from_user.id, "user", f"[קולי] {text}")
        await save_message(message.from_user.id, "assistant", reply)

    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        await message.answer("❌ שגיאה בעיבוד ההקלטה")

# ====================== COMMANDS ======================
@dp.message(Command("remind"))
async def remind_handler(message: types.Message, command: CommandObject):
    if not is_allowed(message.from_user.id):
        return
    if not command.args:
        return await message.answer(
            "❓ שימוש:\n`/remind 2h לקנות חלב`\n`/remind 18:30 פגישה`\n`/remind 1d חידוש מנוי`"
        )
    remind_at, text = parse_reminder_time(command.args)
    if not remind_at:
        return await message.answer("❌ לא הבנתי את הזמן")
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO reminders (user_id, remind_at, text, created_at) VALUES (?, ?, ?, ?)",
            (message.from_user.id, remind_at, text, int(time.time()))
        )
        await db.commit()
    dt = datetime.fromtimestamp(remind_at).strftime('%d/%m/%Y %H:%M')
    await message.answer(f"✅ **תזכורת:**\n📝 {text}\n⏰ {dt}")

@dp.message(Command("reminders"))
async def reminders_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT id, remind_at, text FROM reminders WHERE user_id=? ORDER BY remind_at",
            (message.from_user.id,)
        ) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        return await message.answer("📭 אין תזכורות פעילות")
    lines = ["⏰ **תזכורות:**\n"]
    for r_id, remind_at, text in rows:
        dt = datetime.fromtimestamp(remind_at).strftime('%d/%m %H:%M')
        lines.append(f"• `#{r_id}` {dt} – {text}")
    lines.append("\nלמחיקה: `/delremind <מספר>`")
    await message.answer("\n".join(lines))

@dp.message(Command("delremind"))
async def delremind_handler(message: types.Message, command: CommandObject):
    if not is_allowed(message.from_user.id) or not command.args or not command.args.strip().isdigit():
        return await message.answer("❓ `/delremind <מספר>`")
    r_id = int(command.args.strip())
    async with aiosqlite.connect(DB_FILE) as db:
        result = await db.execute("DELETE FROM reminders WHERE id=? AND user_id=?", (r_id, message.from_user.id))
        await db.commit()
    await message.answer(f"{'✅ נמחק' if result.rowcount else '❌ לא נמצא'}")

@dp.message(Command("note"))
async def note_handler(message: types.Message, command: CommandObject):
    if not is_allowed(message.from_user.id) or not command.args:
        return await message.answer("❓ `/note כותרת | תוכן`")
    parts = command.args.split("|", 1)
    title, content = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT INTO notes (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            (message.from_user.id, title, content, int(time.time())))
        await db.commit()
    await message.answer(f"📝 פתק נשמר: **{title}**")

@dp.message(Command("notes"))
async def notes_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT id, title, content, created_at FROM notes WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
            (message.from_user.id,)
        ) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        return await message.answer("📭 אין פתקים")
    lines = ["📋 **פתקים:**\n"]
    for n_id, title, content, ts in rows:
        dt = datetime.fromtimestamp(ts).strftime('%d/%m')
        preview = f" – {content[:40]}..." if content else ""
        lines.append(f"• `#{n_id}` [{dt}] **{title}**{preview}")
    lines.append("\nלמחיקה: `/delnote <מספר>`")
    await message.answer("\n".join(lines))

@dp.message(Command("delnote"))
async def delnote_handler(message: types.Message, command: CommandObject):
    if not is_allowed(message.from_user.id) or not command.args or not command.args.strip().isdigit():
        return await message.answer("❓ `/delnote <מספר>`")
    n_id = int(command.args.strip())
    async with aiosqlite.connect(DB_FILE) as db:
        result = await db.execute("DELETE FROM notes WHERE id=? AND user_id=?", (n_id, message.from_user.id))
        await db.commit()
    await message.answer(f"{'✅ נמחק' if result.rowcount else '❌ לא נמצא'}")

@dp.message(Command("find"))
async def find_handler(message: types.Message, command: CommandObject):
    if not is_allowed(message.from_user.id) or not command.args:
        return await message.answer("❓ `/find <מילה>`")
    query = command.args.strip()
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute(
            "SELECT id, title, content FROM notes WHERE user_id=? AND (title LIKE ? OR content LIKE ?)",
            (message.from_user.id, f"%{query}%", f"%{query}%")
        ) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        return await message.answer(f"🔍 לא נמצא: `{query}`")
    lines = [f"🔍 **תוצאות עבור '{query}':**\n"]
    for n_id, title, content in rows:
        preview = content[:60] + "..." if content and len(content) > 60 else content or ""
        lines.append(f"• `#{n_id}` **{title}**\n  {preview}")
    await message.answer("\n".join(lines))

@dp.message(Command("export"))
async def export_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT title, content, created_at FROM notes WHERE user_id=? ORDER BY created_at DESC", (message.from_user.id,)) as c:
            notes = await c.fetchall()
        async with db.execute("SELECT remind_at, text FROM reminders WHERE user_id=? ORDER BY remind_at", (message.from_user.id,)) as c:
            reminders = await c.fetchall()
    lines = [f"# הייצוא של {BOT_NAME}\n", f"תאריך: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"]
    if notes:
        lines.append("\n## פתקים\n")
        for title, content, ts in notes:
            dt = datetime.fromtimestamp(ts).strftime('%d/%m/%Y')
            lines.append(f"### {title} ({dt})\n{content or ''}\n")
    if reminders:
        lines.append("\n## תזכורות פעילות\n")
        for remind_at, text in reminders:
            dt = datetime.fromtimestamp(remind_at).strftime('%d/%m/%Y %H:%M')
            lines.append(f"- {dt}: {text}\n")
    buf = io.BytesIO("\n".join(lines).encode('utf-8'))
    buf.seek(0)
    await message.answer_document(
        types.BufferedInputFile(buf.read(), filename=f"export_{datetime.now().strftime('%Y%m%d')}.md"),
        caption="📤 הייצוא שלך"
    )

@dp.message(Command("memory"))
async def memory_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    facts = await get_user_facts(message.from_user.id)
    if not facts:
        return await message.answer("🧠 לא נצברו עובדות עדיין.\nאמור לי דברים עליך ואזכור.")
    lines = ["🧠 **מה שזכרתי עליך:**\n"]
    for key, val in facts.items():
        lines.append(f"• {key}: **{val}**")
    lines.append("\nלמחיקה: `/clearmemory`")
    await message.answer("\n".join(lines))

@dp.message(Command("clearmemory"))
async def clearmemory_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM user_memory WHERE user_id=?", (message.from_user.id,))
        await db.commit()
    await message.answer("✅ הזיכרון נוקה")

@dp.message(Command("model"))
async def model_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    await message.answer(f"🤖 מודל פעיל: `{active_model}`\n\nבודק...")
    best = await get_best_model()
    await message.answer(
        f"✅ מודל עדכני: `{best}`\n\n" +
        "\n".join([f"{'✅' if m == best else '⬜'} `{m}`" for m in GROQ_MODELS])
    )

@dp.message(Command("clear"))
async def clear_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM history WHERE user_id=?", (message.from_user.id,))
        await db.commit()
    await message.answer("✅ היסטוריה נוקתה")

@dp.message(Command("myid"))
async def myid_handler(message: types.Message):
    await message.answer(
        f"🆔 ID: `{message.from_user.id}`\n"
        f"שם: {message.from_user.full_name}\n"
        f"{'✅ יש גישה' if is_allowed(message.from_user.id) else '🔒 אין גישה'}"
    )

@dp.message(Command("search"))
async def search_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return await message.answer("🔒 אין גישה")
    if not await check_rate(message.from_user.id, "search", RATE_SEARCH, 3600):
        return await message.answer(f"⏳ מגבלה: {RATE_SEARCH} חיפושים/שעה")
    query = message.text.replace("/search", "").strip()
    if not query:
        return await message.answer("❓ `/search <שאילתה>`")
    await bot.send_chat_action(message.chat.id, "typing")
    result = await async_web_search(query)
    await message.answer(result, reply_markup=after_reply_kb())

@dp.message(Command("flux", "fluxdev"))
async def flux_handler(message: types.Message):
    if not is_allowed(message.from_user.id):
        return await message.answer("🔒 אין גישה")
    if not await check_rate(message.from_user.id, "images", RATE_IMAGES, 3600):
        return await message.answer(f"⏳ מגבלה: {RATE_IMAGES} תמונות/שעה")
    variant = "dev" if message.text.startswith("/fluxdev") else "schnell"
    prompt = message.text.replace(f"/{message.text.split()[0][1:]}", "").strip()
    if not prompt:
        return await message.answer("❓ `/flux <תיאור>`")
    await bot.send_chat_action(message.chat.id, "upload_photo")
    try:
        buf = await async_generate_flux(prompt, variant)
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔄 נסה שוב", callback_data=f"img_{variant}"),
        ]])
        await message.answer_photo(
            types.BufferedInputFile(buf.read(), filename="flux.png"),
            caption=f"🎨 Flux {variant.upper()}\n📝 {prompt}",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Flux error: {e}")
        await message.answer("❌ שגיאה ביצירת תמונה")

# ====================== ADMIN ======================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(
        "🔧 **פאנל מנהל:**\n\n"
        "• `/stats` – סטטיסטיקות\n"
        "• `/ban <ID>` – חסום\n"
        "• `/unban <ID>` – שחרר\n"
        "• `/broadcast <הודעה>` – שלח לכולם\n"
        "• `/model` – בדוק מודל\n"
        "• `/wipeall CONFIRM` – מחק הכל"
    )

@dp.message(Command("stats"))
async def stats_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT COUNT(*) FROM history") as c:
            total = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(DISTINCT user_id) FROM history") as c:
            users = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM reminders") as c:
            reminders = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM notes") as c:
            notes = (await c.fetchone())[0]
    await message.answer(
        f"📈 **סטטיסטיקות:**\n"
        f"• הודעות: {total:,}\n• משתמשים: {users}\n"
        f"• תזכורות: {reminders}\n• פתקים: {notes}\n"
        f"• מודל: `{active_model}`"
    )

@dp.message(Command("ban"))
async def ban_handler(message: types.Message, command: CommandObject):
    if message.from_user.id not in ADMIN_IDS or not command.args:
        return
    try:
        uid = int(command.args.strip())
        if uid in ADMIN_IDS:
            return await message.answer("❌ לא ניתן לחסום מנהל")
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("INSERT OR IGNORE INTO bans VALUES (?)", (uid,))
            await db.commit()
        banned.add(uid)
        await message.answer(f"🚫 {uid} נחסם")
    except ValueError:
        await message.answer("❌ ID לא תקין")

@dp.message(Command("unban"))
async def unban_handler(message: types.Message, command: CommandObject):
    if message.from_user.id not in ADMIN_IDS or not command.args:
        return
    try:
        uid = int(command.args.strip())
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute("DELETE FROM bans WHERE user_id=?", (uid,))
            await db.commit()
        banned.discard(uid)
        await message.answer(f"✅ {uid} שוחרר")
    except ValueError:
        await message.answer("❌ ID לא תקין")

@dp.message(Command("broadcast"))
async def broadcast_handler(message: types.Message, command: CommandObject):
    if message.from_user.id not in ADMIN_IDS or not command.args:
        return
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT DISTINCT user_id FROM history") as cursor:
            users = [r[0] for r in await cursor.fetchall()]
    sent = failed = 0
    for uid in users:
        if uid in banned or uid in ADMIN_IDS:
            continue
        try:
            await bot.send_message(uid, f"📢 {command.args}")
            sent += 1
        except Exception:
            failed += 1
        if sent % 20 == 0:
            await asyncio.sleep(1)
    await message.answer(f"✅ נשלח: {sent} | נכשל: {failed}")

@dp.message(Command("wipeall"))
async def wipeall_handler(message: types.Message, command: CommandObject):
    if message.from_user.id not in ADMIN_IDS:
        return
    if command.args and command.args.strip().upper() == "CONFIRM":
        backup = await backup_before_wipe()
        async with aiosqlite.connect(DB_FILE) as db:
            for table in ["history", "bans", "reminders", "notes", "user_memory"]:
                await db.execute(f"DELETE FROM {table}")
            await db.commit()
        banned.clear()
        rate_limit.clear()
        await message.answer(f"✅ הכל נמחק. גיבוי: `{backup}`")
    else:
        await message.answer("⚠️ לאישור: `/wipeall CONFIRM`")

# ====================== MAIN CHAT ======================
@dp.message()
async def chat_handler(message: types.Message, state: FSMContext):
    if not is_allowed(message.from_user.id):
        return await message.answer("🔒 בוט פרטי.")
    if message.from_user.id in banned or not message.text:
        return
    if not await check_rate(message.from_user.id, "msgs", RATE_MSGS, 60):
        return await message.answer(f"⏳ מגבלה: {RATE_MSGS} הודעות/דקה")

    # זיהוי תזכורת אוטומטי
    reminder_keywords = ["תזכיר לי", "תזכור לי", "תזכורת ל", "remind me"]
    if any(kw in message.text.lower() for kw in reminder_keywords):
        remind_at, text = parse_reminder_time(message.text)
        if remind_at:
            async with aiosqlite.connect(DB_FILE) as db:
                await db.execute(
                    "INSERT INTO reminders (user_id, remind_at, text, created_at) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, remind_at, text, int(time.time()))
                )
                await db.commit()
            dt = datetime.fromtimestamp(remind_at).strftime('%d/%m/%Y %H:%M')
            return await message.answer(f"✅ תזכורת נקבעה:\n**{text}**\n⏰ {dt}")

    # שמירת עובדות
    await extract_and_save_facts(message.from_user.id, message.text)

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        history = await get_history(message.from_user.id)
        facts = await get_user_facts(message.from_user.id)
        facts_str = "\n".join([f"- {k}: {v}" for k, v in facts.items()]) if facts else "אין עדיין"
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')

        messages = [{"role": "system", "content": f"""אתה הבוט האישי של אביאל - איש IT ואוטומציה מישראל.
אופי: ציני, ישיר, לא מבזבז מילים. הומור יבש וסארקזם במינון נכון.
מומחיות: IT, Windows/Active Directory, Python, אוטומציה, AI, טלגרם בוטים, ענן.
השעה: {now_str}
עובדות שאתה זוכר על המשתמש:
{facts_str}
עברית בלבד. תשובות קצרות וממוקדות.
אל תתחיל ב"בהחלט!" / "כמובן!" / "שאלה מצוינת!""""}
        ] + history + [{"role": "user", "content": message.text}]

        response = await groq_client.chat.completions.create(
            model=active_model, messages=messages, max_tokens=900, temperature=0.7
        )
        reply = response.choices[0].message.content
        await message.answer(reply, reply_markup=after_reply_kb())
        await save_message(message.from_user.id, "user", message.text)
        await save_message(message.from_user.id, "assistant", reply)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        await message.answer("❌ שגיאה. נסה שוב.")

# ====================== BACKGROUND ======================
async def cleanup_task():
    while True:
        await asyncio.sleep(86400)
        try:
            await cleanup_old_history()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def model_check_task():
    while True:
        await asyncio.sleep(86400)
        try:
            old = active_model
            new = await get_best_model()
            if new != old:
                for admin_id in ADMIN_IDS:
                    try:
                        await bot.send_message(admin_id, f"🤖 מודל עודכן:\n`{old}` → `{new}`")
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Model check error: {e}")

async def daily_summary_task():
    """סיכום יומי בכל בוקר ב-8:00"""
    while True:
        now = datetime.now()
        next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        await asyncio.sleep((next_run - now).total_seconds())
        try:
            for user_id in ALLOWED_IDS | ADMIN_IDS:
                async with aiosqlite.connect(DB_FILE) as db:
                    async with db.execute(
                        "SELECT remind_at, text FROM reminders WHERE user_id=? AND remind_at < ? ORDER BY remind_at",
                        (user_id, int((datetime.now() + timedelta(days=1)).timestamp()))
                    ) as c:
                        todays = await c.fetchall()
                if todays:
                    lines = ["☀️ **תזכורות להיום:**\n"]
                    for remind_at, text in todays:
                        dt = datetime.fromtimestamp(remind_at).strftime('%H:%M')
                        lines.append(f"• {dt} – {text}")
                    try:
                        await bot.send_message(user_id, "\n".join(lines))
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Daily summary error: {e}")

# ====================== MAIN ======================
async def main():
    await init_db()
    await load_bans()
    await get_best_model()
    asyncio.create_task(cleanup_task())
    asyncio.create_task(reminder_checker())
    asyncio.create_task(model_check_task())
    asyncio.create_task(daily_summary_task())
    logger.info(f"Starting {BOT_NAME} v5.0 with model {active_model}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
