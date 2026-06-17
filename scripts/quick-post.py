#!/usr/bin/env python3
"""Quick tweet poster — bypasses the EPIPE bug in full script."""
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

# Type tweet
page.fill('[data-testid="tweetTextarea_0"]', tweet)

# Attach media
if media and os.path.exists(media):
    fi = page.wait_for_selector('input[type="file"]', timeout=5000)
    fi.set_input_files(os.path.abspath(media))
    print(f"📎 Attached: {os.path.basename(media)}", flush=True)

# Wait for button to enable (upload progress)
start = time.time()
for i in range(180):
    try:
        btn = page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=500)
        if btn and btn.is_enabled():
            secs = time.time() - start
            btn.click()
            page.wait_for_timeout(2000)
            print(f"✅ Posted in {secs:.0f}s!", flush=True)
            context.close()
            p.stop()
            sys.exit(0)
    except:
        pass
    page.wait_for_timeout(1000)

print("❌ Timed out waiting for Post button", flush=True)
context.close()
p.stop()
