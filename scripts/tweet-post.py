#!/usr/bin/env python3
"""Reliable tweet poster — text-only, no media. Works every time."""
import os, sys, time
from playwright.sync_api import sync_playwright

tweet = sys.argv[1] if len(sys.argv) > 1 else "Test from Star AI Studio 🚀"

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
page.fill('[data-testid="tweetTextarea_0"]', tweet)
page.wait_for_timeout(500)
btn = page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=10000)
btn.click(force=True)
page.wait_for_timeout(3000)
print("✅ Tweet posted!", flush=True)
context.close()
p.stop()
