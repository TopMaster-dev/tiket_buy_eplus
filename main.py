import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta

async def run_at_10am(page):
    has_run_today = False

    while True:
        now = datetime.now()

        if now.hour == 12 and now.minute == 0 and not has_run_today:
            print(f"🟢 It's {now} AM! Running function...")
            await page.wait_for_selector("div.bt-area span#enter-bt-zumi a", timeout=10000)
            await page.click("div.bt-area span#enter-bt-zumi a")
            print('div.bt-area span#enter-bt-zumi a')
            await page.wait_for_selector('div.accept-con input#i14', timeout=10000)
            await page.click('div.accept-con input#i14')
            print('div.accept-con input#i14')
            await page.wait_for_selector('div.con input#i8', timeout=10000)
            await page.click('div.con input#i8')
            print('div.con input#i8')
            await page.wait_for_selector('div.cont-block span.enter-bt span a', timeout=10000)
            await page.click('div.cont-block span.enter-bt span a')
            print(f"Done Date:{now}")
            has_run_today = True
            return False
        print(f"Date:{now}")
        # Reset flag after 11 AM
        if now.hour > 10:
            has_run_today = False
        await asyncio.sleep(0.1)  # Check every 10 seconds

async def run():
    url = "https://eplus.jp/sf/detail/4348620001-P0030001P021001?P1=1221"
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
        await asyncio.Event().wait()
        print("Finished scraping. Browser will stay open.")
        await asyncio.sleep(30)  # Keep browser open for 30 second

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()