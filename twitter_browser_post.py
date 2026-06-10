#!/usr/bin/env python3
"""
Twitter/X Browser Posting Tool
===============================
Posts tweets via browser automation when API is unavailable (free tier 402).

What it does:
1. Opens Twitter/X in a browser window
2. Types your tweet text
3. Clicks Post

HOWEVER: This script is a GUIDE for manual posting because:
- Twitter/X blocks automated browser posting with login challenges
- The session requires 2FA on a fresh browser
- Even with saved sessions, Twitter detects automation

Installing Playwright:
    pip3 install playwright
    python3 -m playwright install chromium

Usage:
    python3 twitter_browser_post.py --tweet "Your text here"
    python3 twitter_browser_post.py --thread 1
    python3 twitter_browser_post.py --thread "Blog content engine is live..."

Manual posting guide:
    1. Open x.com and log in
    2. Click "Post" button
    3. Type or paste your text
    4. Click "Post" to publish

Thread posting:
    1. Post first tweet
    2. Click "Reply" on your tweet
    3. Type next tweet
    4. Click "Reply"
    5. Repeat for all tweets in thread
"""

import argparse
import sys
import json
import time
from pathlib import Path

# Thread content (same as twitter_post.py but sanitized)
THREADS = {
    1: [  # SEO Blog Engine
        "I built an AI blog content engine that researches the web and writes SEO-optimized posts. In 2 hours. Using an AI automation toolkit. Here's how. 🧵👇",
        "The problem: Content marketing works but it's expensive. Agencies charge $500-2,000/post. Freelancers take 3-5 days. Most businesses can't keep up.",
        "The solution: An AI agent that does the entire content pipeline: Research → Analyze → Generate → Format → Publish. No human needed between topic and post.",
        "How it works: Give it a topic → it searches 8+ articles → extracts key insights → generates a 685+ word post with SEO frontmatter, headings, and real examples. All in 2 minutes.",
        "The output: Ready-to-publish markdown with YAML metadata, keyword tags, reading time, and structured sections. Compatible with any static site (Hugo, Jekyll, Ghost).",
        "The business model: $297/mo for 30 posts. At 50 customers = $14,850/mo MRR. Zero marginal cost. 1% of agency prices.",
        "Full code on GitHub: https://github.com/Stlzu/star-ai-studio\n\nDM me if you want a custom automation tool for your business. I'm taking 5 beta clients at 50% off.",
    ],
    2: [  # Lead Enrichment
        "Sales teams waste 30% of time researching leads. I built a tool that does it in 5 seconds. Here's how. 🧵👇",
        "The problem: An SDR spends 5-10 minutes researching each company before a call. For 50 calls/week = 4-8 hours of research. That's $75K/year in wasted salary for a team of 5.",
        "The solution: Paste company names → the AI enriches every field automatically: website, description, industry, LinkedIn, location, size. Ready for CRM import in CSV.",
        "The demo: 3 companies (Nous Research, Anthropic, Hugging Face) → enriched in 15 seconds. Real data from web search. Consistent. Accurate. No human fatigue.",
        "The business model: $197/mo for 2,000 companies. At 50 customers = $9,850/mo MRR. 10x faster than manual research.",
        "Built with Python. Full code: https://github.com/Stlzu/star-ai-studio\n\nWant me to enrich your lead list? DM me.",
    ],
    3: [  # Invoice Extractor
        "Accountants spend 40-80 hours/month on manual data entry. I built an AI that does it in seconds. Here's how. 🧵👇",
        "The problem: 500 invoices/month = 40-80 hours of manual entry. Errors, fatigue, and expensive labor. Most accounting firms hate this work.",
        "The solution: Upload PDF → AI extracts every field: invoice #, date, vendor, line items, amounts, tax, total. Outputs CSV or JSON.",
        "The demo: Extracted 12 fields from a sample invoice with 100% accuracy in under 1 second. Including 4 line items with descriptions and amounts.",
        "The business model: $297/mo for 5,000 invoices. At 30 accounting firms = $8,910/mo MRR. Eliminates a full-time data entry position.",
        "Built with Python + pdftotext. Full code: https://github.com/Stlzu/star-ai-studio\n\nKnow an accountant who needs this? Tag them below 👇",
    ],
}


def manual_posting_guide(args):
    """Print the manual posting guide with the thread content."""
    if args.thread:
        thread_num = int(args.thread)
        tweets = THREADS.get(thread_num, [])
        if not tweets:
            print(f"Thread {thread_num} not found. Available threads: 1, 2, 3")
            return

        print("=" * 60)
        print(f"  📝 THREAD {thread_num} — {len(tweets)} tweets")
        print("=" * 60)
        print()
        print("  MANUAL POSTING INSTRUCTIONS:")
        print("  1. Open https://x.com and log in")
        print("  2. Click the 'Post' button (or press 'n' key)")
        print("  3. Copy the FIRST tweet below and paste it")
        print("  4. Click 'Post'")
        print("  5. Wait 30 seconds")
        print("  6. Click 'Reply' on your posted tweet")
        print("  7. Paste the NEXT tweet")
        print("  8. Click 'Reply'")
        print("  9. Repeat steps 6-8 for all remaining tweets")
        print()
        for i, tweet in enumerate(tweets, 1):
            print(f"  [{i}/{len(tweets)}] {'=' * 50}")
            print(f"  {tweet}")
            print()
            if i < len(tweets):
                print(f"  → Then reply with the next tweet")
                print()

        print("=" * 60)
        print("  ✅ Post all tweets, then verify they appear on your profile")
        print()

    if args.tweet:
        print("=" * 60)
        print("  📝 SINGLE TWEET")
        print("=" * 60)
        print()
        print("  MANUAL POSTING:")
        print("  1. Open https://x.com and log in")
        print("  2. Click 'Post' or press 'n'")
        print(f"  3. Paste: {args.tweet}")
        print("  4. Click 'Post'")
        print()

    if args.all:
        for num in [1, 2, 3]:
            print(f"\n{'='*60}")
            print(f"  Thread {num}")
            print(f"{'='*60}")
            manual_posting_guide_from_list(THREADS[num], num)
            print("\n  Wait 5 minutes before posting the next thread.\n")


def manual_posting_guide_from_list(tweets, thread_num):
    """Print guide for a single thread."""
    print(f"\n  📝 THREAD {thread_num} — {len(tweets)} tweets")
    print()
    print("  Copy these tweets one at a time:")
    for i, tweet in enumerate(tweets, 1):
        print(f"\n  [{i}] {tweet}")


def main():
    parser = argparse.ArgumentParser(description="Twitter/X Browser Posting Guide")
    parser.add_argument("--tweet", help="Single tweet text")
    parser.add_argument("--thread", choices=["1", "2", "3"], help="Pre-written thread (1-3)")
    parser.add_argument("--all", action="store_true", help="Print all 3 threads")
    parser.add_argument("--list", action="store_true", help="List available threads")

    args = parser.parse_args()

    if args.list:
        print("Available threads:")
        for num, tweets in THREADS.items():
            print(f"  Thread {num}: {len(tweets)} tweets — {tweets[0][:60]}...")
        return

    if not any([args.tweet, args.thread, args.all]):
        print("Provide --tweet, --thread N, --all, or --list")
        print()
        print("Examples:")
        print("  python3 twitter_browser_post.py --thread 1")
        print("  python3 twitter_browser_post.py --all")
        print("  python3 twitter_browser_post.py --tweet \"Your tweet here\"")
        print("  python3 twitter_browser_post.py --list")
        return

    manual_posting_guide(args)


if __name__ == "__main__":
    main()
