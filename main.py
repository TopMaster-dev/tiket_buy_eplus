import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta

async def run_at_10am(page):
    has_run_today = False

    while True:
        now = datetime.now()

        if now.hour == 21 and now.minute == 15 and not has_run_today:
            print("🟢 It's 10:00 AM! Running function...")
            page.click("div.br-area span#enter-bt-zumi a")
            page.wait_for_selector('div.accept-con input#i14', timeout=10000)
            page.click('div.accept-con input#i14')
            page.wait_for_selector('div.con input#i8', timeout=10000)
            page.click('div.con input#i8')
            page.wait_for_selector('span.enter-bt span a', timeout=10000)
            page.click('span.enter-bt span a')
            has_run_today = True
            return False

        # Reset flag after 11 AM
        if now.hour > 10:
            has_run_today = False

        await asyncio.sleep(1)  # Check every 10 seconds

async def run():
    # tomorrow = datetime.now() + timedelta(days=1)
    # setDay = tomorrow.strftime("%Y%m%d")
    # print(setDay)
    url = "https://eplus.jp"
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        # Avoid automation detection
        await page.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")

        print("Navigating...")
        await page.goto(url, wait_until="load", timeout=300000)
        print("loaded")
        await run_at_10am(page)
        print("end=====")
        # ==========login wait=============
        await page.wait_for_selector("div.br-area span#enter-bt-zumi a", timeout=0)
        
        print("Finished scraping. Browser will stay open.")
        await asyncio.sleep(30)  # Keep browser open for 1 hour

def main(): 
    asyncio.run(run())

if __name__ == "__main__":
    main()