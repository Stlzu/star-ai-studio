#!/usr/bin/env python3
"""
Hermes Email Manager — Gmail via IMAP/SMTP
===========================================
Read, search, reply, and manage client emails.

Usage:
    python3 hermes_mail.py --check          # Check inbox for new client emails
    python3 hermes_mail.py --list           # List recent emails  
    python3 hermes_mail.py --search "keyword"  # Search emails
    python3 hermes_mail.py --send --to "x@y.com" --subject "Hi" --body "Hello"
    python3 hermes_mail.py --reply MSG_ID --body "Thanks for your email"

Auto-reply mode:
    python3 hermes_mail.py --auto           # Auto-reply to new inquiries
"""

import argparse
import email
import imaplib
import json
import os
import re
import smtplib
import sys
from datetime import datetime, timedelta
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime, formataddr
from pathlib import Path
from typing import Optional

# ─── Config ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "email_config.py"

def load_config() -> dict:
    """Load email config from email_config.py"""
    config = {}
    exec(CONFIG_PATH.read_text(), config)
    # Filter to only our config vars
    keys = ["EMAIL_ADDRESS", "EMAIL_APP_PASSWORD", "IMAP_SERVER", "IMAP_PORT",
            "SMTP_SERVER", "SMTP_PORT", "INBOX_FOLDER", "SENT_FOLDER",
            "AUTO_REPLY_ENABLED", "AUTO_REPLY_SIGNATURE"]
    return {k: config.get(k) for k in keys}


# ─── IMAP Connection ────────────────────────────────────────────────────────


def connect_imap(config: dict) -> imaplib.IMAP4_SSL:
    """Connect to Gmail via IMAP."""
    imap = imaplib.IMAP4_SSL(config["IMAP_SERVER"], config["IMAP_PORT"])
    imap.login(config["EMAIL_ADDRESS"], config["EMAIL_APP_PASSWORD"])
    return imap


def decode_mime_header(header_value: str) -> str:
    """Decode a MIME encoded header like =?UTF-8?Q?...?="""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or "utf-8", errors="replace"))
            except:
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result)


