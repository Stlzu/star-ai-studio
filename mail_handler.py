#!/usr/bin/env python3
"""
Hermes Email Handler — for use inside execute_code
===================================================
Lets me check and reply to client emails on your behalf.

Usage in execute_code:
    from hermes_tools import terminal
    terminal("python3 hermes_mail.py --check")
"""

import json, sys, re
from pathlib import Path

BASE = Path.home() / "hermes-million"
sys.path.insert(0, str(BASE))

def check_mail():
    """Check inbox for client inquiries."""
    import subprocess
    result = subprocess.run(
        ["python3", str(BASE / "hermes_mail.py"), "--check"],
        capture_output=True, text=True, timeout=30
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

def list_emails(limit=20):
    """List recent emails."""
    import subprocess
    result = subprocess.run(
        ["python3", str(BASE / "hermes_mail.py"), "--list", "--limit", str(limit)],
        capture_output=True, text=True, timeout=30
    )
    print(result.stdout)

def send_reply(msg_id, body):
    """Reply to an email by its ID."""
    import subprocess
    result = subprocess.run(
        ["python3", str(BASE / "hermes_mail.py"), "--reply", str(msg_id), "--body", body],
        capture_output=True, text=True, timeout=30
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

def send_new(to, subject, body):
    """Send a new email."""
    import subprocess
    result = subprocess.run(
        ["python3", str(BASE / "hermes_mail.py"), "--send", "--to", to,
         "--subject", subject, "--body", body],
        capture_output=True, text=True, timeout=30
    )
    print(result.stdout)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "check":
            check_mail()
        elif cmd == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            list_emails(limit)
        elif cmd == "reply":
            send_reply(sys.argv[2], sys.argv[3])
        elif cmd == "send":
            send_new(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        check_mail()
