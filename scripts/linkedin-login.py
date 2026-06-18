#!/usr/bin/env python3
"""Save LinkedIn session from real Chrome into Playwright profile for headless use."""
import os, sys, json
from playwright.sync_api import sync_playwright

PLAYWRIGHT_PROFILE = os.path.expanduser("~/.hermes/playwright-linkedin")

p = sync_playwright().start()

# Launch real Chrome (not Playwright Chromium) with the user's profile
# This bypasses LinkedIn's bot detection
context = p.chromium.launch_persistent_context(
    user_data_dir=PLAYWRIGHT_PROFILE,
    channel="chrome",
    headless=False,  # Show the browser so user can see it
    args=["--no-sandbox"],
    viewport={"width": 1280, "height": 900},
)

page = context.new_page()
page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(3000)

# Check if already logged in
if "feed" in page.url:
    print("✅ Already logged into LinkedIn! Session captured.", flush=True)
    # Save cookies for headless reuse
    cookies = context.cookies()
    with open(os.path.join(PLAYWRIGHT_PROFILE, "linkedin_cookies.json"), "w") as f:
        json.dump(cookies, f)
    print(f"Saved {len(cookies)} cookies to Playwright profile.", flush=True)
else:
    print(f"⚠ Not logged in. URL: {page.url[:80]}", flush=True)
    print("Log in manually and close the browser.", flush=True)
    try:
        page.wait_for_event("close", timeout=300000)
    except:
        pass

context.close()
p.stop()
print("Done. Headless LinkedIn posting should work now.", flush=True)
