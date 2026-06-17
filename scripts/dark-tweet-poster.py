#!/usr/bin/env python3
"""
dark-tweet-poster.py — Posts to X.com via Chrome JavaScript injection.
Works when display is asleep because it uses AppleScript → Chrome DevTools,
NOT screen capture. No Peekaboo see/image needed.

Usage: python3 dark-tweet-poster.py "Your tweet text here"
"""
import subprocess, sys, json, os, time

tweet = sys.argv[1] if len(sys.argv) > 1 else "Test from dark mode"

# Escape text for JavaScript injection
js_text = json.dumps(tweet)

# Build JavaScript that navigates to compose, fills text, and posts
js = f"""
(function(){{
  var text = {js_text};
  var doPost = function() {{
    var ta = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (!ta) return 'NO_TA';
    ta.focus();
    ta.innerText = text;
    ta.setAttribute('data-text', text);
    ta.dispatchEvent(new Event('input', {{bubbles: true}}));
    setTimeout(function() {{
      var btn = document.querySelector('[data-testid="tweetButton"]');
      if (btn) {{ btn.click(); }}
    }}, 2000);
    return 'SET:' + ta.innerText.length;
  }};
  if (window.location.href.indexOf('compose') > -1) {{
    return doPost();
  }} else {{
    window.location.href = 'https://x.com/compose/post';
    setTimeout(doPost, 3000);
    return 'NAVIGATING';
  }}
}})();
"""

# Write JS to temp file
with open('/tmp/_dark_tweet.js', 'w') as f:
    f.write(js)

# Execute via AppleScript (doesn't need display)
script = f'''
tell application "Google Chrome"
	set jsCode to do shell script "cat /tmp/_dark_tweet.js"
	set result to execute active tab of window 1 javascript jsCode
	return result
end tell
'''

result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=30)
print(result.stdout or result.stderr[:200])
