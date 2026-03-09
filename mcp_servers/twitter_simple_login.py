#!/usr/bin/env python3
"""
Simple Twitter Login - Manual login with proper session save
FINAL ATTEMPT with better debugging
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

STORAGE_PATH = "AI_Employee_Vault/twitter_session.json"

async def main():
    print("=" * 60)
    print("TWITTER MANUAL LOGIN - Session Saver")
    print("=" * 60)
    
    # Create directory
    Path(STORAGE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    print("\n[INFO] Opening browser...")
    print("[INFO] Please login to Twitter in the browser window.")
    print("[INFO] After login, the browser will close automatically in 10 minutes.")
    print("[INFO] Or press Ctrl+C to close early after you've logged in.\n")
    
    playwright = await async_playwright().start()
    
    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            '--window-size=1920,1080',
            '--start-maximized',
            '--disable-gpu',
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
        ]
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False
    )
    
    page = await context.new_page()
    
    # Go to Twitter home (not login page)
    print("[INFO] Opening Twitter...")
    await page.goto("https://x.com", wait_until='domcontentloaded')
    await asyncio.sleep(5)
    
    # Take initial screenshot
    await page.screenshot(path='twitter_manual_start.png', full_page=True)
    print("[INFO] Screenshot saved: twitter_manual_start.png")
    
    # Check if already logged in
    try:
        is_logged_in = await page.is_visible('article[data-testid="tweet"]')
        if is_logged_in:
            print("\n[OK] Already logged in! Saving session...")
            await context.storage_state(path=STORAGE_PATH)
            print(f"[OK] Session saved to: {STORAGE_PATH}")
            await browser.close()
            print("\n[OK] Done!")
            return
    except Exception as e:
        print(f"[INFO] Not logged in yet: {e}")
    
    print("[INFO] Waiting for login... (Press Ctrl+C when done)")
    print("[INFO] You have 10 minutes to complete login.\n")
    
    # Wait for user to login (up to 10 minutes)
    try:
        for i in range(120):  # 10 minutes (120 * 5 seconds)
            await asyncio.sleep(5)
            
            # Check if logged in every 30 seconds
            if (i + 1) % 6 == 0:
                try:
                    # Check for home timeline
                    is_logged_in = await page.is_visible('article[data-testid="tweet"]')
                    if is_logged_in:
                        print(f"\n[OK] Login detected! Home timeline found. ({(i+1)*5}s)")
                        break
                    
                    # Check for profile
                    is_profile = await page.is_visible('[data-testid="UserName"]')
                    if is_profile:
                        print(f"\n[OK] Profile detected - logged in! ({(i+1)*5}s)")
                        break
                    
                    # Check URL
                    current_url = page.url
                    if ('x.com/home' in current_url or 'twitter.com/home' in current_url):
                        if 'login' not in current_url and 'i/flow' not in current_url:
                            print(f"\n[OK] Home page detected - logged in! ({(i+1)*5}s)")
                            break
                    
                    print(f"[INFO] Still waiting... ({(i+1)*5}s / 600s)")
                    print(f"[INFO] Current URL: {current_url}")
                    
                    # Take screenshot for debugging
                    await page.screenshot(path=f'twitter_waiting_{i+1}.png', full_page=True)
                    
                except Exception as e:
                    print(f"[INFO] Checking login status... ({e})")
                
    except KeyboardInterrupt:
        print("\n[INFO] Login interrupted by user")
    
    # Save session
    print("\n[INFO] Saving session...")
    try:
        await context.storage_state(path=STORAGE_PATH)
        print(f"[OK] Session saved to: {STORAGE_PATH}")
        
        # Verify session was saved
        if Path(STORAGE_PATH).exists():
            file_size = Path(STORAGE_PATH).stat().st_size
            print(f"[OK] Session file size: {file_size} bytes")
            
            if file_size > 1000:
                print("[OK] Session looks valid!")
            else:
                print("[WARNING] Session file seems small, login may not have completed")
        else:
            print("[ERROR] Session file was not created!")
            
    except Exception as e:
        print(f"[ERROR] Failed to save session: {e}")
    
    await browser.close()
    print("\n[OK] Browser closed.")
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Check if session file exists:")
    print(f"   dir {STORAGE_PATH}")
    print("\n2. If session saved, test auto-posting:")
    print('   python mcp_servers/twitter_mcp_playwright.py --post "Test tweet" --headless')
    print("\n3. If session not saved, run this script again and login properly")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
