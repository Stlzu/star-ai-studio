#!/usr/bin/env python3
"""Post to LinkedIn via Playwright browser automation. Text + optional link."""
import os, sys, time
from playwright.sync_api import sync_playwright

post_text = sys.argv[1] if len(sys.argv) > 1 else "Test post from Star AI Studio"
article_link = sys.argv[2] if len(sys.argv) > 2 else None

p = sync_playwright().start()
context = p.chromium.launch_persistent_context(
    user_data_dir=os.path.expanduser("~/.hermes/playwright-linkedin"),
    headless=True,
    args=["--no-sandbox"],
    viewport={"width": 1280, "height": 900},
)
page = context.new_page()

# Navigate to LinkedIn and start a post
page.goto("https://www.linkedin.com", wait_until="domcontentloaded", timeout=20000)
page.wait_for_timeout(2000)

# Check if logged in
if "login" in page.url.lower() or "/auth/" in page.url:
    print("❌ Not logged into LinkedIn. Run with --login to set up manually.", flush=True)
    context.close()
    p.stop()
    sys.exit(1)

# Click "Start a post" button
try:
    start_post = page.locator('[role="combobox"], button:has-text("Start a post"), .share-box-feed-entry__trigger').first
    if start_post.is_visible(timeout=5000):
        start_post.click()
        page.wait_for_timeout(2000)
    else:
        # Try navigating directly to feed
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(2000)
        start_post = page.locator('[role="combobox"], button:has-text("Start a post")').first
        start_post.click()
        page.wait_for_timeout(2000)
except Exception as e:
    print(f"⚠ Could not open post composer: {e}", flush=True)
    context.close()
    p.stop()
    sys.exit(1)

# Type the post content
try:
    editor = page.locator('[role="textbox"][aria-label*="post"], div[contenteditable="true"][data-placeholder*="what"]').first
    editor.fill("")
    page.wait_for_timeout(300)
    editor.fill(post_text)
    page.wait_for_timeout(500)
    
    if article_link:
        # Add link if provided
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(200)
        editor.fill(post_text + "\n\n" + article_link)
        page.wait_for_timeout(500)
except Exception as e:
    print(f"⚠ Could not fill post content: {e}", flush=True)
    context.close()
    p.stop()
    sys.exit(1)

# Click Post button
try:
    post_btn = page.locator('button:has-text("Post")').first
    post_btn.click()
    page.wait_for_timeout(3000)
    print("✅ LinkedIn post published!", flush=True)
except Exception as e:
    print(f"⚠ Could not click Post: {e}", flush=True)

context.close()
p.stop()
