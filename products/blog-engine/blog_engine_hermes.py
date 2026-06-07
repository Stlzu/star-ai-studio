#!/usr/bin/env python3
"""
Automated SEO Blog Content Engine — Hermes Native Version
=========================================================
Uses Hermes Agent's built-in web_search and web_extract tools for
reliable search, then generates SEO-optimized blog posts.

Usage via Hermes:
    python3 blog_engine_hermes.py --topic "Your Topic" [--keywords "kw1, kw2"]

Or within execute_code:
    from hermes_tools import terminal
    terminal("python3 blog_engine_hermes.py --topic '...'")
"""

import argparse
import json
import os
import re
import sys
import yaml
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

# Try to import Hermes tools (works when run via execute_code or with hermes_tools installed)
try:
    from hermes_tools import web_search, web_extract
    HAS_HERMES_TOOLS = True
except ImportError:
    HAS_HERMES_TOOLS = False

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

STOP_WORDS = {
    'the', 'and', 'for', 'are', 'that', 'this', 'with', 'have', 'from',
    'your', 'will', 'can', 'not', 'but', 'all', 'its', 'has', 'was',
    'you', 'our', 'their', 'they', 'been', 'more', 'some', 'what',
    'which', 'also', 'just', 'than', 'them', 'about', 'how', 'when',
    'into', 'over', 'make', 'like', 'each', 'other', 'many', 'then',
    'been', 'very', 'there', 'where', 'most', 'much', 'such', 'here',
}


# ─── Research using Hermes web_search ────────────────────────────────────────


def hermes_search(query: str, limit: int = 5) -> list[dict]:
    """Search using Hermes Agent's web_search tool."""
    if not HAS_HERMES_TOOLS:
        print("  [!] Hermes tools not available. Falling back to direct search.", file=sys.stderr)
        return fallback_search(query, limit)

    try:
        result = web_search(query=query, limit=limit)
        data = result.get("data", {})
        web_results = data.get("web", []) or data.get("results", [])
        items = []
        for r in web_results[:limit]:
            items.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("description", r.get("snippet", "")),
            })
        return items
    except Exception as e:
        print(f"  [!] Hermes search error: {e}", file=sys.stderr)
        return []


