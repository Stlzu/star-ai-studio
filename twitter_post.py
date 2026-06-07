#!/usr/bin/env python3
"""
Twitter Posting Tool — Post threads to X/Twitter
=================================================
Uses Twitter API v2 via Tweepy (OAuth 1.0a User Context).

Usage:
    python3 twitter_post.py --tweet "Your tweet text"
    python3 twitter_post.py --thread 1      # Post Thread 1 (SEO Blog Engine)
    python3 twitter_post.py --thread 2      # Post Thread 2 (Lead Enrichment)
    python3 twitter_post.py --thread 3      # Post Thread 3 (Invoice Extractor)
    python3 twitter_post.py --all           # Post all 3 threads
"""

import argparse
import sys
import time
from pathlib import Path

# Load config
CONFIG_PATH = Path(__file__).parent / "twitter_config.py"
if not CONFIG_PATH.exists():
    print("❌ twitter_config.py not found. Create it with your API keys.")
    sys.exit(1)

config = {}
exec(CONFIG_PATH.read_text(), config)

try:
    import tweepy
except ImportError:
    print("❌ tweepy not installed. Run: pip3 install tweepy")
    sys.exit(1)

# ─── Auth ───────────────────────────────────────────────────────────────────

def get_client():
    """Get authenticated Tweepy client."""
    client = tweepy.Client(
        consumer_key=config["CONSUMER_KEY"],
        consumer_secret=config["CONSUMER_SECRET"],
        access_token=config["ACCESS_TOKEN"],
        access_token_secret=config["ACCESS_TOKEN_SECRET"],
    )
    return client


# ─── Posting ────────────────────────────────────────────────────────────────

def post_tweet(client, text: str, reply_to: str = None) -> str:
    """Post a single tweet. Returns the tweet ID."""
    try:
        if reply_to:
            response = client.create_tweet(text=text, in_reply_to_tweet_id=reply_to)
        else:
            response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"  ✅ Posted (ID: {tweet_id})")
        print(f"     {text[:80]}...")
        return tweet_id
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return None


def post_thread(client, tweets: list[str], delay: float = 2.0):
    """Post a thread of tweets, each replying to the previous."""
    print(f"\n  📝 Posting thread with {len(tweets)} tweets...")
    prev_id = None
    for i, tweet in enumerate(tweets, 1):
        print(f"\n  [{i}/{len(tweets)}] ", end="")
        tweet_id = post_tweet(client, tweet, reply_to=prev_id)
        if not tweet_id:
            print(f"  Stopping thread at tweet {i}")
            break
        prev_id = tweet_id
        if i < len(tweets):
            time.sleep(delay)
    print(f"\n  ✅ Thread complete! ({i} tweets posted)" if i == len(tweets) else f"\n  ⚠️  Thread incomplete ({i}/{len(tweets)} tweets)")


# ─── Thread Content ─────────────────────────────────────────────────────────

THREADS = {
    1: [
        "I built an AI blog content engine that researches the web and writes SEO-optimized posts. In 2 hours. With Hermes Agent. Here's how. 🧵👇",
        "The problem: Content marketing works but it's expensive. Agencies charge $500-2,000/post. Freelancers take 3-5 days. Most businesses can't keep up.",
        "The solution: An AI agent that does the entire content pipeline: Research → Analyze → Generate → Format → Publish. No human needed between topic and post.",
        "How it works: Give it a topic → it searches 8+ articles → extracts key insights → generates a 685+ word post with SEO frontmatter, headings, and real examples. All in 2 minutes.",
        "The output: Ready-to-publish markdown with YAML metadata, keyword tags, reading time, and structured sections. Compatible with any static site (Hugo, Jekyll, Ghost).",
        "The business model: $297/mo for 30 posts. At 50 customers = $14,850/mo MRR. Zero marginal cost. 1% of agency prices.",
        "Full code on GitHub: https://github.com/Stlzu/star-ai-studio\n\nDM me if you want a custom automation tool for your business. I'm taking 5 beta clients at 50% off.",
    ],
    2: [
        "Sales teams waste 30% of time researching leads. I built a tool that does it in 5 seconds. Here's how. 🧵👇",
        "The problem: An SDR spends 5-10 minutes researching each company before a call. For 50 calls/week = 4-8 hours of research. That's $75K/year in wasted salary for a team of 5.",
        "The solution: Paste company names → the AI enriches every field automatically: website, description, industry, LinkedIn, location, size. Ready for CRM import in CSV.",
        "The demo: 3 companies (Nous Research, Anthropic, Hugging Face) → enriched in 15 seconds. Real data from web search. Consistent. Accurate. No human fatigue.",
        "The business model: $197/mo for 2,000 companies. At 50 customers = $9,850/mo MRR. 10x faster than manual research.",
        "Built with Python + Hermes Agent. Full code: https://github.com/Stlzu/star-ai-studio\n\nWant me to enrich your lead list? DM me.",
    ],
    3: [
        "Accountants spend 40-80 hours/month on manual data entry. I built an AI that does it in seconds. Here's how. 🧵👇",
        "The problem: 500 invoices/month = 40-80 hours of manual entry. Errors, fatigue, and expensive labor. Most accounting firms hate this work.",
        "The solution: Upload PDF → AI extracts every field: invoice #, date, vendor, line items, amounts, tax, total. Outputs CSV or JSON.",
        "The demo: Extracted 12 fields from a sample invoice with 100% accuracy in under 1 second. Including 4 line items with descriptions and amounts.",
        "The business model: $297/mo for 5,000 invoices. At 30 accounting firms = $8,910/mo MRR. Eliminates a full-time data entry position.",
        "Built with Python + pdftotext. Full code: https://github.com/Stlzu/star-ai-studio\n\nKnow an accountant who needs this? Tag them below 👇",
    ],
}


# ─── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Post tweets to X/Twitter")
    parser.add_argument("--tweet", help="Post a single tweet")
    parser.add_argument("--thread", type=int, choices=[1, 2, 3], help="Post a pre-written thread (1-3)")
    parser.add_argument("--all", action="store_true", help="Post all 3 threads")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between tweets in seconds")

    args = parser.parse_args()

    client = get_client()

    # Verify auth by getting user info
    try:
        me = client.get_me()
        print(f"  👤 Logged in as: @{me.data.username}")
    except Exception as e:
        print(f"  ❌ Auth failed: {e}")
        print("  Check your API keys in twitter_config.py")
        sys.exit(1)

    if args.tweet:
        post_tweet(client, args.tweet)

    elif args.thread:
        thread = THREADS.get(args.thread)
        if thread:
            post_thread(client, thread, args.delay)
        else:
            print(f"  ❌ Thread {args.thread} not found")

    elif args.all:
        for num in [1, 2, 3]:
            print(f"\n{'='*50}")
            print(f"  Thread {num}")
            print(f"{'='*50}")
            post_thread(client, THREADS[num], args.delay)
            if num < 3:
                print("\n  Waiting 30 seconds before next thread...")
                time.sleep(30)

    else:
        print("  Provide --tweet, --thread N, or --all")
        print("  Examples:")
        print("    python3 twitter_post.py --tweet \"Hello world\"")
        print("    python3 twitter_post.py --thread 1")
        print("    python3 twitter_post.py --all")


if __name__ == "__main__":
    main()
