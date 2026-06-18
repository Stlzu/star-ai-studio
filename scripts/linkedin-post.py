#!/usr/bin/env python3
"""Post to LinkedIn using REAL Chrome with saved session cookies."""
import os, sys, json, time
from playwright.sync_api import sync_playwright

post_text = sys.argv[1] if len(sys.argv) > 1 else "Test post from Star AI Studio"
article_link = sys.argv[2] if len(sys.argv) > 2 else None

PROFILE_DIR = os.path.expanduser("~/.hermes/playwright-linkedin")
COOKIES_FILE = os.path.join(PROFILE_DIR, "linkedin_cookies.json")

p = sync_playwright().start()
context = p.chromium.launch_persistent_context(
    user_data_dir=PROFILE_DIR,
    channel="chrome",          # Use REAL Chrome — bypasses LinkedIn bot detection
    headless=True,             # Headless works with real Chrome + cookies
    args=["--no-sandbox"],
    viewport={"width": 1280, "height": 900},
)

# Load saved cookies from earlier Chrome session
if os.path.exists(COOKIES_FILE):
    cookies = json.load(open(COOKIES_FILE))
    context.add_cookies(cookies)

page = context.new_page()

# Go to LinkedIn feed
page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(3000)

# Check login
if "login" in page.url.lower() or "/auth/" in page.url:
    print("❌ Not logged into LinkedIn. Session expired. Re-run linkedin-login.py.", flush=True)
    context.close()
    p.stop()
    sys.exit(1)

print("✅ Logged into LinkedIn", flush=True)

# Open post composer
try:
    start_post = page.locator('[role="combobox"], button:has-text("Start a post")').first
    if start_post.is_visible(timeout=5000):
        start_post.click()
        page.wait_for_timeout(2000)
    else:
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

# Fill content
try:
    editor = page.locator('[role="textbox"][aria-label*="post"], div[contenteditable="true"]').first
    editor.fill("")
    page.wait_for_timeout(300)
    editor.fill(post_text)
    page.wait_for_timeout(500)
    
    if article_link:
        editor.fill(post_text + "\n\n" + article_link)
        page.wait_for_timeout(500)
except Exception as e:
    print(f"⚠ Could not fill content: {e}", flush=True)
    context.close()
    p.stop()
    sys.exit(1)

# Click Post
try:
    post_btn = page.locator('button:has-text("Post")').first
    post_btn.click(timeout=10000)
    page.wait_for_timeout(3000)
    print("✅ LinkedIn post published!", flush=True)
except Exception as e:
    print(f"⚠ Could not post: {e}", flush=True)

context.close()
p.stop()
