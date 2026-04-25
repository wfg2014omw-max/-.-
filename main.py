# -*- coding: utf-8 -*-
import g4f
from pymongo import MongoClient
import certifi
import os
import re
import json
import time
import random
import string
import pyotp
import logging
import asyncio
import httpx
import threading
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, jsonify

# مكتبات السيلينيوم الجديدة
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, Defaults

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
TELEGRAM_TOKEN = "8207864733:AAE_TvQ9T-PdZ6zLA1OyN4E4oDHKko4pIgs"
ADMIN_ID = 5284917152
MONGO_URL = "mongodb+srv://Sabir_db_user:SabirFathy%4022@sabir.lmgceju.mongodb.net/sabir_omega?retryWrites=true&w=majority&appName=Sabir"
ca = certifi.where()

# API Keys
API_KEY_PRIYO = "7jkmE5NM2VS6GqJ9pzlI"
API_KEY_CYBER = "tk_0bf2b34656f5933b0015c0a4bbe026811a754c32074e4591afec8b27a293e253"

DOMAINS_LIST = ["auth2fa.com", "Sabir.funnylolcap.com", "Sabir.picturehostel.com"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SABIR_SYSTEM")

# ==========================================
# 📊 DATABASE & AI
# ==========================================
client = MongoClient(MONGO_URL, tlsCAFile=ca)
db = client['sabir_omega']

def get_user_data(uid):
    return db.users.find_one({"user_id": uid})

# (دالة الذكاء الاصطناعي g4f ودالة سحب الإيميلات موجودة مسبقاً في كودك)

# ==========================================
# 🟦 SELENIUM ENGINE: FB AUTO REGISTER
# ==========================================
async def fb_auto_register_task(update, context, email, fname, lname, pwd):
    chat_id = update.effective_user.id
    
    # إعدادات المتصفح
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # فعلها لو عايز المتصفح يشتغل في الخلفية بدون ما تشوفه
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = None
    try:
        await context.bot.send_message(chat_id, "🌐 جاري تشغيل المحرك وفتح فيسبوك...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # 1. الدخول لصفحة التسجيل (نسخة الموبايل أسهل في التخطي)
        driver.get("https://m.facebook.com/reg/")
        wait = WebDriverWait(driver, 20)

        # 2. ملء البيانات
        wait.until(EC.presence_of_element_located((By.NAME, "firstname"))).send_keys(fname)
        driver.find_element(By.NAME, "lastname").send_keys(lname)
        
        # اختيار تاريخ ميلاد عشوائي
        driver.find_element(By.NAME, "birthday_day").send_keys(str(random.randint(1, 28)))
        driver.find_element(By.NAME, "birthday_month").send_keys(str(random.randint(1, 12)))
        driver.find_element(By.NAME, "birthday_year").send_keys(str(random.randint(1990, 2000)))
        
        # اختيار الجنس (ذكر)
        driver.find_elements(By.NAME, "sex")[1].click()
        
        # إدخال البريد والباسورد
        driver.find_element(By.NAME, "reg_email__").send_keys(email)
        driver.find_element(By.NAME, "reg_passwd__").send_keys(pwd)
        
        # الضغط على زر التسجيل
        driver.find_element(By.NAME, "submit").click()
        
        await context.bot.send_message(chat_id, f"📧 تم إرسال البيانات.. في انتظار وصول كود التأكيد على بريد: `{email}`")

        # 3. محاولة جلب الكود من السيستم بتاعك (ننتظر 2 دقيقة)
        otp_code = None
        for _ in range(20): 
            await asyncio.sleep(10)
            content = await get_latest_email_content(email) # الدالة الأصلية في كودك
            if content:
                match = re.search(r'\b\d{5}\b', content)
                if match:
                    otp_code = match.group(0)
                    break
        
        if otp_code:
            await context.bot.send_message(chat_id, f"✅ تم استلام الكود تلقائياً: `{otp_code}`. جاري التأكيد...")
            # إدخال الكود في الخانة المخصصة
            code_input = wait.until(EC.presence_of_element_located((By.NAME, "code")))
            code_input.send_keys(otp_code)
            driver.find_element(By.NAME, "confirm").click()
            
            await asyncio.sleep(5)
            await context.bot.send_message(chat_id, f"🎉 **تم إنشاء الحساب بنجاح!**\n👤 الاسم: {fname} {lname}\n📧 البريد: `{email}`\n🔑 الباسورد: `{pwd}`")
        else:
            await context.bot.send_message(chat_id, "❌ فشل استلام كود التأكيد في الوقت المحدد. يرجى محاولة تأكيده يدوياً.")

    except Exception as e:
        logger.error(f"FB Error: {e}")
        await context.bot.send_message(chat_id, f"❌ حدث خطأ أثناء الإنشاء: {str(e)[:100]}")
    finally:
        if driver:
            driver.quit()

# ==========================================
# 🎮 DISPATCHER (LOGIC UPGRADE)
# ==========================================
async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg_text = update.message.text
    state = context.user_data.get('sabir_state')
    user = get_user_data(uid)

    # ... (الأوامر الأساسية) ...

    if msg_text == "🟦 إنشاء حساب فيس تلقائي":
        context.user_data['sabir_state'] = 'FB_WAIT_FNAME'
        await update.message.reply_text("🟦 **خدمة الإنشاء التلقائي**\nأرسل الاسم الأول (First Name):")

    elif state == 'FB_WAIT_FNAME':
        context.user_data['temp_fname'] = msg_text
        context.user_data['sabir_state'] = 'FB_WAIT_LNAME'
        await update.message.reply_text("أرسل اسم العائلة (Last Name):")

    elif state == 'FB_WAIT_LNAME':
        context.user_data['temp_lname'] = msg_text
        context.user_data['sabir_state'] = 'FB_WAIT_PWD'
        await update.message.reply_text("أرسل الباسورد المطلوب للحساب:")

    elif state == 'FB_WAIT_PWD':
        pwd = msg_text
        fname = context.user_data['temp_fname']
        lname = context.user_data['temp_lname']
        
        # إنشاء بريد عشوائي من السيستم
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        email = f"{prefix}@{user.get('domain', 'auth2fa.com')}"
        
        await update.message.reply_text(f"⏳ بدأت العملية لإنشاء حساب باسم: {fname} {lname}\nالبريد المستخدم: `{email}`")
        
        # تشغيل السيلينيوم في الخلفية
        asyncio.create_task(fb_auto_register_task(update, context, email, fname, lname, pwd))
        context.user_data['sabir_state'] = None

    # ... (بقية معالجة الرسائل والذكاء الاصطناعي) ...

# ==========================================
# 🚀 MAIN MENU UPDATE
# ==========================================
def get_main_menu(uid):
    keyboard = [
        ["🆕 إنشاء بريد جديد", "🔄 استرجاع بريد سابق"],
        ["🌐 تغيير الدومين", "🔐 استخراج كود 2FA"],
        ["🟦 إنشاء حساب فيس تلقائي", "🤖 الذكاء الاصطناعي"], # الزر الجديد هنا
        ["👤 بروفيلي", "🗂 إدارة الحسابات المستخدمة"],
        ["🔑 إدارة الباسوردات", "🧹 مسح ذاكرة الذكاء"]
    ]
    # ... (إضافة أزرار الأدمن) ...
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# (تكملة الكود هي نفسها في الـ Bot Loader والـ Flask server)
