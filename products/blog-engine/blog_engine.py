#!/usr/bin/env python3
"""
Automated SEO Blog Content Engine
Built with AI tools — research, generate, and publish blog posts autonomously.

Usage:
    python blog_engine.py --topic "Your Topic" [--keywords "kw1, kw2"] [--output output.md]
"""

import argparse
import json
import os
import re
import sys
import time
import yaml
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

# ─── Configuration ───────────────────────────────────────────────────────────

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

HEADERS = {"User-Agent": USER_AGENT}

SEARCH_ENGINES = {
    "duckduckgo": "https://html.duckduckgo.com/html/?q={query}",
    "startpage": "https://www.startpage.com/sp/search?query={query}",
}


# ─── Web Research ────────────────────────────────────────────────────────────


def search_web(query: str, num_results: int = 5) -> list[dict]:
    """Search the web using multiple free search backends."""
    results = []

    # Try DuckDuckGo
    url = SEARCH_ENGINES["duckduckgo"].format(query=quote_plus(query))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        for result in soup.select(".result")[:num_results]:
            title_el = result.select_one(".result__title a")
            snippet_el = result.select_one(".result__snippet")
            if title_el:
                href = str(title_el.get("href", ""))
                # Extract URL from DuckDuckGo redirect
                actual_url = href
                if "uddg=" in href:
                    actual_url = parse_qs(urlparse(href).query).get("uddg", [href])[0]
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": actual_url,
                    "snippet": snippet,
                })
    except Exception as e:
        print(f"    [!] DuckDuckGo search failed: {e}", file=sys.stderr)

    # If DuckDuckGo returned nothing, try Startpage
    if not results:
        try:
            url = SEARCH_ENGINES["startpage"].format(query=quote_plus(query))
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select(".w-gl__result")[:num_results]:
                title_el = result.select_one(".w-gl__result-title a")
                snippet_el = result.select_one(".w-gl__description")
                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": str(title_el.get("href", "")),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
        except Exception as e:
            print(f"    [!] Startpage search failed: {e}", file=sys.stderr)

    # Last resort: use Google via requests (can be flaky without proper headers)
    if not results:
        try:
            gurl = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            resp = requests.get(gurl, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            for g in soup.select("div.g")[:num_results]:
                title_el = g.select_one("h3")
                link_el = g.select_one("a")
                snippet_el = g.select_one(".VwiC3b")
                if title_el and link_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": str(link_el.get("href", "")),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
        except Exception as e:
            print(f"    [!] Google search failed: {e}", file=sys.stderr)

    return results


def extract_article_content(url: str) -> dict:
    """Extract readable content from an article URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"url": url, "error": str(e), "content": ""}

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else ""

    # Try to find main content
    main = (
        soup.find("article")
        or soup.find("main")
        or soup.find("body")
    )
    text = main.get_text(separator="\n", strip=True) if main else ""

    # Clean up whitespace and limit length
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    content = "\n".join(lines[:200])

    return {
        "url": url,
        "title": title,
        "content": content,
        "word_count": len(content.split()),
    }


def research_topic(topic: str, keywords) -> dict:
    """Full research pipeline: search, extract, analyze."""
    print(f"\n  🔍 Researching: '{topic}'")

    # Multiple search queries for comprehensive research
    queries = [topic]
    if keywords:
        queries.extend([f"{topic} {kw}" for kw in keywords[:3]])

    all_results = []
    seen_urls = set()
    for q in queries:
        print(f"    Searching: {q}")
        results = search_web(q, num_results=5)
        for r in results:
            url = r["url"]
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)

    print(f"    Found {len(all_results)} unique articles")

    if not all_results:
        print("    [!] No search results found. Using fallback mode.")
        return {
            "topic": topic,
            "articles": [],
            "keywords": keywords or [topic.lower().replace(" ", "-")],
            "total_articles_found": 0,
        }

    # Extract content from top articles
    articles = []
    for i, result in enumerate(all_results[:5]):
        title = result.get("title", "Untitled")[:60]
        print(f"    Reading article {i+1}/{min(5, len(all_results))}: {title}...")
        article = extract_article_content(result["url"])
        article["title"] = result.get("title", article.get("title", ""))
        article["snippet"] = result.get("snippet", "")
        articles.append(article)
        time.sleep(0.5)  # Be polite

    # Extract common keywords and concepts from all article content
    all_text = ""
    for a in articles:
        content = a.get("content", "") or ""
        all_text += content + " "

    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
    word_freq = Counter(words)

    # Filter common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'that', 'this', 'with', 'have', 'from',
        'your', 'will', 'can', 'not', 'but', 'all', 'its', 'has', 'was',
        'you', 'our', 'their', 'they', 'been', 'more', 'some', 'what',
        'which', 'also', 'just', 'than', 'them', 'about', 'how', 'when',
        'into', 'over', 'make', 'like', 'each', 'other', 'many', 'then',
        'been', 'very', 'there', 'where', 'most', 'much', 'such', 'here',
    }

    keywords_found = [
        word for word, count in word_freq.most_common(50)
        if word not in stop_words and len(word) > 3
    ][:20]

    return {
        "topic": topic,
        "articles": articles,
        "keywords": keywords_found,
        "total_articles_found": len(all_results),
    }


# ─── Content Generation ──────────────────────────────────────────────────────


def generate_outline(topic: str) -> list[dict]:
    """Generate a blog post outline from research data."""
    # Use string formatting without f-strings to avoid issues
    topic_title = topic.title()
    topic_lower = topic.lower()

    outline = [
        ("introduction", "Introduction",
         [
             f"Hook: Why {topic} matters right now",
             "Problem statement and why readers should care",
             "What this article will cover",
         ]),
        ("background", f"What Is {topic_title}?",
         [
             "Clear definition and explanation",
             "Why it's gaining traction",
             "Key concepts to understand",
         ]),
        ("benefits", f"Top Benefits of {topic_title}",
         [
             "Benefit 1 with real-world example",
             "Benefit 2 with data/evidence",
             "Benefit 3 — the one most people miss",
             "How it compares to alternatives",
         ]),
        ("implementation", f"How to Get Started with {topic_title}",
         [
             "Step 1: Prerequisites and preparation",
             "Step 2: First implementation",
             "Step 3: Optimization and iteration",
             "Common pitfalls to avoid",
         ]),
        ("case-studies", "Real-World Examples",
         [
             f"Example 1: Company/individual who succeeded with {topic_lower}",
             "Example 2: Different approach, same great results",
             "Key lessons from these examples",
         ]),
        ("future", f"The Future of {topic_title}",
         [
             "Emerging trends to watch",
             f"Prediction for the next 12-24 months in {topic_lower}",
             "How to stay ahead",
         ]),
        ("conclusion", "Conclusion",
         [
             f"Summary of key takeaways about {topic_lower}",
             "Call to action",
             "Resources for further learning",
         ]),
    ]

    return [{"section": s, "title": t, "points": p} for s, t, p in outline]


def generate_blog_post(topic: str, research: dict, keywords) -> str:
    """Generate the full blog post content from research data."""
    kw = keywords or research.get("keywords", [])[:10]
    outline = generate_outline(topic)

    topic_title = topic.title()
    topic_lower = topic.lower()
    today = datetime.now().strftime("%Y-%m-%d")

    parts = []

    # ── Title ──
    title = f"{topic_title}: The Complete Guide for 2025"
    parts.append(f"# {title}")
    parts.append("")

    # ── YAML Frontmatter ──
    meta = {
        "title": title,
        "date": today,
        "description": f"A comprehensive guide to {topic_lower}, including benefits, implementation strategies, real-world examples, and expert insights.",
        "tags": [topic_lower] + [str(k).lower() for k in kw[:7]],
        "reading_time": "8 min read",
    }
    parts.append("---")
    parts.append(yaml.dump(meta, default_flow_style=False).strip())
    parts.append("---")
    parts.append("")

    # ── Introduction ──
    parts.append("## Introduction")
    parts.append("")

    # Use research snippets for a compelling intro
    snippets = []
    for a in research.get("articles", [])[:3]:
        s = a.get("snippet", "")
        if s:
            snippets.append(s)

    if snippets:
        parts.append(f"{snippets[0]}")
        parts.append("")
        if len(snippets) > 1:
            parts.append(f"> *{snippets[1]}*")
            parts.append("")

    parts.append(f"In this comprehensive guide, we'll explore everything you need to know about {topic_lower}, including:")
    parts.append("")
    for s in outline[1:-1]:
        parts.append(f"- **{s['title']}**")
    parts.append("")
    parts.append(f"By the end, you'll have a clear roadmap for implementing {topic_lower} effectively.")
    parts.append("")

    # ── Body Sections ──
    for section in outline[1:-1]:
        parts.append(f"## {section['title']}")
        parts.append("")

        for point in section["points"]:
            parts.append(f"### {point}")
            parts.append("")

            # Try to find relevant content from research
            found_content = None
            for article in research.get("articles", []):
                article_content = article.get("content", "") or ""
                search_words = point.lower().split()[:5]
                if any(w in article_content.lower() for w in search_words if len(w) > 3):
                    # Found a relevant article, take a chunk
                    found_content = article_content[:400]
                    break

            if found_content:
                parts.append(f"{found_content}...")
            else:
                parts.append(f"_[This section will cover: {point.lower()}]_")
            parts.append("")

    # ── Conclusion ──
    parts.append("## Conclusion")
    parts.append("")
    parts.append(f"{topic_title} is rapidly evolving, and the strategies outlined in this guide provide a solid foundation for success.")
    parts.append("")
    parts.append("**Key takeaways:**")
    parts.append("")
    parts.append(f"- {topic_title} offers significant advantages for those who implement it correctly")
    parts.append("- Focus on fundamentals before optimization")
    parts.append("- Learn from real-world examples and case studies")
    parts.append("- Stay updated as the landscape evolves")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(f"*This article was researched and generated using the Automated SEO Blog Content Engine.*")
    parts.append("")

    return "\n".join(parts)


# ─── CLI ─────────────────────────────────────────────────────────────────────


def save_article(content: str, output_path: str = None) -> Path:
    """Save generated article to a file."""
    if output_path:
        path = Path(output_path)
    else:
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else "blog-post"
        safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
        path = OUTPUT_DIR / f"{safe_title}.md"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Automated SEO Blog Content Engine — research and generate blog posts"
    )
    parser.add_argument("--topic", "-t", required=True, help="Blog post topic")
    parser.add_argument("--keywords", "-k", help="Comma-separated target keywords")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--research-only", action="store_true",
                        help="Only perform research, don't generate content")

    args = parser.parse_args()
    topic = args.topic
    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else None

    print(f"\n{'='*60}")
    print(f"  📝 Automated SEO Blog Content Engine")
    print(f"  Topic: {topic}")
    print(f"{'='*60}")

    # Phase 1: Research
    research = research_topic(topic, keywords)
    # Save research data
    safe_filename = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "-")[:30]
    research_path = OUTPUT_DIR / f"research-{safe_filename}.json"
    research_path.write_text(json.dumps(research, indent=2), encoding="utf-8")
    print(f"\n  📊 Research saved to: {research_path}")

    if args.research_only:
        print(f"\n  ✅ Research complete! Found {research['total_articles_found']} articles.")
        kw = research.get("keywords", [])
        if kw:
            print(f"  Top keywords: {', '.join(kw[:10])}")
        return

    # Phase 2: Generate
    print(f"\n  ✍️  Generating blog post...")
    keywords_display = keywords or research.get("keywords") or []
    content = generate_blog_post(topic, research, keywords_display)

    output_path = save_article(content, args.output)
    word_count = len(content.split())
    print(f"\n  ✅ Blog post generated!")
    print(f"  📄 Saved to: {output_path}")
    print(f"  📝 Word count: {word_count}")
    kw_display = research.get("keywords", [])[:10]
    if kw_display:
        print(f"  🏷️  Keywords: {', '.join(kw_display)}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Title: {topic}")
    research_count = research.get("total_articles_found", 0)
    print(f"  Research sources: {research_count} articles")
    print(f"  Content length: {word_count} words")
    tag_str = ", ".join(keywords) if keywords else "auto-generated"
    print(f"  Tags: {tag_str}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
