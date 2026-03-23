import requests
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- الإعدادات النهائية لزينو ---
PROFILE_IDS = ["k1apg3yu"]
ADS_API_BASE = "http://local.adspower.net:50325/api/v1/browser"
MY_SITE = "tgcryptobot.com"
KEYWORDS = ["Tg Crypto Bot", "بوت تحليل العملات الرقمية", "بوت تحليل العملات"]

async def human_scroll(page):
    """محاكاة سكرول بشري حقيقي (توقف وحركة متقطعة)"""
    for _ in range(random.randint(3, 6)):
        scroll_step = random.randint(300, 700)
        await page.mouse.wheel(0, scroll_step)
        await asyncio.sleep(random.uniform(2, 4))

async def perform_visit(profile_id):
    try:
        # 1. تشغيل المتصفح مع إجبار مسح الكاش وإغلاق الصفحات السابقة (open_tabs=1 تعني فتح تبويب جديد فقط)
        # نستخدم &ip_tab=1 لضمان فتح صفحة نظيفة
        start_url = f"{ADS_API_BASE}/start?user_id={profile_id}&clear_cache=1&open_tabs=1"
        response = requests.get(start_url).json()
        if response["code"] != 0: return

        ws_endpoint = response["data"]["ws"]["puppeteer"]

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            
            # إغلاق أي صفحات قديمة كانت مفتوحة وبقيت معلقة
            pages = context.pages
            for i in range(1, len(pages)):
                await pages[i].close()
            
            page = pages[0]
            await page.set_viewport_size({"width": 1366, "height": 768})

            # 2. الدخول لجوجل
            await page.goto(random.choice(["https://www.google.com.sa", "https://www.google.com"]))
            await asyncio.sleep(random.uniform(3, 5))

            # 3. البحث
            keyword = random.choice(KEYWORDS)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']")
            await search_box.click()
            for char in keyword:
                await page.keyboard.type(char, delay=random.randint(150, 350))
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")

            # 4. البحث في أول 5 صفحات
            found = False
            for current_page in range(1, 6):
                print(f"🔎 فحص الصفحة رقم {current_page} عن موقع {MY_SITE}...")
                await asyncio.sleep(random.uniform(3, 5))
                await human_scroll(page)

                # هل الموقع موجود في هذه الصفحة؟
                link_selector = f"a[href*='{MY_SITE}']"
                links_count = await page.locator(link_selector).count()
                
                if links_count > 0:
                    print(f"🎯 تم العثور على الموقع في الصفحة {current_page}!")
                    link_element = page.locator(link_selector).first
                    await link_element.scroll_into_view_if_needed()
                    await asyncio.sleep(random.uniform(2, 4))
                    await link_element.click()
                    found = True
                    break
                else:
                    # إذا لم يجد الموقع، يذهب للزر "التالي" (Next)
                    print(f"⏭️ لم يظهر في الصفحة {current_page}، ننتقل للتالية...")
                    next_button = page.locator("a#pnnext, a[aria-label='Next page']").first
                    if await next_button.is_visible():
                        await next_button.click()
                        await page.wait_for_load_state("networkidle")
                    else:
                        print("⚠️ لا يوجد صفحات تالية.")
                        break

            # 5. التفاعل داخل الموقع إذا تم الدخول
            if found:
                stay_time = random.randint(240, 400)
                end_time = time.time() + stay_time
                while time.time() < end_time:
                    await human_scroll(page)
                    await asyncio.sleep(random.uniform(15, 30))
                print(f"✅ انتهت الجلسة بنجاح.")

            # 6. الإغلاق النهائي (تنظيف كامل)
            await browser.close()
            # أمر إيقاف البروفايل في AdsPower يمسح الجلسة المؤقتة
            requests.get(f"{ADS_API_BASE}/stop?user_id={profile_id}")
            print(f"🧹 تم إغلاق البروفايل {profile_id} ومسح الكاش.")

    except Exception as e:
        print(f"❌ خطأ: {e}")

async def main():
    print("🚀 بوت السيو (نسخة الـ 5 صفحات) انطلق!")
    while True:
        for pid in PROFILE_IDS:
            await perform_visit(pid)
            gap = random.randint(600, 1200)
            print(f"😴 استراحة {gap//60} دقيقة...")
            await asyncio.sleep(gap)

if __name__ == "__main__":
    asyncio.run(main())
