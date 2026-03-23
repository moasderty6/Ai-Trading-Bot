import requests
import time
import random
import asyncio
from playwright.async_api import async_playwright

# --- الإعدادات النهائية لزينو ---
PROFILE_IDS = ["k1apg3yu"] #
ADS_API_BASE = "http://local.adspower.net:50325/api/v1/browser"
MY_SITE = "tgcryptobot.com" #
KEYWORDS = ["Tg Crypto Bot", "بوت تحليل العملات الرقمية", "بوت تحليل العملات"]

async def refresh_fingerprint(profile_id):
    url = "http://local.adspower.net:50325/api/v1/user/update"
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ]
    data = {"user_id": profile_id, "fingerprint_config": {"ua": random.choice(ua_list)}}
    try:
        requests.post(url, json=data, timeout=5)
        print(f"🔄 [ID: {profile_id}] تم تحديث البصمة.")
    except: pass

async def perform_visit(profile_id):
    try:
        await refresh_fingerprint(profile_id)
        start_url = f"{ADS_API_BASE}/start?user_id={profile_id}&clear_cache=1"
        response = requests.get(start_url).json()
        
        if response["code"] != 0: return
        
        ws_endpoint = response["data"]["ws"]["puppeteer"]

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_endpoint)
            context = browser.contexts[0]
            page = context.pages[0]
            
            await page.goto(random.choice(["https://www.google.com.sa", "https://www.google.com"]))
            
            # --- فحص الكابشا ---
            if "google.com/sorry" in page.url or await page.query_selector("iframe[src*='recaptcha']"):
                print("⚠️ تنبيه: ظهرت الكابشا! حلها يدوياً الآن.. سأنتظر 60 ثانية.")
                await asyncio.sleep(60) # يمنحك دقيقة لحلها يدوياً قبل الإغلاق
            
            # كتابة البحث
            keyword = random.choice(KEYWORDS)
            search_box = await page.wait_for_selector("textarea[name='q'], input[name='q']")
            for char in keyword:
                await page.keyboard.type(char, delay=random.randint(150, 400))
            await page.keyboard.press("Enter")
            
            # البحث عن الموقع والضغط
            link_selector = f"a[href*='{MY_SITE}']"
            try:
                await page.wait_for_selector(link_selector, timeout=15000)
                link = page.locator(link_selector).first
                await link.click()
                print(f"🎯 دخلت الموقع: {MY_SITE}")
                await asyncio.sleep(random.randint(200, 400))
            except:
                print("⚠️ لم أجد الموقع أو ظهرت كابشا ثانية.")

            await browser.close()
            requests.get(f"{ADS_API_BASE}/stop?user_id={profile_id}")

    except Exception as e:
        print(f"❌ خطأ: {e}")

async def main():
    print("🚀 بوت زينو شغال.. عيني على الكابشا!")
    while True:
        for pid in PROFILE_IDS:
            await perform_visit(pid)
            await asyncio.sleep(random.randint(300, 600)) 

if __name__ == "__main__":
    asyncio.run(main())
