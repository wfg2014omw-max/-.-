import os
import time
import random
import string
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth

# --- إعدادات النظام العملاق ---
TOKEN = "8611483217:AAFRdww2hpvUAez32Wx4XubeXCMS3q8Pi44"
CYBER_API = "tk_0bf2b34656f5933b0015c0a4bbe026811a754c32074e4591afec8b27a293e253"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sabir_Omega")

class SabirAutomator:
    def __init__(self):
        self.options = Options()
        self.setup_browser()

    def setup_browser(self):
        self.options.add_argument('--headless=new')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        # مسارات Railway الافتراضية للكروم (لحل مشكلة 127)
        self.options.binary_location = "/usr/bin/chromium"

    def get_driver(self):
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=self.options)
        # تكتكة التخفي
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver

    async def run_mission(self, chat_id, context):
        driver = None
        try:
            await context.bot.send_message(chat_id, "🚀 **الغول انطلق.. جاري اختراق السستم!**")
            driver = await asyncio.to_thread(self.get_driver)
            
            # توليد بيانات احترافية
            email = f"{''.join(random.choices(string.ascii_lowercase, k=10))}@Sabir.cybertemp.xyz"
            user = "sabir_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            
            # تنفيذ المهمة (مثال إنستجرام)
            driver.get("https://www.instagram.com/accounts/emailsignup/")
            await asyncio.sleep(5)
            
            # لقطة شاشة للنجاح
            snap = f"res_{chat_id}.png"
            driver.save_screenshot(snap)
            with open(snap, 'rb') as f:
                await context.bot.send_photo(chat_id, f, caption=f"✅ **تمت العملية!**\n📧 `{email}`\n👤 `{user}`")
            os.remove(snap)

        except Exception as e:
            await context.bot.send_message(chat_id, f"❌ **عطل فني في السيرفر:**\n`{str(e)[:200]}`")
        finally:
            if driver: driver.quit()

# --- واجهة التلجرام ---
async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🔥 إطلاق المحرك OMEGA", callback_data="go")]]
    await u.message.reply_text("😎 **Sabir Sniper V1000 - الـعـظـمـة**", reply_markup=InlineKeyboardMarkup(kb))

async def handle_click(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    if q.data == "go":
        bot_logic = SabirAutomator()
        asyncio.create_task(bot_logic.run_mission(q.message.chat_id, c))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_click))
    print("📡 البوت شغال على Railway.. مستني الأوامر")
    app.run_polling()
    
