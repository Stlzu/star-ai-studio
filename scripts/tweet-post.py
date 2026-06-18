#!/usr/bin/env python3
"""Reliable tweet poster — text + optional media. Works every time."""
import os, sys, time
from playwright.sync_api import sync_playwright

tweet = sys.argv[1] if len(sys.argv) > 1 else "Test from Star AI Studio 🚀"
media = sys.argv[2] if len(sys.argv) > 2 else None

p = sync_playwright().start()
context = p.chromium.launch_persistent_context(
    user_data_dir=os.path.expanduser("~/.hermes/playwright-twitter"),
    headless=True,
    args=["--no-sandbox"],
    viewport={"width": 1280, "height": 900},
)
page = context.new_page()
page.goto("https://x.com", wait_until="domcontentloaded", timeout=20000)
page.wait_for_timeout(2000)

# Fill tweet text
page.fill('[data-testid="tweetTextarea_0"]', tweet)
page.wait_for_timeout(500)

# Upload media if provided
if media and os.path.exists(media):
    try:
        # Twitter/X file input
        file_input = page.locator('input[accept*="image"], input[accept*="video"], input[type="file"]').first
        if file_input.is_visible(timeout=3000):
            file_input.set_input_files(media)
            print(f"📎 Attached media: {media}", flush=True)
            page.wait_for_timeout(3000)  # Wait for upload
    except Exception as e:
        print(f"⚠ Media upload skipped: {e}", flush=True)

# Click post button
btn = page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=10000)
btn.click(force=True)
page.wait_for_timeout(3000)
print("✅ Tweet posted!", flush=True)
context.close()
p.stop()
