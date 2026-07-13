import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to https://civitai.com...")
            await page.goto("https://civitai.com/", timeout=60000)
            print(f"Title: {await page.title()}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
