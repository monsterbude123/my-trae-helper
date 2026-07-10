import asyncio
from playwright.async_api import async_playwright
import os
import requests

async def download_image(url, filename):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36"
        }
        with requests.get(url, stream=True, timeout=10, headers=headers) as response:
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

async def main():
    async with async_playwright() as p:
        print("Launching chromium...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.109 Safari/537.36"
        )
        page = await context.new_page()
        
        target_url = "https://civitai.com/user/LatentHeart/images"
        print(f"Navigating to {target_url}...")
        
        try:
            # Use domcontentloaded to avoid waiting for all assets
            await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            print("Page loaded (domcontentloaded). Waiting for images...")
            # Wait for images to be present in the DOM
            await page.wait_for_selector("img", timeout=30000)
            # Wait for a bit to allow lazy loading
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return

        # Find images
        images = await page.query_selector_all("img")
        print(f"Found {len(images)} image elements.")

        count = 0
        for i, img in enumerate(images):
            if count >= 3:
                break
            
            try:
                src = await img.get_attribute("src")
                if src:
                    if src.startswith("http") and not src.startswith("data:"):
                        filename = f"image_{count+1}.jpg"
                        print(f"Attempting to download: {src}")
                        success = await download_image(src, filename)
                        if success:
                            print(f"Successfully saved {filename}")
                            count += 1
                        else:
                            print(f"Failed to save {filename}")
                    else:
                        continue
            except Exception as e:
                print(f"Error processing image {i}: {e}")
                continue

        print(f"Finished. Downloaded {count} images.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
