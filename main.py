import requests
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- الإعدادات النهائية لزينو ---
PROFILE_IDS = ["k1apg3yu"] 
# تغيير الرابط للعنوان المحلي الافتراضي لتجنب طلب الـ API Key
ADS_API_BASE = "http://127.0.0.1:50325/api/v1/browser"
MY_SITE = "tgcryptobot.com" 
KEYWORDS = ["Tg Crypto Bot", "بوت تحليل العملات الرقمية", "بوت تحليل العملات"]

async def refresh_fingerprint(profile_id):
    """تغيير بصمة المتصفح برمجياً لكسر النمط قبل كل زيارة"""
    url = f"http://127.0.0.1:50325/api/v1/user/update"
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    data = {
        "user_id": profile_id,
        "fingerprint_config": {
            "automatic_timezone": "1",
            "language_type": "1",
            "ua": random.choice(ua_list)
        }
    }
    try:
        requests.post(url, json=data, timeout=5)
        print(f"🔄 [ID: {profile_id}] تم تحديث الهوية بنجاح.")
    except:
        print(f"⚠️ تنبيه: تعذر تحديث الهوية، تأكد من فتح تطبيق AdsPower.")

async def perform_visit(profile_id):
    """دورة الزيارة الكاملة بمحاكاة سلوك بشري حقيقي"""
    try:
        await refresh_fingerprint(profile_id)
        
        # طلب تشغيل المتصفح (clear_cache لضمان جلسة جديدة)
        start_url = f"{ADS_API_BASE}/start?user_id={profile_id}&clear_cache=1"
        response = requests.get(start_url).json()
        
        if response["code"] != 0: 
            print(f"❌ خطأ AdsPower: {response.get('msg')}")
            print("💡 جرب الذهاب لإعدادات AdsPower -> Local API وقم بتفعيل 'Allow No Password'")
            return
        
        ws_endpoint = response["data"]["ws"]["puppeteer"]

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0]
            
            # 1. التوجه لجوجل (استخدام النطاق السعودي)
            await page.goto(random.choice(["https://www.google.com.sa", "https://www.google.com"]))
            await asyncio.sleep(random.uniform(5, 8))

            # 2. محاكاة البحث
            keyword = random.choice(KEYWORDS)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']")
            for char in keyword:
                await page.keyboard.type(char, delay=random.randint(100, 300))
            await page.keyboard.press("Enter")
            print(f"🔍 جاري البحث عن: {keyword}")

            # 3. سكرول عشوائي في النتائج
            await asyncio.sleep(random.uniform(5, 10))
            for _ in range(random.randint(1, 3)):
                await page.mouse.wheel(0, random.randint(300, 700))
                await asyncio.sleep(2)

            # 4. البحث عن موقعك والضغط عليه
            link_selector = f"a[href*='{MY_SITE}']"
            try:
                await page.wait_for_selector(link_selector, timeout=12000)
                link = page.locator(link_selector).first
                await link.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(2, 4))
                await link.click()
                print(f"🎯 نجاح: تم الدخول إلى {MY_SITE}")

                # 5. التفاعل داخل الموقع (4-6 دقائق)
                stay_seconds = random.randint(240, 360)
                print(f"⏳ سأبقى في الموقع لمدة {stay_seconds//60} دقيقة لتعزيز السيو...")
                end_time = time.time() + stay_seconds
                while time.time() < end_time:
                    await page.mouse.wheel(0, random.randint(-200, 500))
                    await asyncio.sleep(random.uniform(20, 45))
                
                print(f"✅ انتهت الجلسة بنجاح.")
            except:
                print(f"⚠️ الموقع لم يظهر في الصفحة الأولى، سأحاول في المرة القادمة.")

            await browser.close()
            requests.get(f"{ADS_API_BASE}/stop?user_id={profile_id}")

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")

async def main():
    """المحرك الرئيسي"""
    print("🚀 بوت السيو انطلق! (لابتوب زينو)")
    print("تأكد أن AdsPower مفتوح والـ Local API مفعل.")
    while True:
        for pid in PROFILE_IDS:
            await perform_visit(pid)
            await asyncio.sleep(random.randint(150, 300)) 

        # استراحة كبرى لكسر النمط (ساعة ونصف تقريباً)
        wait_time = random.randint(5400, 7200)
        print(f"😴 استراحة كبرى لمدة {wait_time//3600} ساعة... سأعود تلقائياً.")
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت.")
