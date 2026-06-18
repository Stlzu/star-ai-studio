#!/usr/bin/env python3
"""Import LinkedIn session from Chrome into the Playwright profile."""
import os, sys, time, sqlite3, shutil
from pathlib import Path

CHROME_COOKIES = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"
PLAYWRIGHT_DIR = Path.home() / ".hermes/playwright-linkedin"
PLAYWRIGHT_COOKIES = PLAYWRIGHT_DIR / "Default/Cookies"

# Ensure Playwright profile directory exists
PLAYWRIGHT_DIR.mkdir(parents=True, exist_ok=True)
(PLAYWRIGHT_DIR / "Default").mkdir(parents=True, exist_ok=True)

if not CHROME_COOKIES.exists():
    print(f"Chrome cookies not found at {CHROME_COOKIES}")
    sys.exit(1)

# Copy Chrome's Cookies DB to Playwright profile
shutil.copy2(str(CHROME_COOKIES), str(PLAYWRIGHT_COOKIES))
print(f"Copied Chrome cookies to {PLAYWRIGHT_COOKIES}")

# Verify LinkedIn session exists
conn = sqlite3.connect(str(PLAYWRIGHT_COOKIES))
cursor = conn.cursor()
cursor.execute("SELECT host_key, name FROM cookies WHERE host_key LIKE '%linkedin%'")
linkedin_cookies = cursor.fetchall()
conn.close()

if linkedin_cookies:
    print(f"Found {len(linkedin_cookies)} LinkedIn cookies:")
    for host, name in linkedin_cookies[:10]:
        print(f"  {host} → {name}")
    print("\n✅ LinkedIn session imported! Automated posting should work now.")
else:
    print("⚠ No LinkedIn cookies found in Chrome.")
    print("   Make sure you're logged into LinkedIn in Chrome and try again.")
