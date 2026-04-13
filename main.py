import time
import random
import re
import requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from faker import Faker

fake = Faker()

# --- وظائف الإيميل المؤقت ---
def get_temp_email():
    """توليد إيميل مؤقت باستخدام 1secmail"""
    username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=10))
    domain = "1secmail.com"
    return f"{username}@{domain}", username, domain

def wait_for_otp(username, domain):
    """انتظار وصول كود التفعيل من إنستجرام"""
    print(f"Checking inbox for {username}@{domain}...")
    api_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
    
    for _ in range(24): # محاولة لمدة دقيقتين (كل 5 ثواني محاولة)
        response = requests.get(api_url).json()
        if response:
            msg_id = response[0]['id']
            msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
            msg_content = requests.get(msg_url).json()
            # البحث عن 6 أرقام في نص الرسالة
            code = re.findall(r'\b\d{6}\b', msg_content['body'])
            if code:
                print(f"Found OTP: {code[0]}")
                return code[0]
        time.sleep(5)
    return None

# --- السكربت الأساسي ---
def run_bot():
    email, user, dom = get_temp_email()
    full_name = fake.name()
    insta_username = user + str(random.randint(10, 99))
    password = "SafePassword123!" # يفضل تخليها متغيرة

    with sync_playwright() as p:
        # ملاحظة: في Railway لازم headless=True
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        stealth_sync(page)

        print(f"Starting registration for: {email}")
        page.goto("https://www.instagram.com/accounts/emailsignup/")
        
        # ملء البيانات مع تأخيرات عشوائية (Human-like behavior)
        page.wait_for_selector('input[name="emailOrPhone"]')
        page.type('input[name="emailOrPhone"]', email, delay=random.randint(100, 200))
        page.type('input[name="fullName"]', full_name, delay=random.randint(100, 200))
        page.type('input[name="username"]', insta_username, delay=random.randint(100, 200))
        page.type('input[name="password"]', password, delay=random.randint(100, 200))
        
        # الضغط على زر التسجيل
        page.click('button[type="submit"]')
        
        # هنا المفروض تختار تاريخ الميلاد (خطوة إضافية)
        # وبعدها هيطلب كود الـ OTP
        
        otp_code = wait_for_otp(user, dom)
        if otp_code:
            print(f"Entering OTP: {otp_code}")
            # كود ملء خانة الـ OTP هنا
        else:
            print("Failed to get OTP.")

        browser.close()

if __name__ == "__main__":
    run_bot()
    
