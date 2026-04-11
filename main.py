"""
SABIR SNIPER OMEGA - VERSION 500+
PROFEESIONAL AUTOMATION SYSTEM
TARGET: RAILWAY DEPLOYMENT
"""

import os
import time
import random
import string
import logging
import asyncio
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict

# استيراد مكتبات سيلينيوم الاحترافية
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# مكتبات التمويه وتخطي الحماية
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# مكتبات التلجرام
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# =================================================================
# 1. نظام إدارة السجلات (Advanced Logging System)
# =================================================================
class SabirLogger:
    @staticmethod
    def setup():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler("sabir_sniper.log", encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("SabirSniper")

logger = SabirLogger.setup()

# =================================================================
# 2. الإعدادات والبيانات الحساسة (Config Management)
# =================================================================
class Config:
    TOKEN = "8611483217:AAFRdww2hpvUAez32Wx4XubeXCMS3q8Pi44"
    CYBER_API = "tk_0bf2b34656f5933b0015c0a4bbe026811a754c32074e4591afec8b27a293e253"
    DOMAIN = "Sabir.cybertemp.xyz"
    INSTAGRAM_SIGNUP_URL = "https://www.instagram.com/accounts/emailsignup/"
    DEFAULT_TIMEOUT = 45
    
    # قائمة بأسماء عربية وأجنبية لجعل الحساب يبدو حقيقياً
    FULL_NAMES = ["Sabir Ahmed", "Omar Khaled", "Ziad Mahmoud", "Alex Thompson", "Marco Rossi"]

# =================================================================
# 3. محرك توليد البيانات (Data Synthesis Engine)
# =================================================================
class DataGenerator:
    @staticmethod
    def generate_username(length=8):
        prefix = random.choice(["pro_", "real_", "user_", "it_"])
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        return f"{prefix}{random_str}"

    @staticmethod
    def generate_password():
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "Sbr" + "".join(random.choices(chars, k=10))

    @staticmethod
    def generate_email():
        random_prefix = ''.join(random.choices(string.ascii_lowercase, k=9))
        return f"{random_prefix}@{Config.DOMAIN}"

# =================================================================
# 4. محرك البروكسي (Proxy Rotation System)
# =================================================================
class ProxyManager:
    def __init__(self):
        self.proxy_list = []
        self.current_proxy = None

    async def fetch_fresh_proxies(self):
        """جلب بروكسيات جديدة لتجنب الحظر"""
        try:
            # مثال لجلب بروكسيات مجانية (يمكن استبداله ببروكسيات مدفوعة لزيادة القوة)
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self.proxy_list = response.text.splitlines()
                logger.info(f"✅ تم تحديث قائمة البروكسيات: {len(self.proxy_list)} بروكسي متاح.")
        except Exception as e:
            logger.error(f"❌ فشل جلب البروكسيات: {e}")

    def get_random_proxy(self):
        if self.proxy_list:
            self.current_proxy = random.choice(self.proxy_list)
            return self.current_proxy
        return None

# =================================================================
# 5. محرك المتصفح (The Stealth Browser Engine)
# =================================================================
class BrowserEngine:
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.ua = UserAgent()

    def create_driver(self):
        """إنشاء متصفح مع تكتيكات التخفي العالية"""
        chrome_options = Options()
        chrome_options.add_argument("--headless") # تشغيل بدون واجهة في Railway
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"user-agent={self.ua.random}")
        
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server=http://{self.proxy}')

        # تثبيت وتدشين الدرايفر تلقائياً
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # تفعيل Stealth mode لإخفاء بصمة سيلينيوم
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        return driver

