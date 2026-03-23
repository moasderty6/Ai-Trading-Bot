import requests
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- الإعدادات النهائية لزينو ---
PROFILE_IDS = ["k1apg3yu"] #
# استخدام الرابط المحلي الجديد لفك تشفير الوصول
ADS_API_BASE = "http://local.adspower.net:50325/api/v1/browser"
MY_SITE = "tgcryptobot.com" #
KEYWORDS = ["Tg Crypto Bot", "بوت تحليل العملات الرقمية", "بوت تحليل العملات"]

async def refresh_fingerprint(profile_id):
    """تحديث بصمة المتصفح لضمان زيارة فريدة في كل مرة"""
    url = "http://local.adspower.net:50325/api/v1/user/update"
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
        print(f"🔄 [ID: {profile_id}] تم تحديث البصمة بنجاح.")
    except:
        print(f"⚠️ تنبيه: تعذر تحديث البصمة، تأكد أن AdsPower مفتوح.")

async def perform_visit(profile_id):
    """تنفيذ دورة البحث والزيارة بالكامل"""
    try:
        await refresh_fingerprint(profile_id)
        
        # طلب تشغيل المتصفح من الرابط المحلي الجديد
        start_url = f"{ADS_API_BASE}/start?user_id={profile_id}&clear_cache=1"
        response = requests.get(start_url).json()
        
        if response["code"] != 0: 
            print(f"❌ خطأ AdsPower: {response.get('msg')}")
            return
        
        ws_endpoint = response["data"]["ws"]["puppeteer"]

        async with async_playwright() as p:
            # الاتصال بالمتصفح عبر CDP
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0]
            
            # 1. التوجه لمحرك البحث
            await page.goto(random.choice(["https://www.google.com.sa", "https://www.google.com"]))
            await asyncio.sleep(random.uniform(5, 8))

            # 2. محاكاة الكتابة البشرية للبحث
            keyword = random.choice(KEYWORDS)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']")
            for char in keyword:
                await page.keyboard.type(char, delay=random.randint(100, 300))
            await page.keyboard.press("Enter")
            print(f"🔍 جاري البحث عن: {keyword}")

            # 3. تصفح النتائج بشكل عشوائي لرفع الثقة
            await asyncio.sleep(random.uniform(5, 10))
            for _ in range(random.randint(1, 3)):
                await page.mouse.wheel(0, random.randint(300, 700))
                await asyncio.sleep(2)

            # 4. محاولة العثور على موقعك والضغط عليه
            link_selector = f"a[href*='{MY_SITE}']"
            try:
                await page.wait_for_selector(link_selector, timeout=12000)
                link = page.locator(link_selector).first
                await link.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(2, 4))
                await link.click()
                print(f"🎯 دخلت الموقع: {MY_SITE} بنجاح!")

                # 5. التفاعل الداخلي لتقليل الارتداد (Bounce Rate)
                stay_seconds = random.randint(240, 480)
                print(f"⏳ سأبقى داخل الموقع لمدة {stay_seconds//60} دقيقة...")
                end_time = time.time() + stay_seconds
                while time.time() < end_time:
                    await page.mouse.wheel(0, random.randint(-300, 600))
                    await asyncio.sleep(random.uniform(20, 50))
                
                print(f"✅ انتهت الزيارة بنجاح.")
            except:
                print(f"⚠️ الموقع لم يظهر في الصفحة الأولى، سأجرب كلمة أخرى لاحقاً.")

            await browser.close()
            # إغلاق البروفايل في البرنامج لتوفير موارد الجهاز
            requests.get(f"{ADS_API_BASE}/stop?user_id={profile_id}")

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")

async def main():
    """المحرك الرئيسي للبوت"""
    print("🚀 انطلاق بوت السيو المحلي على جهاز زينو...")
    print("الموقع المستهدف: " + MY_SITE)
    while True:
        for pid in PROFILE_IDS:
            await perform_visit(pid)
            # استراحة بين الزيارات
            await asyncio.sleep(random.randint(180, 400)) 

        # استراحة كبرى لتمويه خوارزميات جوجل (ساعتين تقريباً)
        wait_time = random.randint(7200, 10800)
        print(f"😴 استراحة كبرى لمدة {wait_time//3600} ساعة... سأعود للعمل تلقائياً.")
        await asyncio.sleep(wait_time)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت يدوياً.")
