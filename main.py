# -*- coding: utf-8 -*-

"""
================================================================================
🔥 SABIR OMEGA V17 - THE TITAN SUPREME EDITION (STABLE DEPLOYMENT + G4F AI)
================================================================================
Developer: Sabir Fathy (The Sabir Sniper)
Project: Ultimate Multi-Domain Mail & OTP Automated System & AI Assistant
Framework: Python 3.10+ / Telegram-Bot / Flask / MongoDB / G4F (GPT-4 Free)
================================================================================
"""

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
import sys
import threading
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask, jsonify

# ==========================================
# 🤖 استيراد مكتبة الذكاء الاصطناعي المجاني (G4F)
# ==========================================
import g4f

# Telegram Library Imports
from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    constants
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    Defaults
)

# ==========================================
# ⚙️ CORE CONFIGURATION & CONSTANTS
# ==========================================
TELEGRAM_TOKEN = "8265031988:AAGmjbCo7fygg7rtOGLJ2J-HVrxPnr1dT1Y"
ADMIN_ID = 5284917152
ADMIN_USERNAME = "@SabirFathy20"

# MongoDB Configuration
MONGO_URL = "mongodb+srv://Sabir_db_user:SabirFathy%4022@sabir.lmgceju.mongodb.net/sabir_omega?retryWrites=true&w=majority&appName=Sabir"
ca = certifi.where()

# API Infrastructure
API_KEY_PRIYO = "7jkmE5NM2VS6GqJ9pzlI"
API_KEY_CYBER = "tk_0bf2b34656f5933b0015c0a4bbe026811a754c32074e4591afec8b27a293e253"

# Domain Pools
DOMAINS_LIST = [
    "Sabir.crazy.hcap.ai",  
    "Sabir.loganister.com", 
    "Sabir.diddyricky.com", 
    "Sabir.Wg.rexabot.com",
    "Sabir.fruitservice.xyz",
    "Sabir.cybertemp.xyz",
    "Sabir.kmail123.com",
]

# Logging Architecture
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("sabir_system.log"), logging.StreamHandler()]
)
logger = logging.getLogger("SABIR_OMEGA_V17")

# ==========================================
# 🧠 AI MEMORY ENGINE (الذاكرة السياقية للذكاء الاصطناعي)
# ==========================================
user_chat_history = {}

def get_g4f_response(uid, prompt):
    """
    دالة للاتصال بمكتبة g4f وإدارة الذاكرة.
    """
    # تهيئة الذاكرة للمستخدم إذا لم تكن موجودة
    if uid not in user_chat_history:
        user_chat_history[uid] = [
            {"role": "system", "content": "أنت مساعد ذكي ومحترف جداً، اسمك 'صابر AI' تابع لنظام SABIR OMEGA V17. مطورك هو Sabir Sniper. مهمتك مساعدة المستخدمين والإجابة على أسئلتهم باللغة العربية وبدقة عالية."}
        ]
    
    # إضافة رسالة المستخدم للذاكرة
    user_chat_history[uid].append({"role": "user", "content": prompt})
    
    # الاحتفاظ بآخر 10 رسائل فقط (لتجنب استهلاك الذاكرة أو أخطاء الحجم)
    if len(user_chat_history[uid]) > 11:
        user_chat_history[uid] = [user_chat_history[uid][0]] + user_chat_history[uid][-10:]
        
    try:
        # استخدام موديل GPT-4 عبر g4f
        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=user_chat_history[uid],
            timeout=60
        )
        
        # إضافة رد الذكاء الاصطناعي للذاكرة
        user_chat_history[uid].append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        # في حالة الخطأ، نقوم بإزالة رسالة المستخدم الأخيرة حتى لا تفسد التسلسل
        user_chat_history[uid].pop()
        raise e

