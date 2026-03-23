import requests
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- الإعدادات ---
PROFILE_IDS = ["k1apg3yu"]
ADS_API_BASE = "http://local.adspower.net:50325/api/v1/browser"
MY_SITE = "tgcryptobot.com"
KEYWORDS = ["Tg Crypto Bot", "بوت تحليل العملات الرقمية", "بوت تحليل العملات"]

async def super_clean(page):
    """مسح السجل والكوكيز والتخزين المحلي من داخل المتصفح مباشرة"""
    try:
        context = page.context
        await context.clear_cookies()
        await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        print("🧹 تم تنظيف الكوكيز والتخزين المحلي يدوياً.")
    except: pass

async def random_human_action(page):
    """تحركات عشوائية غير مكررة (سكرول، تحريك ماوس، توقف)"""
    actions = ["scroll_down", "scroll_up", "mouse_move", "wait"]
    action = random.choice(actions)
    
    if action == "scroll_down":
        await page.mouse.wheel(0, random.randint(200, 600))
    elif action == "scroll_up":
        await page.mouse.wheel(0, random.randint(-100, -300))
    elif action == "mouse_move":
        await page.mouse.move(random.randint(100, 1000), random.randint(100, 600), steps=20)
    elif action == "wait":
        await asyncio.sleep(random.uniform(2, 5))

async def perform_visit(profile_id):
    try:
        # 1. فتح المتصفح مع بارامترات إضافية للتنظيف
        start_url = f"{ADS_API_BASE}/start?user_id={profile_id}&clear_cache=1&open_tabs=1"
        response = requests.get(start_url).json()
        if response["code"] != 0: return

        ws_endpoint = response["data"]["ws"]["puppeteer"]

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            
            # إغلاق كل الصفحات القديمة فوراً
            for pge in context.pages:
                if pge != context.pages[0]: await pge.close()
            
            page = context.pages[0]
            await super_clean(page) # تنظيف يدوي إضافي
            
            # 2. التوجه لجوجل (بشكل عشوائي)
            await page.goto(random.choice(["https://www.google.com", "https://www.google.com.sa"]))
            await asyncio.sleep(random.uniform(3, 6))

            # 3. البحث
            keyword = random.choice(KEYWORDS)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']")
            
            # محاكاة خطأ مطبعي وتصحيحه (حركة بشرية بامتياز)
            await search_box.click()
            for char in keyword:
                await page.keyboard.type(char, delay=random.randint(150, 400))
            
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")

            # 4. البحث في الصفحات (حتى الصفحة 5)
            found = False
            for p_num in range(1, 6):
                print(f"🧐 فحص الصفحة {p_num}...")
                
                # تنفيذ تحركات عشوائية قبل البحث عن الرابط
                for _ in range(random.randint(2, 5)):
                    await random_human_action(page)

                link_selector = f"a[href*='{MY_SITE}']"
                if await page.locator(link_selector).count() > 0:
                    print(f"🎯 وجدته في الصفحة {p_num}!")
                    link = page.locator(link_selector).first
                    await link.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(2, 5))
                    await link.click()
                    found = True
                    break
                else:
                    # ننتقل للتالية
                    next_btn = page.locator("a#pnnext").first
                    if await next_btn.is_visible():
                        await next_btn.click()
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(random.uniform(3, 5))
                    else: break

            # 5. التفاعل داخل الموقع (تغيير السيناريو في كل مرة)
            if found:
                stay_limit = time.time() + random.randint(300, 600)
                while time.time() < stay_limit:
                    await random_human_action(page)
                    # أحياناً نضغط على رابط داخلي، وأحياناً لا (عشوائية)
                    if random.random() > 0.85:
                        inner = await page.query_selector_all(f"a[href*='{MY_SITE}']")
                        if inner: await random.choice(inner).click()
                    await asyncio.sleep(random.uniform(10, 30))

            # 6. الإغلاق النهائي
            await browser.close()
            requests.get(f"{ADS_API_BASE}/stop?user_id={profile_id}")
            print(f"✅ تم الانتهاء وتنظيف الجلسة للبروفايل {profile_id}")

    except Exception as e:
        print(f"❌ خطأ: {e}")

async def main():
    print("🚀 بوت زينو الخفي (النسخة البشرية القصوى) انطلق!")
    while True:
        await perform_visit(PROFILE_IDS[0])
        # استراحة عشوائية طويلة جداً لكسر أي نمط تكتشفه جوجل
        sleep_time = random.randint(900, 2400) 
        print(f"😴 سأنام لمدة {sleep_time//60} دقيقة لتمويه الرادار...")
        await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main())
