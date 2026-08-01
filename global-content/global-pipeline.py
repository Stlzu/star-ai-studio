#!/usr/bin/env python3
"""
Global Content Pipeline — unified daily content generation + posting
for TikTok, YouTube Shorts, and Xiaohongshu.

Runs as a cron job. Each run:
  1. Generates content (via content-engine.py)
  2. Creates video (via short-video-maker.py)
  3. Creates image cards (via card-maker.py)
  4. Posts to configured platforms

Usage:
  python3 global-pipeline.py                        # Full pipeline: gen + post all
  python3 global-pipeline.py --dry-run               # Preview only
  python3 global-pipeline.py --platform tiktok       # One platform only
  python3 global-pipeline.py --gen-only              # Generate content only, no posting
  python3 global-pipeline.py --status                # Check file counts and last post times
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HOME = Path.home()
BASE_DIR = HOME / "star-ai-studio" / "global-content"
CONTENT_ENGINE = BASE_DIR / "content-engine.py"
VIDEO_MAKER = BASE_DIR / "short-video-maker.py"
CARD_MAKER = BASE_DIR / "card-maker-article.py"
TIKTOK_POSTER = BASE_DIR / "tiktok-poster.py"
YOUTUBE_POSTER = BASE_DIR / "youtube-poster.py"
XHS_POSTER = BASE_DIR / "xiaohongshu-poster.py"
LINKEDIN_POSTER = Path.home() / "star-ai-studio" / "scripts" / "linkedin-post.py"
POST_LOG = BASE_DIR / "post.log"
VIDEOS_DIR = BASE_DIR / "videos"
CARDS_DIR = BASE_DIR / "cards"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    with open(POST_LOG, "a") as f:
        f.write(f"{timestamp}|{msg}\n")


def run_script(script_path, args_list, desc, timeout=600):
    """Run a Python script and return success/failure."""
    if not script_path.exists():
        log(f"❌ {desc}: script not found at {script_path}")
        return False

    cmd = [sys.executable, str(script_path)] + args_list
    log(f"▶ Running {desc}...")
    log(f"  $ {' '.join(cmd[-5:])}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(BASE_DIR),
        )
        out = result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
        err = result.stderr[-300:] if result.stderr else ""
        if result.returncode == 0:
            log(f"✅ {desc} succeeded")
            if out:
                for line in out.strip().split("\n")[-3:]:
                    if line.strip():
                        log(f"  {line.strip()}")
            return True
        else:
            log(f"❌ {desc} failed (exit={result.returncode})")
            if err:
                log(f"  Error: {err[:200]}")
            return False
    except subprocess.TimeoutExpired:
        log(f"⏰ {desc} timed out ({timeout}s)")
        return False
    except Exception as e:
        log(f"💥 {desc} crashed: {e}")
        return False


def find_latest_video():
    """Find the most recent video in the videos dir."""
    if not VIDEOS_DIR.exists():
        return None
    videos = sorted(VIDEOS_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
    return str(videos[0]) if videos else None


def find_latest_cards():
    """Find the most recent cards in the cards dir."""
    if not CARDS_DIR.exists():
        return []
    cards = sorted(CARDS_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
    return [str(c) for c in cards[:10]] if cards else []


def get_latest_content_file(platform):
    """Find the most recent content JSON for a platform."""
    files = sorted(BASE_DIR.glob(f"{platform}_*.json"), key=os.path.getmtime, reverse=True)
    return str(files[0]) if files else None


def main():
    parser = argparse.ArgumentParser(description="Global Content Pipeline")
    parser.add_argument("--platform", choices=["tiktok", "youtube", "xiaohongshu", "linkedin", "all"],
                        default="all", help="Platform(s) to generate for and post to")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no posting")
    parser.add_argument("--gen-only", action="store_true", help="Generate content only, no posting")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--count", type=int, default=1, help="Number of content pieces (default: 1)")
    args = parser.parse_args()

    # ── Status Mode ──
    if args.status:
        print("=" * 55)
        print(f"📊 Global Content Pipeline — Status Report")
        print("=" * 55)

        # Content files
        print(f"\n📄 Content files:")
        for platform in ["tiktok", "youtube", "xiaohongshu"]:
            files = sorted(BASE_DIR.glob(f"{platform}_*.json"),
                           key=os.path.getmtime, reverse=True)
            if files:
                mtime = datetime.fromtimestamp(os.path.getmtime(files[0]))
                print(f"  {platform}: {len(files)} files, latest: {mtime.strftime('%m/%d %H:%M')}")
            else:
                print(f"  {platform}: 0 files")

        # Videos
        vids = sorted(VIDEOS_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
        print(f"\n🎬 Videos: {len(vids)} files")
        if vids:
            total_mb = sum(os.path.getsize(v) for v in vids) / (1024 * 1024)
            print(f"  Total: {total_mb:.1f} MB")
            print(f"  Latest: {vids[0].name}")

        # Cards
        cards = sorted(CARDS_DIR.glob("*.png"), key=os.path.getmtime, reverse=True)
        print(f"\n🖼️  Image cards: {len(cards)} files")
        if cards:
            print(f"  Latest: {cards[0].name}")

        # Post log
        if POST_LOG.exists():
            lines = POST_LOG.read_text().strip().split("\n")
            posts = [l for l in lines if "Posted to" in l or "✅" in l]
            print(f"\n📋 Post history: {len(posts)} posts logged")
            for p in posts[-5:]:
                print(f"  {p[:120]}")
        else:
            print(f"\n📋 No post history yet")

        return

    # ── Determine platforms ──
    platforms = {
        "all": ["tiktok", "youtube", "xiaohongshu", "linkedin"],
        "tiktok": ["tiktok"],
        "youtube": ["youtube"],
        "xiaohongshu": ["xiaohongshu"],
        "linkedin": ["linkedin"],
    }[args.platform]

    log(f"🚀 Global Content Pipeline starting — {', '.join(platforms)}")
    log(f"{'=' * 50}")

    # ── Step 1: Generate Content ──
    log(f"\n{'─' * 40}")
    log("📝 Step 1: Generating content...")

    # Generate for each platform (skip linkedin — uses same content as other channels)
    for platform in platforms:
        if platform == "linkedin":
            log(f"  ⏩ Skipping content generation for {platform} (uses same content)")
            continue
        success = run_script(
            CONTENT_ENGINE,
            ["--count", str(args.count), "--platform", platform, "--seed-news"],
            f"content-gen ({platform})",
        )
        if not success:
            log(f"⚠  Content generation for {platform} failed, continuing...")

    if args.gen_only:
        log(f"\n✅ Gen-only mode. Content ready in {BASE_DIR}")
        return

    # ── Step 2: Create Videos (for TikTok + YouTube) ──
    if "tiktok" in platforms or "youtube" in platforms:
        log(f"\n{'─' * 40}")
        log("🎬 Step 2: Creating videos...")

        for platform in ["tiktok", "youtube"]:
            if platform not in platforms:
                continue

            content_file = get_latest_content_file(platform)
            if not content_file:
                log(f"⚠  No content file for {platform}, skipping video creation")
                continue

            success = run_script(
                VIDEO_MAKER,
                [content_file],
                f"video-make ({platform})",
                timeout=600,
            )
            if not success:
                log(f"⚠  Video creation for {platform} failed")

    # ── Step 3: Create Article Cards (for Xiaohongshu) ──
    if "xiaohongshu" in platforms:
        log(f"\n{'─' * 40}")
        log("🖼️  Step 3: Creating article-style image cards...")

        # Generate article content first
        article_gen = BASE_DIR / "article-generator.py"
        if article_gen.exists():
            log("  📝 Generating article content...")
            gen_ok = run_script(
                article_gen,
                ["--count", "1"],
                "article-gen (xiaohongshu)",
                timeout=30,
            )
            if gen_ok:
                # Find the latest article JSON
                import glob
                article_files = sorted(BASE_DIR.glob("article_*.json"),
                                       key=os.path.getmtime, reverse=True)
                if article_files:
                    content_file = str(article_files[0])
                    log(f"  Using: {Path(content_file).name}")
                    success = run_script(
                        CARD_MAKER,
                        [content_file],
                        "card-make (article)",
                        timeout=120,
                    )
                    if not success:
                        log("⚠  Article card creation failed")
                else:
                    log("⚠  No article file found")
            else:
                log("⚠  Article generation failed")
        else:
            log("⚠  No content file for xiaohongshu, skipping card creation")

    if args.dry_run:
        log(f"\n📋 DRY RUN — Would post:")
        if "tiktok" in platforms:
            vid = find_latest_video()
            log(f"   TikTok: {vid or 'No video found'}")
        if "youtube" in platforms:
            vid = find_latest_video()
            log(f"   YouTube: {vid or 'No video found'}")
        if "xiaohongshu" in platforms:
            cards = find_latest_cards()
            log(f"   Xiaohongshu: {len(cards)} cards")
        if "linkedin" in platforms:
            log(f"   LinkedIn: Post text from latest content")
        log(f"\n✅ Dry run complete.")
        return

    # ── Step 4: Post to Platforms ──
    log(f"\n{'─' * 40}")
    log("📤 Step 4: Posting to platforms...")

    if "tiktok" in platforms:
        video_path = find_latest_video()
        if video_path and os.path.exists(video_path):
            # Extract a short caption from the content file
            content_file = get_latest_content_file("tiktok")
            description = ""
            if content_file:
                try:
                    with open(content_file) as f:
                        data = json.load(f)
                    script = data.get("script", "")
                    # First 150 chars as description
                    desc_lines = script.strip().split("\n")[:3]
                    description = " | ".join(l.strip() for l in desc_lines if l.strip())[:200]
                except Exception:
                    pass

            # Append product CTA to TikTok description — rotating through all 4 products
            from datetime import date
            day_of_year = date.today().timetuple().tm_yday
            product_ctas = [
                " 🔧 Built with LocalDoc: starlit8302.gumroad.com/l/localdoc",
                " 📄 Extract invoices: starlit8302.gumroad.com/l/invoice-extractor-pro",
                " ✍️ SEO Blog Engine: starlit8302.gumroad.com/l/seo-blog-engine",
                " 🕸️ Web scraping service: starlit8302.gumroad.com",
            ]
            product_cta = product_ctas[day_of_year % 4]
            desc_with_cta = (description + product_cta)[:280]

            success = run_script(
                TIKTOK_POSTER,
                [video_path] + (["--description", desc_with_cta] if desc_with_cta else []),
                "tiktok-post",
                timeout=180,
            )
            if success:
                log(f"✅ Posted to TikTok: {video_path}")

    if "youtube" in platforms:
        video_path = find_latest_video()
        if video_path and os.path.exists(video_path):
            content_file = get_latest_content_file("youtube")
            title = ""
            description = ""
            if content_file:
                try:
                    with open(content_file) as f:
                        data = json.load(f)
                    script = data.get("script", "")
                    lines = script.strip().split("\n")
                    title = lines[0][:100] if lines else "AI News Update"
                    description = "\n".join(l.strip() for l in lines[1:6])

                    # Add tags and rotating product links
                    tags = data.get("tags", [])
                    tag_line = "\n\n#AI #Tech #News " + " ".join(f"#{t}" for t in tags[:5])
                    from datetime import date
                    _doy = date.today().timetuple().tm_yday
                    _product_links = [
                        "\n🔧 Built with LocalDoc: https://starlit8302.gumroad.com/l/localdoc",
                        "\n📄 Extract invoices: https://starlit8302.gumroad.com/l/invoice-extractor-pro",
                        "\n✍️ SEO Blog Engine: https://starlit8302.gumroad.com/l/seo-blog-engine",
                        "\n🕸️ Web scraping service: https://starlit8302.gumroad.com",
                    ]
                    tag_line += _product_links[_doy % 4]
                    description += tag_line
                except Exception:
                    pass

            args_list = [video_path]
            if title:
                args_list += ["--title", title]
            if description:
                args_list += ["--desc", description]
            args_list += ["--public"]  # Public for discoverability

            success = run_script(
                YOUTUBE_POSTER,
                args_list,
                "youtube-post",
                timeout=600,
            )
            if success:
                log(f"✅ Posted to YouTube Shorts: {title}")

    if "xiaohongshu" in platforms:
        cards = find_latest_cards()
        if cards:
            content_file = get_latest_content_file("xiaohongshu")
            title = ""
            text = ""
            tags = []
            if content_file:
                try:
                    with open(content_file) as f:
                        data = json.load(f)
                    title = data.get("caption", "")[:50]
                    text = data.get("caption", "")
                    tags = data.get("tags", [])
                except Exception:
                    pass

            # Rotating Gumroad product link for XHS
            from datetime import date
            _xhs_doy = date.today().timetuple().tm_yday
            _xhs_product_ctas = [
                "\n\n🔧 用 LocalDoc 制作: starlit8302.gumroad.com/l/localdoc",
                "\n\n📄 发票提取工具: starlit8302.gumroad.com/l/invoice-extractor-pro",
                "\n\n✍️ SEO 博客引擎: starlit8302.gumroad.com/l/seo-blog-engine",
                "\n\n🕸️ 网页数据抓取服务: starlit8302.gumroad.com",
            ]
            _xhs_cta = _xhs_product_ctas[_xhs_doy % 4]

            args_list = ["--images"] + cards[:6]
            if title:
                args_list += ["--title", title]
            if text:
                text_with_cta = text[:400] + _xhs_cta
                args_list += ["--text", text_with_cta[:500]]
            if tags:
                args_list += ["--tags"] + tags[:3]

            success = run_script(
                XHS_POSTER,
                args_list,
                "xiaohongshu-post",
                timeout=300,
            )
            if success:
                log(f"✅ Posted to Xiaohongshu: {len(cards)} cards")

    # ── LinkedIn Posting ──
    if "linkedin" in platforms:
        # LinkedIn session expired — user needs to log in manually in Chrome.
        # The AppleScript injection script exists at scripts/linkedin-post.py
        # but requires a valid LinkedIn session.
        # Skip until the user logs into linkedin.com in Chrome.
        log(f"  ⏸ LinkedIn skipped — session expired. Log into linkedin.com in Chrome to restore.")
        log(f"     Script ready: ~/star-ai-studio/scripts/linkedin-post.py")

    # ── Summary ──
    log(f"\n{'=' * 50}")
    log(f"✅ Pipeline complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"{'=' * 50}")


if __name__ == "__main__":
    main()