# ==========================================
# 📊 DATABASE ARCHITECTURE (MONGODB)
# ==========================================
class DatabaseManager:
    def __init__(self, uri):
        self.client = MongoClient(uri, tlsCAFile=ca)
        self.db = self.client['sabir_omega']
        self.users = self.db['users']
        self.logs = self.db['logs']
        self.tokens = self.db['tokens'] 
        self.settings = self.db['settings'] 
        self._initialize_database()

    def _initialize_database(self):
        admin = self.users.find_one({"user_id": ADMIN_ID})
        if not admin:
            self.users.insert_one({
                "user_id": ADMIN_ID,
                "username": "SabirSniper",
                "status": "active",
                "role": "admin",
                "access_type": "full",
                "domain": "Sabir.loganister.com",
                "total_mails": 0,
                "created_at": datetime.now(),
                "expire_at": None 
            })
        
        if not self.settings.find_one({"_id": "bot_status"}):
            self.settings.insert_one({"_id": "bot_status", "status": "active"})
            
        logger.info("MongoDB Engine Initialized & Connected.")

    def get_bot_status(self):
        doc = self.settings.find_one({"_id": "bot_status"})
        return doc.get("status", "active") if doc else "active"

    def set_bot_status(self, status):
        self.settings.update_one({"_id": "bot_status"}, {"$set": {"status": status}})

    def create_user_token(self, token_type="full"):
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        self.tokens.insert_one({
            "token": token,
            "type": token_type,
            "used_by": None,
            "created_at": datetime.now()
        })
        return token

    def verify_and_use_token(self, token, user_id):
        doc = self.tokens.find_one({"token": token, "used_by": None})
        if doc:
            token_type = doc.get("type", "full")
            self.tokens.update_one({"token": token}, {"$set": {"used_by": user_id, "used_at": datetime.now()}})
            expire_time = datetime.now() + timedelta(hours=24)
            self.users.update_one({"user_id": int(user_id)}, {
                "$set": {
                    "status": "active", 
                    "expire_at": expire_time,
                    "access_type": token_type
                }
            })
            return True
        return False

    def activate_user_manual(self, user_id):
        expire_time = datetime.now() + timedelta(hours=24)
        self.users.update_one({"user_id": int(user_id)}, {
            "$set": {
                "status": "active", 
                "expire_at": expire_time,
                "access_type": "full"
            }
        })

    def reset_user(self, user_id):
        self.users.update_one({"user_id": int(user_id)}, {"$set": {"status": "pending", "expire_at": None}})

    def clear_all_users(self):
        self.users.delete_many({"user_id": {"$ne": ADMIN_ID}})

    def check_expired_users(self):
        expired = self.users.find({"status": "active", "expire_at": {"$lt": datetime.now()}})
        for u in expired:
            if u['user_id'] != ADMIN_ID:
                self.reset_user(u['user_id'])

    def get_user_data(self, user_id):
        return self.users.find_one({"user_id": user_id})

    def update_status(self, user_id, status):
        self.users.update_one({"user_id": int(user_id)}, {"$set": {"status": status}})

    def set_user_role(self, user_id, role):
        self.users.update_one({"user_id": int(user_id)}, {"$set": {"role": role}})

    def update_domain(self, user_id, domain):
        self.users.update_one({"user_id": user_id}, {"$set": {"domain": domain}})

    def increment_mail_count(self, user_id):
        self.users.update_one({"user_id": user_id}, {"$inc": {"total_mails": 1}})

    def fetch_admin_panel_users(self):
        self.check_expired_users() 
        return list(self.users.find({"status": {"$in": ["active", "banned"]}}))

    def fetch_all_users_for_stats(self):
        return list(self.users.find())

    def log_action(self, user_id, action):
        self.logs.insert_one({
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.now()
        })

db = DatabaseManager(MONGO_URL)

# ==========================================
# 🛡️ WEB SERVER (PORT 8080)
# ==========================================
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "Online",
        "system": "SABIR OMEGA V17",
        "developer": "Sabir Fathy",
        "database": "MongoDB Connected",
        "ai_engine": "G4F (GPT-4 Free) Active",
        "uptime": datetime.now().strftime("%H:%M:%S")
    })

def run_web_server():
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask Server Failure: {e}")

