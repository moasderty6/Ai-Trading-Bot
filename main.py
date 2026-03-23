import requests
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- الإعدادات الخاصة بزينو ---
PROFILE_IDS = ["k1apg3yu"] #
ADS_API_BASE = "http://local.adspower.net:50325/api/v1/browser"
MY_SITE = "tgcryptobot.com" #
KEYWORDS = ["Tg Crypto Bot", "بوت تحليل العملات الرقمية", "بوت تحليل العملات"] #

async def human_scroll(page):
    """محاكاة سكرول بشري حقيقي (سرعات متغيرة وتوقف للقراءة)"""
    for _ in range(random.randint(3, 7)):
        scroll_amount = random.randint(300, 800)
        # سكرول لأسفل
        await page.mouse.wheel(0, scroll_amount)
        await asyncio.sleep(random.uniform(1.5, 4.0)) # توقف كأنه عم يقرأ
        # سكرول خفيف لأعلى (كأنه رجع يقرأ سطر)
        if random.random() > 0.7:
            await page.mouse.wheel(0, -200)
            await asyncio.sleep(1)

async def human_mouse_move(page):
    """تحريك الماوس بشكل عشوائي فوق العناصر"""
    width, height = 1280, 720
    for _ in range(random.randint(2, 5)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        await page.mouse.move(x, y, steps=random.randint(10, 30))
        await asyncio.sleep(random.uniform(0.5, 1.5))

async def perform_visit(profile_id):
    try:
        # تشغيل المتصفح من AdsPower
        start_url = f"{ADS_API_BASE}/start?user_id={profile_id}&clear_cache=1"
        response = requests.get(start_url).json()
        if response["code"] != 0: return
        
        ws_endpoint = response["data"]["ws"]["puppeteer"]

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0]
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            # 1. الدخول لجوجل وانتظار "بشري"
            await page.goto(random.choice(["https://www.google.com.sa", "https://www.google.com"]))
            await asyncio.sleep(random.uniform(3, 6))

            # 2. كتابة البحث (بطيئة جداً مع أخطاء مطبعية وتصحيحها لزيادة الواقعية)
            keyword = random.choice(KEYWORDS)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']")
            await search_box.click()
            for char in keyword:
                await page.keyboard.type(char, delay=random.randint(150, 450)) #
            await page.keyboard.press("Enter")
            
            # 3. تصفح نتائج جوجل قبل اختيار موقعك (عشان تبين طبيعي)
            await asyncio.sleep(random.uniform(4, 7))
            await human_scroll(page)
            
            # 4. البحث عن موقعك والضغط عليه
            link_selector = f"a[href*='{MY_SITE}']"
            try:
                await page.wait_for_selector(link_selector, timeout=15000)
                link = page.locator(link_selector).first
                await link.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(2, 5))
                await human_mouse_move(page)
                await link.click()
                print(f"🎯 دخلت الموقع: {MY_SITE} بنجاح!")

                # 5. التفاعل العميق داخل الموقع (أهم مرحلة للسيو)
                stay_duration = random.randint(300, 600) # بقاء من 5 لـ 10 دقائق
                end_time = time.time() + stay_duration
                while time.time() < end_time:
                    await human_scroll(page)
                    await human_mouse_move(page)
                    # احتمالية الضغط على رابط داخلي لرفع الـ Page Views
                    if random.random() > 0.8:
                        inner_links = await page.query_selector_all(f"a[href*='{MY_SITE}']")
                        if inner_links:
                            await random.choice(inner_links).click()
                            await asyncio.sleep(random.uniform(5, 10))
                    await asyncio.sleep(random.uniform(10, 30))
                
                print(f"✅ انتهت الجلسة البشرية بنجاح.")
            except:
                print("⚠️ الموقع مش طالع بالصفحة الأولى، جرب ترفع الترتيب يدوياً شوي.")

            await browser.close()
            requests.get(f"{ADS_API_BASE}/stop?user_id={profile_id}")

    except Exception as e:
        print(f"❌ خطأ في النظام: {e}")

async def main():
    print("🚀 انطلاق بوت 'الزيارة البشرية' لرفع سيو Tg Crypto Bot...")
    while True:
        for pid in PROFILE_IDS:
            await perform_visit(pid)
            # استراحة طويلة بين الزيارات عشان جوجل ما تشك بالـ IP السعودي
            gap = random.randint(600, 1200)
            print(f"😴 استراحة تكتيكية لمدة {gap//60} دقيقة...")
            await asyncio.sleep(gap)

if __name__ == "__main__":
    asyncio.run(main())