# =================================================================
# 6. منطق العمليات الأساسي (The Core Automation Logic)
# =================================================================
class InstagramSniper:
    def __init__(self, chat_id, context):
        self.chat_id = chat_id
        self.context = context
        self.driver = None
        self.email = DataGenerator.generate_email()
        self.username = DataGenerator.generate_username()
        self.password = DataGenerator.generate_password()

    async def report(self, message):
        """إرسال تقرير حالة للمستخدم عبر التلجرام"""
        logger.info(f"Reporting to {self.chat_id}: {message}")
        await self.context.bot.send_message(self.chat_id, f"📡 {message}", parse_mode="Markdown")

    async def capture_screen(self, label):
        """أخذ لقطة شاشة للعملية وحفظها كدليل"""
        filename = f"snap_{self.chat_id}_{label}.png"
        try:
            self.driver.save_screenshot(filename)
            with open(filename, 'rb') as photo:
                await self.context.bot.send_photo(self.chat_id, photo, caption=f"📸 لقطة: {label}")
            os.remove(filename)
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")

    async def execute(self, proxy=None):
        """تنفيذ العملية بالكامل بتكتيك عالي"""
        try:
            engine = BrowserEngine(proxy)
            self.driver = await asyncio.to_thread(engine.create_driver)
            wait = WebDriverWait(self.driver, Config.DEFAULT_TIMEOUT)

            await self.report(f"🚀 **بدء العملية...**\n📧 البريد: `{self.email}`\n👤 المستخدم: `{self.username}`")

            # 1. الدخول للموقع
            await asyncio.to_thread(self.driver.get, Config.INSTAGRAM_SIGNUP_URL)
            await asyncio.sleep(random.uniform(5, 8)) # تأخير بشري عشوائي

            # 2. ملء البيانات (التكتيك: الكتابة ببطء محاكي للبشر)
            inputs = {
                "emailOrPhone": self.email,
                "fullName": random.choice(Config.FULL_NAMES),
                "username": self.username,
                "password": self.password
            }

            for name, value in inputs.items():
                element = wait.until(EC.presence_of_element_located((By.NAME, name)))
                for char in value: # كتابة حرف حرف
                    element.send_keys(char)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                logger.info(f"Field {name} filled.")

            # 3. ضغط زر التسجيل
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            await self.report("⏳ تم إرسال البيانات.. في انتظار شاشة تاريخ الميلاد")
            await asyncio.sleep(7)

            # 4. معالجة تاريخ الميلاد
            try:
                month_select = Select(wait.until(EC.presence_of_element_located((By.XPATH, "//select[@title='Month:']"))))
                month_select.select_by_index(random.randint(1, 12))
                
                day_select = Select(self.driver.find_element(By.XPATH, "//select[@title='Day:']"))
                day_select.select_by_index(random.randint(1, 28))
                
                year_select = Select(self.driver.find_element(By.XPATH, "//select[@title='Year:']"))
                year_select.select_by_value(str(random.randint(1994, 2003)))
                
                next_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'التالي')]")
                next_btn.click()
                await self.report("✅ تم اختيار التاريخ.. بانتظار الكود")
            except Exception as e:
                logger.warning(f"Birthday step issue: {e}")

            # 5. مراقبة الكود (Polling)
            await self.monitor_email_for_code()

        except Exception as e:
            await self.report(f"❌ **عطل تقني:**\n`{str(e)[:200]}`")
        finally:
            if self.driver:
                self.driver.quit()

    async def monitor_email_for_code(self):
        """نظام مراقبة البريد الاحترافي"""
        start_time = time.time()
        await self.report("🔍 جاري فحص بريد صابر بحثاً عن الكود...")
        
        while time.time() - start_time < 300: # محاولة لمدة 5 دقائق
            try:
                res = requests.get(
                    f"https://api.cybertemp.xyz/getMail?email={self.email}",
                    headers={"X-API-KEY": Config.CYBER_API},
                    timeout=10
                )
                if res.status_code == 200 and res.json():
                    data = res.json()
                    code_content = data[0].get('text', 'No Text Found')
                    await self.context.bot.send_message(self.chat_id, f"📩 **الكود وصل يا صابر!**\n\n`{code_content[:400]}`")
                    return
            except Exception as e:
                logger.error(f"Mail check error: {e}")
            
            await asyncio.sleep(20) # انتظار قبل المحاولة القادمة
        
        await self.report("⚠️ انتهت المدة ولم يصل الكود. قد يكون الحساب محظوراً أو البريد بطيئاً.")

# =================================================================
# 7. واجهة التلجرام (Telegram Command Interface)
# =================================================================
proxy_hub = ProxyManager()

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🔥 **Sabir Sniper OMEGA V500**\n"
        "المنظومة الاحترافية تعمل الآن على سيرفرات Railway.\n\n"
        "**المميزات:**\n"
        "• نظام OOP لإدارة العمليات.\n"
        "• تخطي الحماية بـ Stealth Mode.\n"
        "• تدوير البروكسيات آلياً.\n"
        "• لقطات شاشة حية لكل خطوة."
    )
    keyboard = [
        [InlineKeyboardButton("🚀 إطلاق الهجوم المنسق", callback_data="launch")],
        [InlineKeyboardButton("🔄 تحديث البروكسيات", callback_data="refresh_proxy")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def callback_worker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "launch":
        # اختيار بروكسي عشوائي قبل البدء
        proxy = proxy_hub.get_random_proxy()
        sniper = InstagramSniper(query.message.chat_id, context)
        asyncio.create_task(sniper.execute(proxy))
        
    elif query.data == "refresh_proxy":
        await context.bot.send_message(query.message.chat_id, "🔄 جاري البحث عن بروكسيات طازجة...")
        await proxy_hub.fetch_fresh_proxies()
        await context.bot.send_message(query.message.chat_id, f"✅ جاهز! عدد البروكسيات: {len(proxy_hub.proxy_list)}")

# =================================================================
# 8. نقطة انطلاق النظام (System Entry Point)
# =================================================================
def main():
    print("""
    #################################################
    #        SABIR SNIPER OMEGA V500 INITIALIZED    #
    #        STATUS: OPERATIONAL ON RAILWAY         #
    #################################################
    """)
    
    # بناء التطبيق
    app = ApplicationBuilder().token(Config.TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(callback_worker))
    
    # تشغيل البوت بنظام Polling (مناسب لـ Railway Worker)
    app.run_polling()

if __name__ == "__main__":
    main()
  