def get_email_body(msg: email.message.Message) -> str:
    """Extract plain text body from an email message."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body += part.get_payload(decode=True).decode(charset, errors="replace")
                except:
                    pass
            elif content_type == "text/html" and not body:
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body += part.get_payload(decode=True).decode(charset, errors="replace")
                except:
                    pass
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="replace")
        except:
            pass
    return body.strip()


def fetch_emails(config: dict, folder: str = "INBOX", search_criteria: str = "ALL",
                 max_results: int = 20) -> list[dict]:
    """Fetch emails matching criteria from Gmail."""
    imap = connect_imap(config)
    try:
        imap.select(folder)

        status, message_ids = imap.search(None, search_criteria)
        if status != "OK":
            return []

        ids = message_ids[0].split() if message_ids[0] else []
        # Get the most recent ones
        recent_ids = ids[-max_results:] if len(ids) > max_results else ids

        emails = []
        for msg_id in reversed(recent_ids):
            status, data = imap.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode headers
            subject = decode_mime_header(msg.get("Subject", ""))
            from_addr = decode_mime_header(msg.get("From", ""))
            to_addr = decode_mime_header(msg.get("To", ""))
            date_str = msg.get("Date", "")
            message_id = msg.get("Message-ID", str(msg_id))
            references = msg.get("References", "")

            # Parse date
            date = None
            try:
                date = parsedate_to_datetime(date_str).isoformat()
            except:
                date = date_str

            # Get body
            body = get_email_body(msg)

            emails.append({
                "id": msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
                "message_id": message_id.strip() if message_id else "",
                "from": from_addr,
                "to": to_addr,
                "subject": subject,
                "date": date,
                "body_preview": body[:300],
                "body": body,
                "has_attachments": msg.get_content_maintype() == "multipart",
            })

        return emails
    finally:
        imap.close()
        imap.logout()


# ─── SMTP Send ──────────────────────────────────────────────────────────────


def send_email(config: dict, to: str, subject: str, body: str,
               reply_to_msg_id: str = None, cc: str = None) -> dict:
    """Send an email via Gmail SMTP."""
    msg = MIMEMultipart()
    msg["From"] = config["EMAIL_ADDRESS"]
    msg["To"] = to
    msg["Subject"] = subject

    if cc:
        msg["Cc"] = cc

    # Handle reply threading
    if reply_to_msg_id:
        msg["In-Reply-To"] = reply_to_msg_id
        msg["References"] = reply_to_msg_id

    # Attach body
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Gather all recipients
    all_recipients = [to]
    if cc:
        all_recipients.extend([addr.strip() for addr in cc.split(",")])

    # Send
    try:
        with smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"]) as server:
            server.starttls()
            server.login(config["EMAIL_ADDRESS"], config["EMAIL_APP_PASSWORD"])
            server.sendmail(config["EMAIL_ADDRESS"], all_recipients, msg.as_string())

        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "body_length": len(body),
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }


# ─── Inquiry Detection ──────────────────────────────────────────────────────


INQUIRY_KEYWORDS = [
    "quote", "price", "cost", "how much", "interested", "hire", "service",
    "automation", "build", "develop", "create", "help", "question", "inquiry",
    "freelance", "project", "work with", "collaborate", "partnership",
    "demo", "consultation", "book", "schedule", "meeting", "call",
    "website", "tool", "app", "software", "solution",
    "proposal", "estimate", "hire you", "can you", "i need", "we need",
]

NEWSLETTER_SENDERS = [
    "newsletter@", "noreply@", "no-reply@", "notifications@",
    "news@", "announcements@", "mail@", "weekly@", "digest@",
    "accounts@", "security@",
]

NEWSLETTER_SUBJECTS = [
    "newsletter", "weekly digest", "unsubscribe", "your weekly",
    "usage at", "security alert", "action required", "breaking change",
    "is now available", "is launching", "just shipped",
]

CLIENT_SENDER_PATTERNS = [
    r'(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|icloud\.com)',
]


def is_client_inquiry(email_data: dict) -> bool:
    """Detect if an email is a client inquiry vs spam/subscription/etc."""
    subject = (email_data.get("subject") or "").lower()
    body = (email_data.get("body") or "").lower()
    from_addr = (email_data.get("from") or "").lower()
    sender_email = from_addr
    email_match = re.search(r'<([^>]+)>', from_addr)
    if email_match:
        sender_email = email_match.group(1).lower()

    # Skip if it's from our own address
    if "dstarlight851@gmail.com" in sender_email:
        return False

    # Skip known newsletter/noreply senders
    for ns in NEWSLETTER_SENDERS:
        if ns in sender_email:
            return False

    # Skip subscription/notification subject lines
    for ns in NEWSLETTER_SUBJECTS:
        if ns in subject:
            return False

    # Skip auto-replies and bounces
    if any(kw in subject for kw in ["mail delivery failed", "returned mail",
                                     "undelivered", "auto-reply", "out of office"]):
        return False

    # Check for inquiry keywords in subject or body
    text_to_check = subject + " " + body[:1000]
    inquiry_score = sum(1 for kw in INQUIRY_KEYWORDS if kw in text_to_check)

    return inquiry_score >= 1


# ─── Main CLI ───────────────────────────────────────────────────────────────


def cmd_check(config: dict, args):
    """Check inbox for new client inquiries."""
    print(f"\n{'='*60}")
    print(f"  📬 Checking inbox for {config['EMAIL_ADDRESS']}")
    print(f"{'='*60}")

    # Get recent unread emails
    emails = fetch_emails(config, "INBOX", "UNSEEN", max_results=30)

    if not emails:
        print("\n  ✅ No new emails.")
        return

    inquiries = [e for e in emails if is_client_inquiry(e)]
    other = [e for e in emails if not is_client_inquiry(e)]

    if inquiries:
        print(f"\n  📨 CLIENT INQUIRIES FOUND: {len(inquiries)}")
        print(f"  {'─' * 60}")
        for e in inquiries:
            print(f"  From    : {e['from']}")
            print(f"  Subject : {e['subject']}")
            print(f"  Date    : {e['date'][:19] if e['date'] else 'N/A'}")
            preview = e['body_preview'][:100].replace('\n', ' ')
            print(f"  Preview : {preview}...")
            print(f"  {'─' * 60}")

    if other:
        print(f"\n  📨 Other emails: {len(other)}")
        for e in other[:5]:
            print(f"    [{e['date'][:10] if e['date'] else ''}] {e['from'][:30]:30s} | {e['subject'][:50]}")

    print(f"\n  💡 Tip: Use --reply {inquiries[0]['id']} --body \"...\" to reply to an inquiry" if inquiries else "")


def cmd_list(config: dict, args):
    """List recent emails."""
    emails = fetch_emails(config, "INBOX", "ALL", max_results=args.limit or 15)
    print(f"\n{'='*60}")
    print(f"  📋 Recent emails ({len(emails)} shown)")
    print(f"{'='*60}")
    for e in emails:
        is_inquiry = "🔔" if is_client_inquiry(e) else "  "
        date_str = e['date'][:19] if e['date'] else 'N/A'
        print(f"  {is_inquiry} [{e['id']:>4s}] {date_str}")
        print(f"        From: {e['from'][:50]}")
        print(f"        Subj: {e['subject'][:60]}")
        print()


def cmd_search(config: dict, args):
    """Search emails by keyword."""
    print(f"\n  🔍 Searching for: {args.query}")
    emails = fetch_emails(config, "INBOX", f'TEXT "{args.query}"', max_results=10)
    if not emails:
        print("  No results found.")
        return
    for e in emails:
        print(f"\n  [{e['id']}] {e['from'][:40]} | {e['subject'][:60]}")
        print(f"      {e['body_preview'][:150].replace(chr(10), ' ')}...")


def cmd_send(config: dict, args):
    """Send a new email."""
    if not args.to or not args.subject or not args.body:
        print("  Error: --to, --subject, and --body are required")
        return
    result = send_email(config, args.to, args.subject, args.body)
    if result["status"] == "sent":
        print(f"\n  ✅ Email sent to {result['to']}")
    else:
        print(f"\n  ❌ Failed: {result.get('error')}")


def cmd_reply(config: dict, args):
    """Reply to an email by its IMAP ID."""
    # Fetch the original email to get sender and subject
    emails = fetch_emails(config, "INBOX", f"UID {args.msg_id}", max_results=1)
    if not emails:
        # Try searching by ID
        all_emails = fetch_emails(config, "INBOX", "ALL", max_results=100)
        emails = [e for e in all_emails if e["id"] == args.msg_id]

    if not emails:
        print(f"  ❌ Email with ID '{args.msg_id}' not found.")
        return

    original = emails[0]
    subject = original["subject"]
    if not subject.startswith("Re:"):
        subject = f"Re: {subject}"

    # Extract sender email from "Name <email>" format
    from_addr = original["from"]
    sender_email = from_addr
    email_match = re.search(r'<([^>]+)>', from_addr)
    if email_match:
        sender_email = email_match.group(1)

    # Build reply body
    signature = config.get("AUTO_REPLY_SIGNATURE", "")
    body = args.body + signature

    # Include original message context
    body += f"\n\n--- Original Message ---\nFrom: {original['from']}\nSubject: {original['subject']}\nDate: {original.get('date', '')[:19]}\n\n{original['body'][:500]}"

    result = send_email(config, sender_email, subject, body,
                        reply_to_msg_id=original.get("message_id"))

    if result["status"] == "sent":
        print(f"\n  ✅ Reply sent to {sender_email}")
        print(f"  Subject: {subject}")
    else:
        print(f"\n  ❌ Failed: {result.get('error')}")


def cmd_auto(config: dict, args):
    """Auto-reply to new client inquiries."""
    print(f"\n{'='*60}")
    print(f"  🤖 Auto-Reply Mode")
    print(f"{'='*60}")

    if not config.get("AUTO_REPLY_ENABLED"):
        print("  Auto-reply is disabled in config.")
        return

    emails = fetch_emails(config, "INBOX", "UNSEEN", max_results=30)
    inquiries = [e for e in emails if is_client_inquiry(e)]

    if not inquiries:
        print("\n  ✅ No new inquiries to reply to.")
        return

    print(f"\n  Found {len(inquiries)} new inquiries. Processing...")

    for e in inquiries:
        print(f"\n  {'─' * 50}")
        print(f"  From: {e['from']}")
        print(f"  Subject: {e['subject']}")

        # Determine the right auto-reply message
        body_lower = (e.get("body", "") + " " + e.get("subject", "")).lower()
        if "price" in body_lower or "cost" in body_lower or "how much" in body_lower:
            reply_body = f"Thank you for reaching out to Star AI Studio!\n\nI'd be happy to discuss pricing with you. Could you tell me a bit more about what you're looking to automate? That way I can give you a tailored quote.\n\nWe build custom AI automation tools starting from $500."
        elif "demo" in body_lower or "consultation" in body_lower or "meeting" in body_lower:
            reply_body = f"Thank you for your interest in Star AI Studio!\n\nI'd be happy to schedule a demo/consultation. Could you let me know what days/times work best for you, and a brief description of what you'd like to discuss?"
        elif "build" in body_lower or "develop" in body_lower or "create" in body_lower:
            reply_body = f"Thank you for reaching out to Star AI Studio!\n\nI'd love to hear more about the project you have in mind. Could you share a few details about what you're looking to build? I'll put together a proposal and timeline for you."
        else:
            reply_body = f"Thank you for contacting Star AI Studio!\n\nI appreciate your interest. Could you tell me a bit more about what you're looking for? I'll be happy to help with a custom solution.\n\nIn the meantime, you can check out some of our work at: https://github.com/Stlzu/star-ai-studio"

        # Extract sender email
        sender = e["from"]
        email_match = re.search(r'<([^>]+)>', sender)
        if email_match:
            sender = email_match.group(1)

        subject = e["subject"]
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"

        signature = config.get("AUTO_REPLY_SIGNATURE", "")
        full_body = reply_body + signature

        result = send_email(config, sender, subject, full_body,
                           reply_to_msg_id=e.get("message_id"))

        if result["status"] == "sent":
            print(f"  ✅ Auto-replied")
        else:
            print(f"  ❌ Failed: {result.get('error')}")

    print(f"\n  ✅ Auto-reply complete. Replied to {len(inquiries)} inquiries.")


def main():
    config = load_config()

    parser = argparse.ArgumentParser(description="Hermes Email Manager")
    parser.add_argument("--check", action="store_true", help="Check for new client inquiries")
    parser.add_argument("--list", action="store_true", help="List recent emails")
    parser.add_argument("--search", help="Search emails by keyword")
    parser.add_argument("--limit", type=int, default=15, help="Max results for --list")

    send_group = parser.add_argument_group("Send/Reply")
    send_group.add_argument("--send", action="store_true", help="Send a new email")
    send_group.add_argument("--reply", help="Reply to an email by ID")
    send_group.add_argument("--to", help="Recipient email address")
    send_group.add_argument("--subject", help="Email subject")
    send_group.add_argument("--body", help="Email body text")
    send_group.add_argument("--msg-id", help="Message ID to reply to (alternative to --reply)")

    send_group.add_argument("--auto", action="store_true", help="Auto-reply to all new inquiries")

    args = parser.parse_args()

    # Validate credentials
    if not config.get("EMAIL_ADDRESS") or not config.get("EMAIL_APP_PASSWORD"):
        print("❌ Email not configured. Run setup first.")
        print("   Create email_config.py with your Gmail credentials.")
        sys.exit(1)

    try:
        if args.check:
            cmd_check(config, args)
        elif args.list:
            cmd_list(config, args)
        elif args.search:
            cmd_search(config, args)
        elif args.send:
            cmd_send(config, args)
        elif args.reply:
            cmd_reply(config, args)
        elif args.auto:
            cmd_auto(config, args)
        else:
            parser.print_help()

    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP Error: {e}")
        print("   Make sure:")
        print("   1. IMAP is enabled in Gmail Settings → Forwarding and POP/IMAP")
        print("   2. The App Password is correct")
        print("   3. 2-Step Verification is enabled on your Google account")
    except smtplib.SMTPAuthenticationError:
        print("\n❌ SMTP Authentication Error")
        print("   The App Password may be incorrect. Generate a new one at:")
        print("   https://myaccount.google.com/apppasswords")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print()


if __name__ == "__main__":
    main()