# ==========================================
# 📡 ENGINE: MULTI-API OTP & LINK FETCHER
# ==========================================
async def get_latest_email_content(email_address):
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            if "auth2fa.com" in email_address:
                api_url = f"https://free.priyo.email/api/messages/{email_address}/{API_KEY_PRIYO}"
                response = await client.get(api_url)
            else:
                api_url = "https://api.cybertemp.xyz/getMail"
                headers = {"X-API-KEY": API_KEY_CYBER}
                params = {"email": email_address, "limit": 1}
                response = await client.get(api_url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    msg = data[0]
                    subj = str(msg.get('subject', 'No Subject'))
                    body_txt = str(msg.get('text', ''))
                    body_html = str(msg.get('html', ''))
                    
                    full_payload = f"{subj} {body_txt} {body_html}".lower()
                    clean_txt = re.sub(r'<[^>]+>', ' ', full_payload)
                    
                    links = re.findall(r'(https?://[^\s<>"]+)', full_payload)
                    verification_links = [l for l in links if any(word in l for word in ["verify", "click", "confirm", "activate", "discord"])]
                    
                    digits = re.findall(r'\b\d{4,8}\b', clean_txt)
                    current_year = str(datetime.now().year)
                    valid_otps = [d for d in digits if d not in [current_year, "2024", "2025", "2026", "94025"]]
                    
                    result_msg = ""
                    if verification_links:
                        result_msg += f"🔗 **رابط التفعيل المكتشف:**\n`{verification_links[0]}`\n\n"
                    
                    if valid_otps:
                        result_msg += f"🔢 **كود OTP (إلمس للنسخ):**\n`{valid_otps[0]}`\n\n"
                    
                    if not result_msg:
                        result_msg = f"📄 **محتوى الرسالة:**\n{clean_txt[:400]}..."
                    
                    return result_msg
            return None
        except Exception as e:
            logger.error(f"OTP Fetcher Error: {e}")
            return None

async def email_monitoring_loop(context, chat_id, email):
    for i in range(300): 
        await asyncio.sleep(4)
        content = await get_latest_email_content(email)
        if content:
            header = f"🚀 **صيد جديد يا صابر!**\n➖➖➖➖➖➖➖➖➖➖\n📧 البريد: `{email}`\n\n"
            await context.bot.send_message(chat_id, header + content, parse_mode=constants.ParseMode.MARKDOWN)
            db.increment_mail_count(chat_id)
            db.log_action(chat_id, f"Caught mail for {email}")
            return
    await context.bot.send_message(chat_id, f"⚠️ انتهت مهلة مراقبة البريد: `{email}`")

# ==========================================
# 🎮 USER INTERFACE & KEYBOARDS
# ==========================================
def get_main_menu(uid):
    user = db.get_user_data(uid)
    role = user.get('role', 'user') if user else 'user'

    keyboard = [
        ["🆕 إنشاء بريد جديد", "🔄 استرجاع بريد سابق"],
        ["🌐 تغيير الدومين", "🔐 استخراج كود 2FA"],
        ["🆔 استخراج ID الفيس بوك", "👤 بروفيلي"],
        ["🤖 الذكاء الاصطناعي", "🧹 مسح ذاكرة الذكاء"],
        ["🔎 فحص حسابات فيس بوك", "🔑 إدارة الباسوردات"]  # الأزرار الجديدة
    ]

    if uid == ADMIN_ID:
        keyboard.append(["🛠 لوحة التحكم", "📊 إحصائيات"])
        keyboard.append(["🔑 إنشاء يوزر جديد", "📢 إذاعة شاملة"])
        keyboard.append(["🛑 إيقاف للجميع", "✅ تشغيل للجميع"])
    elif role == 'reseller':
        keyboard.append(["🔑 إنشاء يوزر جديد"])
        
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_inline():
    active_banned_users = db.fetch_admin_panel_users()
    buttons = []
    
    for u in active_banned_users:
        uid = u['user_id']
        if uid == ADMIN_ID: continue  
        
        uname = u.get('username', 'Unknown')
        status = u.get('status', 'pending')
        mails = u.get('total_mails', 0)
        role = u.get('role', 'user')
        
        name_display = uname if uname != "Unknown" else f"ID:{uid}"
        icon = "✅" if status == 'active' else "⛔"
        role_icon = "⭐" if role == 'reseller' else "👤"
        
        buttons.append([InlineKeyboardButton(f"{role_icon} {icon} {name_display} | 📩 {mails}", callback_data="ignore")])
        
        control_row = []
        if status != 'active':
            control_row.append(InlineKeyboardButton(f"✅ تفعيل", callback_data=f"activate_{uid}"))
        if status != 'banned':
            control_row.append(InlineKeyboardButton(f"❌ حظر", callback_data=f"ban_{uid}"))
        control_row.append(InlineKeyboardButton(f"👁️ إخفاء", callback_data=f"hide_{uid}"))
        
        if control_row:
            buttons.append(control_row)
            
        role_row = []
        if role != 'reseller':
            role_row.append(InlineKeyboardButton(f"⭐ ترقية لموزع", callback_data=f"promote_{uid}"))
        else:
            role_row.append(InlineKeyboardButton(f"⬇️ سحب الترقية", callback_data=f"demote_{uid}"))
        buttons.append(role_row)
        
    buttons.append([InlineKeyboardButton("➕ تفعيل يدوي بالـ ID", callback_data="manual_activate")])
    buttons.append([InlineKeyboardButton("🗑 مسح جميع الأعضاء الحاليين (تصفير)", callback_data="clear_db")])
    
    return InlineKeyboardMarkup(buttons)

# ==========================================
# 🧠 CORE BOT LOGIC (HANDLERS)
# ==========================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uname = update.effective_user.username or "Unknown"
    user_info = db.get_user_data(uid)

    if not user_info:
        status = 'active' if uid == ADMIN_ID else 'pending'
        db.users.insert_one({
            "user_id": uid,
            "username": uname,
            "status": status,
            "role": "admin" if uid == ADMIN_ID else "user",
            "access_type": "full",
            "domain": "auth2fa.com",
            "total_mails": 0,
            "created_at": datetime.now(),
            "expire_at": None
        })
        user_info = db.get_user_data(uid)
        
    if user_info['status'] == 'pending' and uid != ADMIN_ID:
        await update.message.reply_text(
            "🔒 **مرحباً بك في SABIR OMEGA V17**\n\n"
            "هذا البوت مخصص للمشتركين فقط.\n\n"
            "💰 **للاشتراك بالبوت بـ 20 جنيه في اليوم (تفعيل لمدة 24 ساعة)**\n"
            "📱 **التحويل على الرقم التالي:**\n"
            "`01144381960`\n\n"
            "📸 **يرجى إرسال صورة الدفع و ID التليجرام الخاص بك إلى المطور (@SabirFathy778) لتفعيل البوت.**\n"
            "👉 **أو إذا كان لديك مفتاح تفعيل مسبقاً، أرسله الآن للبدء:**",
            parse_mode=constants.ParseMode.MARKDOWN
        )
        return

    welcome_msg = (
        f"🔥 **أهلاً بك في SABIR OMEGA V17**\n"
        f"----------------------------------\n"
        f"نظام سحب الـ OTP وروابط التفعيل الأسرع.\n\n"
        f"👤 **المطور:** Sabir Sniper\n"
        f"🧠 **الذكاء الاصطناعي:** GPT-4 Active 🚀\n"
        f"🛠 **الحالة:** متصل بـ MongoDB 🚀"
    )
    await update.message.reply_text(welcome_msg, reply_markup=get_main_menu(uid), parse_mode=constants.ParseMode.MARKDOWN)

async def message_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    msg_text = update.message.text
    if not msg_text: return

    db.check_expired_users()

    user = db.get_user_data(uid)
    if not user: return

    if user['status'] == 'pending' and uid != ADMIN_ID:
        if db.verify_and_use_token(msg_text.strip(), uid):
            await update.message.reply_text("✅ **تم تفعيل حسابك بنجاح لمدة 24 ساعة! أهلاً بك في النظام.**", reply_markup=get_main_menu(uid))
        else:
            await update.message.reply_text("❌ **المفتاح غير صحيح أو تم استخدامه من قبل. تأكد منه أو تواصل مع المطور.**")
        return

    if db.get_bot_status() == 'stopped' and uid != ADMIN_ID:
        return await update.message.reply_text("⛔ **البوت متوقف حالياً من قبل الإدارة.**")

    if user['status'] == 'banned' and uid != ADMIN_ID:
        return await update.message.reply_text("⛔ **أنت محظور من استخدام البوت.**")
        
    if user['status'] != 'active' and uid != ADMIN_ID:
        return await update.message.reply_text(
            "⛔ **حسابك غير مفعل أو انتهت صلاحيته.**\n\n"
            "💰 **للاشتراك بالبوت بـ 20 جنيه في اليوم (تفعيل لمدة 24 ساعة)**\n"
            "📱 **التحويل على الرقم:** `01144381960`\n\n"
            "📸 **يرجى إرسال صورة الدفع و ID التليجرام الخاص بك إلى المطور (@SabirFathy778) لتفعيل البوت.**\n"
            "👉 **أو أرسل مفتاح التفعيل الخاص بك هنا إذا كان متوفر لديك.**",
            parse_mode=constants.ParseMode.MARKDOWN
        )

    access_type = user.get('access_type', 'full')
    restricted_commands = ["🆕 إنشاء بريد جديد", "🌐 تغيير الدومين", "🆔 استخراج ID الفيس بوك", "🔎 فحص حسابات فيس بوك"]

    if access_type == 'restricted' and uid != ADMIN_ID and msg_text in restricted_commands:
        return await update.message.reply_text("⛔ **عذراً، نوع اشتراكك الحالي يسمح باسترجاع البريد واستخراج كود 2FA فقط.**")

    # ================= أزرار القائمة الرئيسية =================
    if msg_text == "🆕 إنشاء بريد جديد":
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        current_dom = user.get('domain', 'auth2fa.com')
        email = f"{prefix}@{current_dom}"
        await update.message.reply_text(f"📩 **بريدك الجديد:**\n`{email}`\n\n⏳ بدأت المراقبة...", parse_mode=constants.ParseMode.MARKDOWN)
        asyncio.create_task(email_monitoring_loop(context, uid, email))

    elif msg_text == "🌐 تغيير الدومين":
        buttons = [[InlineKeyboardButton(d, callback_data=f"setdom_{d}")] for d in DOMAINS_LIST]
        await update.message.reply_text("🌍 **اختر الدومين المطلوب:**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=constants.ParseMode.MARKDOWN)

    elif msg_text == "🔐 استخراج كود 2FA":
        context.user_data['sabir_state'] = 'WAIT_2FA'
        await update.message.reply_text("🔑 **أرسل كود الـ 2FA الآن:**", parse_mode=constants.ParseMode.MARKDOWN)

    elif msg_text == "🆔 استخراج ID الفيس بوك":
        context.user_data['sabir_state'] = 'WAIT_FBID'
        await update.message.reply_text("👤 **أرسل رابط الحساب المراد فحصه:**", parse_mode=constants.ParseMode.MARKDOWN)

    elif msg_text == "🔎 فحص حسابات فيس بوك":
        context.user_data['sabir_state'] = 'WAIT_FB_CHECK'
        await update.message.reply_text("🔎 **أرسل الحسابات (إيميلات أو كوكيز) لفحصها في رسالة واحدة:**", parse_mode=constants.ParseMode.MARKDOWN)

    elif msg_text == "🔑 إدارة الباسوردات":
        context.user_data['sabir_state'] = 'WAIT_ACCOUNTS_FOR_PASS'
        await update.message.reply_text("📝 **أرسل لستة الإيميلات أو اليوزرات في رسالة واحدة:**", parse_mode=constants.ParseMode.MARKDOWN)

    elif msg_text == "👤 بروفيلي":
        expire_txt = "غير محدود"
        if user.get('expire_at') and uid != ADMIN_ID:
            expire_txt = user['expire_at'].strftime("%Y-%m-%d %H:%M:%S")
            
        role_ar = "مدير" if uid == ADMIN_ID else ("موزع" if user.get('role') == 'reseller' else "عضو")
        type_ar = "كامل الصلاحيات" if access_type == 'full' else "استرجاع و 2FA فقط"
            
        profile = (
            f"👤 **معلوماتك:**\n"
            f"🆔 ID: `{user['user_id']}`\n"
            f"🌍 الدومين: `{user.get('domain', 'auth2fa.com')}`\n"
            f"📊 السحبات: `{user.get('total_mails', 0)}`\n"
            f"🛡️ الحالة: `{user['status']}`\n"
            f"💼 الرتبة: `{role_ar}`\n"
            f"🔑 نوع الاشتراك: `{type_ar}`\n"
            f"⏳ ينتهي في: `{expire_txt}`"
        )
        await update.message.reply_text(profile, parse_mode=constants.ParseMode.MARKDOWN)

    elif msg_text == "🔄 استرجاع بريد سابق":
        context.user_data['sabir_state'] = 'WAIT_RESTORE'
        await update.message.reply_text("📝 **أرسل البريد بالكامل لمراقبته:**", parse_mode=constants.ParseMode.MARKDOWN)
        
    elif msg_text == "🔑 إنشاء يوزر جديد" and (uid == ADMIN_ID or user.get('role') == 'reseller'):
        buttons = [
            [InlineKeyboardButton("🌟 يوزر عادي (كامل الصلاحيات)", callback_data="gentoken_full")],
            [InlineKeyboardButton("🔐 يوزر استرجاع و 2FA فقط", callback_data="gentoken_restricted")]
        ]
        await update.message.reply_text("🎯 **اختر نوع اليوزر المطلوب إنشاؤه:**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=constants.ParseMode.MARKDOWN)

    # ================= الذكاء الاصطناعي (G4F) =================
    elif msg_text == "🤖 الذكاء الاصطناعي":
        context.user_data['sabir_state'] = 'WAIT_AI_PROMPT'
        await update.message.reply_text("✨ **مرحباً بك في قسم الذكاء الاصطناعي!** 🤖\n(أنا صابر AI، سأقوم بالرد على أسئلتك بذكاء وفهم للسياق، تحدث معي كأنك تتحدث مع خبير..)", parse_mode=constants.ParseMode.MARKDOWN)
        
    elif msg_text == "🧹 مسح ذاكرة الذكاء":
        if uid in user_chat_history:
            del user_chat_history[uid]
        await update.message.reply_text("🧹 **تم مسح الذاكرة بنجاح!**\nالذكاء الاصطناعي الآن لا يتذكر محادثتك السابقة.", parse_mode=constants.ParseMode.MARKDOWN)

    # ================= أزرار لوحة الإدارة (للأدمن فقط) =================
    elif uid == ADMIN_ID:
        if msg_text == "🛠 لوحة التحكم":
            await update.message.reply_text("🛠 **إدارة المستخدمين النشطين:**\n(المستخدمين المنتهي وقتهم تم إخفائهم تلقائياً)", reply_markup=get_admin_inline(), parse_mode=constants.ParseMode.MARKDOWN)
            
        elif msg_text == "🛑 إيقاف للجميع":
            db.set_bot_status('stopped')
            await update.message.reply_text("⛔ **تم إيقاف البوت لجميع المستخدمين بنجاح.**", parse_mode=constants.ParseMode.MARKDOWN)
            
        elif msg_text == "✅ تشغيل للجميع":
            db.set_bot_status('active')
            await update.message.reply_text("✅ **تم إعادة تشغيل البوت لجميع المستخدمين بنجاح.**", parse_mode=constants.ParseMode.MARKDOWN)

        elif msg_text == "📊 إحصائيات":
            all_u = db.fetch_all_users_for_stats()
            stat_msg = f"📊 **الإحصائيات العامة:**\n👥 إجمالي المسجلين في القاعدة: `{len(all_u)}`\n\n**تفاصيل السحبات:**\n"
            for u in all_u:
                if u.get('status') in ['active', 'banned']:
                    stat_msg += f"👤 ID: `{u['user_id']}` | سحبات: `{u.get('total_mails', 0)}`\n"
            await update.message.reply_text(stat_msg, parse_mode=constants.ParseMode.MARKDOWN)
            
        elif msg_text == "📢 إذاعة شاملة":
            context.user_data['sabir_state'] = 'WAIT_BC'
            await update.message.reply_text("📣 **أرسل رسالة الإذاعة:**", parse_mode=constants.ParseMode.MARKDOWN)

    # ================= معالجة الحالات (States) =================
    state = context.user_data.get('sabir_state')
    admin_buttons = ["🔑 إنشاء يوزر جديد", "🛑 إيقاف للجميع", "✅ تشغيل للجميع"]
    main_buttons = ["🤖 الذكاء الاصطناعي", "🧹 مسح ذاكرة الذكاء", "🆕 إنشاء بريد جديد", "🔄 استرجاع بريد سابق", "🌐 تغيير الدومين", "🔐 استخراج كود 2FA", "🆔 استخراج ID الفيس بوك", "👤 بروفيلي", "🛠 لوحة التحكم", "📊 إحصائيات", "📢 إذاعة شاملة", "🔎 فحص حسابات فيس بوك", "🔑 إدارة الباسوردات"] + admin_buttons

    if state and msg_text not in main_buttons:
        if state == 'WAIT_2FA':
            try:
                totp = pyotp.TOTP(msg_text.replace(" ", "")).now()
                await update.message.reply_text(f"🔐 **الكود الحالي:** `{totp}`", parse_mode=constants.ParseMode.MARKDOWN)
            except: 
                await update.message.reply_text("❌ خطأ في الكود.")

        elif state == 'WAIT_FBID':
            found = re.findall(r'(?:id=|/)([0-9]{10,})', msg_text)
            if found: 
                await update.message.reply_text(f"✅ **ID المستخرج:** `{found[0]}`", parse_mode=constants.ParseMode.MARKDOWN)
            else: 
                await update.message.reply_text("❌ لم يتم العثور على ID.")

        elif state == 'WAIT_RESTORE':
            if "@" in msg_text:
                await update.message.reply_text(f"⏳ بدأت مراقبة: `{msg_text}`", parse_mode=constants.ParseMode.MARKDOWN)
                asyncio.create_task(email_monitoring_loop(context, uid, msg_text))

        elif state == 'WAIT_FB_CHECK':
            processing_msg = await update.message.reply_text("⏳ **جاري فحص الحسابات...**", parse_mode=constants.ParseMode.MARKDOWN)
            accounts = msg_text.split('\n')
            active = []
            blocked = []
            
            # هنا يمكنك وضع دالة أو API الفحص الحقيقي الخاص بك (لأن فيس بوك يحتاج تخطي و API خارجي)
            # حالياً قمت بعمل محاكاة للفحص لتوضيح الفكرة ولعمل الواجهة كما طلبت
            for acc in accounts:
                if acc.strip():
                    # محاكاة: إذا كان الحساب يحتوي على نقطتين (إيميل:باس) أو كوكيز نعتبره للمثال
                    if "c_user=" in acc or ":" in acc: 
                        active.append(acc.strip())
                    else:
                        blocked.append(acc.strip())
            
            res = f"✅ **Active ({len(active)}):**\n"
            if active:
                res += "`" + "`\n`".join(active) + "`\n\n"
            else:
                res += "لا يوجد\n\n"
                
            res += f"❌ **Blocked ({len(blocked)}):**\n"
            if blocked:
                res += "`" + "`\n`".join(blocked) + "`"
            else:
                res += "لا يوجد"
                
            await context.bot.delete_message(chat_id=uid, message_id=processing_msg.message_id)
            await update.message.reply_text(res, parse_mode=constants.ParseMode.MARKDOWN)
            context.user_data['sabir_state'] = None

        elif state == 'WAIT_ACCOUNTS_FOR_PASS':
            context.user_data['temp_accounts'] = msg_text.split('\n')
            context.user_data['sabir_state'] = 'WAIT_PASS_FOR_ACCOUNTS'
            await update.message.reply_text("🔑 **ممتاز، الآن أرسل الباسورد الذي تريد إضافته لجميع هذه الحسابات:**", parse_mode=constants.ParseMode.MARKDOWN)

        elif state == 'WAIT_PASS_FOR_ACCOUNTS':
            accounts = context.user_data.get('temp_accounts', [])
            password = msg_text.strip()
            result = []
            for acc in accounts:
                if acc.strip():
                    # تنظيف الحساب من أي باسورد قديم وإضافة الباسورد الجديد
                    clean_acc = acc.split(':')[0].strip()
                    result.append(f"{clean_acc}:{password}")
            
            final_text = "✅ **تمت إضافة الباسورد بنجاح:**\n\n"
            final_text += "`" + "`\n`".join(result) + "`"
            
            await update.message.reply_text(final_text, parse_mode=constants.ParseMode.MARKDOWN)
            context.user_data['sabir_state'] = None
            context.user_data['temp_accounts'] = None

        elif state == 'WAIT_BC' and uid == ADMIN_ID:
            users = db.fetch_all_users_for_stats()
            for u in users:
                try: 
                    await context.bot.send_message(u['user_id'], f"📢 **إشعار إداري:**\n\n{msg_text}", parse_mode=constants.ParseMode.MARKDOWN)
                except: 
                    pass
            await update.message.reply_text("✅ تمت الإذاعة.")

        elif state == 'WAIT_MANUAL_ACTIVATE' and uid == ADMIN_ID:
            if msg_text.isdigit():
                db.activate_user_manual(int(msg_text))
                await update.message.reply_text(f"✅ تم تفعيل `{msg_text}` لمدة 24 ساعة.", parse_mode=constants.ParseMode.MARKDOWN)
        
        # معالجة استجابة الذكاء الاصطناعي (G4F)
        elif state == 'WAIT_AI_PROMPT':
            processing_msg = await update.message.reply_text("⏳ **جاري التفكير وتجهيز الرد...**", parse_mode=constants.ParseMode.MARKDOWN)
            try:
                # استخدام asyncio.to_thread لتشغيل g4f في مسار خلفي دون إيقاف البوت
                ai_reply = await asyncio.to_thread(get_g4f_response, uid, msg_text)
                
                # تقسيم الرسالة إذا كانت طويلة جداً (لتفادي خطأ الطول في تيليجرام)
                if len(ai_reply) > 4000:
                    for i in range(0, len(ai_reply), 4000):
                        await update.message.reply_text(ai_reply[i:i+4000])
                else:
                    await update.message.reply_text(ai_reply)
                    
            except Exception as e:
                logger.error(f"G4F AI Error: {e}")
                await update.message.reply_text("❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي. ربما الخادم مضغوط، جرب مرة تانية بعد ثوانٍ.")
            finally:
                # مسح رسالة "جاري التفكير"
                try: await context.bot.delete_message(chat_id=uid, message_id=processing_msg.message_id)
                except: pass

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    uid = query.from_user.id
    user = db.get_user_data(uid)

    if data.startswith("setdom_"):
        db.update_domain(uid, data.split("_")[1])
        await query.answer("تم التحديث")
        await query.edit_message_text(f"✅ الدومين الحالي: `{data.split('_')[1]}`", parse_mode=constants.ParseMode.MARKDOWN)
        
    elif data.startswith("gentoken_"):
        role = user.get('role', 'user')
        if uid == ADMIN_ID or role == 'reseller':
            token_type = data.split("_")[1] 
            new_token = db.create_user_token(token_type)
            type_text = "يوزر عادي كامل" if token_type == "full" else "استرجاع و 2FA فقط"
            await query.answer("تم إنشاء المفتاح")
            await query.edit_message_text(
                f"✅ **تم إنشاء يوزر تفعيل ({type_text}):**\n\n"
                f"`{new_token}`\n\n"
                f"(صالح لمدة 24 ساعة - يستخدم لمرة واحدة فقط)", 
                parse_mode=constants.ParseMode.MARKDOWN
            )

    elif data.startswith("activate_") and uid == ADMIN_ID:
        target = data.split("_")[1]
        db.activate_user_manual(target)
        await query.answer("تم التفعيل")
        await query.edit_message_text(f"✅ تم تفعيل المستخدم `{target}` لمدة 24 ساعة.", parse_mode=constants.ParseMode.MARKDOWN)
        try: await context.bot.send_message(int(target), "🚀 مبروك! تم تفعيل حسابك بنجاح لمدة 24 ساعة من قبل الإدارة.")
        except: pass
        
    elif data.startswith("ban_") and uid == ADMIN_ID:
        target = data.split("_")[1]
        db.update_status(target, 'banned')
        await query.answer("تم الحظر")
        await query.edit_message_text(f"❌ تم حظر المستخدم `{target}`", parse_mode=constants.ParseMode.MARKDOWN)
        
    elif data.startswith("hide_") and uid == ADMIN_ID:
        target = data.split("_")[1]
        db.reset_user(target)
        await query.answer("تم الإخفاء والتصفير")
        await query.edit_message_text(f"👁️ تم إخفاء المستخدم `{target}`، الآن هو يظهر كأنه مستخدم جديد غير مفعل.", parse_mode=constants.ParseMode.MARKDOWN)
        try: await context.bot.send_message(int(target), "⚠️ **تم إنهاء جلستك.**\nبرجاء إرسال مفتاح تفعيل جديد للبدء.", parse_mode=constants.ParseMode.MARKDOWN)
        except: pass

    elif data.startswith("promote_") and uid == ADMIN_ID:
        target = data.split("_")[1]
        db.set_user_role(target, 'reseller')
        await query.answer("تمت الترقية لموزع")
        await query.edit_message_text(f"⭐ تم ترقية المستخدم `{target}` إلى موزع.", parse_mode=constants.ParseMode.MARKDOWN)
        try: 
            await context.bot.send_message(int(target), "🎉 **تمت ترقيتك إلى موزع!**\nالآن يمكنك إنشاء يوزرات تفعيل للأعضاء من خلال القائمة الخاصة بك.", reply_markup=get_main_menu(int(target)), parse_mode=constants.ParseMode.MARKDOWN)
        except: pass

    elif data.startswith("demote_") and uid == ADMIN_ID:
        target = data.split("_")[1]
        db.set_user_role(target, 'user')
        await query.answer("تم سحب الترقية")
        await query.edit_message_text(f"⬇️ تم سحب صلاحية الموزع من المستخدم `{target}`.", parse_mode=constants.ParseMode.MARKDOWN)
        try: 
            await context.bot.send_message(int(target), "⚠️ **تم سحب صلاحية الموزع منك.**", reply_markup=get_main_menu(int(target)), parse_mode=constants.ParseMode.MARKDOWN)
        except: pass

    elif data == "clear_db" and uid == ADMIN_ID:
        db.clear_all_users()
        await query.answer("تم مسح القاعدة")
        await query.edit_message_text("🗑 **تم مسح جميع الأعضاء الحاليين وبدء نظام جديد بالكامل.**\n(الآن يمكنك توزيع يوزرات جديدة ليظهر الأعضاء من جديد)", parse_mode=constants.ParseMode.MARKDOWN)

    elif data == "manual_activate" and uid == ADMIN_ID:
        context.user_data['sabir_state'] = 'WAIT_MANUAL_ACTIVATE'
        await query.message.reply_text("👤 **أرسل الـ ID لتفعيله لمدة 24 ساعة فوراً (بدون يوزر):**", parse_mode=constants.ParseMode.MARKDOWN)

# ==========================================
# 🚀 STARTUP BOOTLOADER
# ==========================================
if __name__ == '__main__':
    # Start Flask Web Server
    Thread(target=run_web_server, daemon=True).start()

    # Build Telegram Bot
    defaults = Defaults(parse_mode=constants.ParseMode.MARKDOWN)
    sabir_app = ApplicationBuilder().token(TELEGRAM_TOKEN).defaults(defaults).build()

    # Handlers
    sabir_app.add_handler(CommandHandler("start", start_command))
    sabir_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_dispatcher))
    sabir_app.add_handler(CallbackQueryHandler(handle_callbacks))

    print("[*] SABIR OMEGA V17 IS READY WITH MONGODB & G4F AI (GPT-4) ASSISTANT...")
    
    # Run Polling
    sabir_app.run_polling(drop_pending_updates=True)
            
