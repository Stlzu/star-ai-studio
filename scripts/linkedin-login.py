#!/usr/bin/env python3
"""LinkedIn login helper — opens a non-headless browser to log in once.
After this, linkedin-post.py can use the saved session."""
import os, sys
from playwright.sync_api import sync_playwright

print("🔓 Opening LinkedIn for one-time login...")
print("   Complete the login in the browser window, then close it.")
print("   The session will be saved for automated posting.\n")

p = sync_playwright().start()
context = p.chromium.launch_persistent_context(
    user_data_dir=os.path.expanduser("~/.hermes/playwright-linkedin"),
    headless=False,  # Visible browser for login
    args=["--no-sandbox"],
    viewport={"width": 1280, "height": 900},
)
page = context.new_page()
page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
print("✅ Browser opened. Log in and close the window when done.")

# Wait for user to close the browser
page.wait_for_event("close", timeout=300000)  # 5 min timeout
context.close()
p.stop()
print("✅ LinkedIn session saved!")