def fallback_search(query: str, limit: int = 5) -> list[dict]:
    """Fallback: use requests-based search if Hermes tools unavailable.
    Tries multiple search engines until one works.
    """
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import quote_plus, urlparse, parse_qs

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    engines = [
        ("DuckDuckGo Lite", f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"),
        ("Startpage", f"https://www.startpage.com/sp/search?query={quote_plus(query)}"),
    ]

    for name, url in engines:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            
            if "duckduckgo" in name.lower():
                for row in soup.select("table.result"):
                    link = row.select_one("a")
                    snippet = row.select_one(".snippet")
                    if link:
                        results.append({
                            "title": link.get_text(strip=True),
                            "url": str(link.get("href", "")),
                            "snippet": snippet.get_text(strip=True) if snippet else "",
                        })
            elif "startpage" in name.lower():
                for result in soup.select(".w-gl__result"):
                    title_el = result.select_one(".w-gl__result-title a")
                    snippet_el = result.select_one(".w-gl__description")
                    if title_el:
                        results.append({
                            "title": title_el.get_text(strip=True),
                            "url": str(title_el.get("href", "")),
                            "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                        })

            if results:
                return results[:limit]
        except Exception:
            continue

    return []


def hermes_extract(url: str) -> Optional[str]:
    """Extract article content using Hermes web_extract."""
    if not HAS_HERMES_TOOLS:
        return None
    try:
        result = web_extract(urls=[url])
        results = result.get("results", [])
        if results and not results[0].get("error"):
            return results[0].get("content", "")
    except Exception:
        pass
    return None


def extract_keywords(articles: list[dict]) -> list[str]:
    """Extract top keywords from article content."""
    all_text = ""
    for a in articles:
        content = a.get("content", "") or ""
        all_text += content + " "

    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
    word_freq = Counter(words)

    return [
        word for word, count in word_freq.most_common(50)
        if word not in STOP_WORDS and len(word) > 3
    ][:20]


def research_topic(topic: str, keywords=None) -> dict:
    """Full research pipeline."""
    print(f"\n  🔍 Researching: '{topic}'")

    queries = [topic]
    if keywords:
        queries.extend([f"{topic} {kw}" for kw in keywords[:3]])

    all_results = []
    seen_urls = set()
    for q in queries:
        print(f"    Searching: {q}")
        results = hermes_search(q, limit=5)
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)

    print(f"    Found {len(all_results)} unique articles")

    if not all_results:
        print("    Using fallback — generating from topic knowledge.")
        return {
            "topic": topic,
            "articles": [],
            "keywords": keywords or [topic.lower().replace(" ", "-")],
            "total_articles_found": 0,
        }

    # Extract content
    articles = []
    for i, result in enumerate(all_results[:5]):
        title = result.get("title", "Untitled")[:60]
        url = result.get("url", "")
        print(f"    Reading article {i+1}/{min(5, len(all_results))}: {title}...")

        content = hermes_extract(url) if url else None
        articles.append({
            "title": result.get("title", ""),
            "url": url,
            "snippet": result.get("snippet", ""),
            "content": content or "",
        })

    keywords_found = extract_keywords(articles)

    return {
        "topic": topic,
        "articles": articles,
        "keywords": keywords_found,
        "total_articles_found": len(all_results),
    }


# ─── Content Generation ──────────────────────────────────────────────────────


def generate_outline(topic: str) -> list[dict]:
    """Generate a blog post outline."""
    t = topic.title()
    l = topic.lower()

    sections = [
        ("introduction", "Introduction", [
            f"Hook: Why {t} matters right now",
            "Problem statement and why readers should care",
            "What this article will cover",
        ]),
        ("background", f"What Is {t}?", [
            "Clear definition and explanation",
            "Why it's gaining traction",
            "Key concepts to understand",
        ]),
        ("benefits", f"Top Benefits of {t}", [
            "Benefit 1 with real-world example",
            "Benefit 2 with data/evidence",
            "Benefit 3 — the one most people miss",
            "How it compares to alternatives",
        ]),
        ("implementation", f"How to Get Started with {t}", [
            "Step 1: Prerequisites and preparation",
            "Step 2: First implementation",
            "Step 3: Optimization and iteration",
            "Common pitfalls to avoid",
        ]),
        ("examples", "Real-World Examples", [
            f"Example 1: Company/individual who succeeded with {l}",
            "Example 2: Different approach, same great results",
            "Key lessons from these examples",
        ]),
        ("future", f"The Future of {t}", [
            "Emerging trends to watch",
            f"Prediction for the next 12-24 months in {l}",
            "How to stay ahead",
        ]),
        ("conclusion", "Conclusion", [
            f"Summary of key takeaways about {l}",
            "Call to action",
            "Resources for further learning",
        ]),
    ]
    return [{"section": s, "title": t, "points": p} for s, t, p in sections]


def generate_blog_post(topic: str, research: dict, keywords: list) -> str:
    """Generate the full blog post content."""
    kw = keywords or research.get("keywords", [])[:10]
    outline = generate_outline(topic)

    t = topic.title()
    l = topic.lower()
    today = datetime.now().strftime("%Y-%m-%d")

    parts = []

    # Title
    title = f"{t}: The Complete Guide for 2025"
    parts.append(f"# {title}")
    parts.append("")

    # Frontmatter
    meta = {
        "title": title,
        "date": today,
        "description": f"A comprehensive guide to {l}, including benefits, strategies, examples, and insights.",
        "tags": [l] + [str(k).lower() for k in kw[:7]],
        "reading_time": "8 min read",
    }
    parts.append("---")
    parts.append(yaml.dump(meta, default_flow_style=False).strip())
    parts.append("---")
    parts.append("")

    # Introduction
    parts.append("## Introduction")
    parts.append("")

    snippets = [a.get("snippet", "") for a in research.get("articles", [])[:3] if a.get("snippet")]
    if snippets:
        parts.append(f"{snippets[0]}")
        parts.append("")
        if len(snippets) > 1:
            parts.append(f"> *{snippets[1]}*")
            parts.append("")

    parts.append(f"In this comprehensive guide, we'll explore everything you need to know about {l}, including:")
    parts.append("")
    for s in outline[1:-1]:
        parts.append(f"- **{s['title']}**")
    parts.append("")
    parts.append(f"By the end, you'll have a clear roadmap for implementing {l} effectively.")
    parts.append("")

    # Body sections
    for section in outline[1:-1]:
        parts.append(f"## {section['title']}")
        parts.append("")

        for point in section["points"]:
            parts.append(f"### {point}")
            parts.append("")

            found_content = None
            for article in research.get("articles", []):
                ac = article.get("content", "") or ""
                search_words = point.lower().split()[:5]
                if any(w in ac.lower() for w in search_words if len(w) > 3):
                    found_content = ac[:400]
                    break

            if found_content:
                parts.append(f"{found_content}...")
            else:
                parts.append(f"_[Content target: {point.lower()}]_")
            parts.append("")

    # Conclusion
    parts.append("## Conclusion")
    parts.append("")
    parts.append(f"{t} is rapidly evolving, and the strategies in this guide provide a solid foundation for success.")
    parts.append("")
    parts.append("**Key takeaways:**")
    parts.append("")
    parts.append(f"- {t} offers significant advantages for those who implement it correctly")
    parts.append("- Focus on fundamentals before optimization")
    parts.append("- Learn from real-world examples and case studies")
    parts.append("- Stay updated as the landscape evolves")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(f"*Generated by the Automated SEO Blog Content Engine using [Hermes Agent](https://hermes-agent.nousresearch.com)*")
    parts.append("")

    return "\n".join(parts)


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Automated SEO Blog Content Engine (Hermes Native)")
    parser.add_argument("--topic", "-t", required=True, help="Blog post topic")
    parser.add_argument("--keywords", "-k", help="Comma-separated target keywords")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--research-only", action="store_true", help="Only research, don't generate")

    args = parser.parse_args()
    topic = args.topic
    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else None

    mode = "Hermes-powered" if HAS_HERMES_TOOLS else "Fallback (standalone)"
    print(f"\n{'='*60}")
    print(f"  📝 Automated SEO Blog Content Engine")
    print(f"  Mode: {mode}")
    print(f"  Topic: {topic}")
    print(f"{'='*60}")

    research = research_topic(topic, keywords)

    safe = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "-")[:30]
    res_path = OUTPUT_DIR / f"research-{safe}.json"
    res_path.write_text(json.dumps(research, indent=2), encoding="utf-8")
    print(f"\n  📊 Research saved to: {res_path}")

    if args.research_only:
        print(f"\n  ✅ Research complete! Found {research['total_articles_found']} articles.")
        if research.get("keywords"):
            print(f"  Top keywords: {', '.join(research['keywords'][:10])}")
        return

    print(f"\n  ✍️  Generating blog post...")
    kws = keywords or research.get("keywords") or []
    content = generate_blog_post(topic, research, kws)

    out_path = OUTPUT_DIR / (args.output or f"{safe}.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    wc = len(content.split())
    print(f"\n  ✅ Blog post generated!")
    print(f"  📄 Saved to: {out_path}")
    print(f"  📝 Word count: {wc}")
    if research.get("keywords"):
        print(f"  🏷️  Keywords: {', '.join(research['keywords'][:10])}")

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Title: {topic}")
    print(f"  Research sources: {research['total_articles_found']} articles")
    print(f"  Content length: {wc} words")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
