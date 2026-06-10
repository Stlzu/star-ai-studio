#!/usr/bin/env python3
"""
Automated SEO Blog Content Engine — AI Workflow
===================================================
Runs inside the AI execute_code environment for reliable web search.

Usage:
    python3 blog_engine_workflow.py --topic "Your Topic" [--keywords "kw1, kw2"]
"""

import argparse
import json
import re
import sys
import yaml
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─── AI tool integration ────────────────────────────────────────────────

def search(query: str, limit: int = 5) -> list[dict]:
    """Search using web_search tool (available in execute_code)."""
    try:
        from hermes_tools import web_search
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
    except ImportError:
        print("  [!] web_search not available", file=sys.stderr)
        return []


def extract(url: str) -> Optional[str]:
    """Extract article content using web_extract."""
    try:
        from hermes_tools import web_extract
        result = web_extract(urls=[url])
        results = result.get("results", [])
        if results and not results[0].get("error"):
            return results[0].get("content", "")
    except Exception as e:
        print(f"  [!] extract error: {e}", file=sys.stderr)
    return None


# ─── Output ──────────────────────────────────────────────────────────────────

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


# ─── Research ────────────────────────────────────────────────────────────────

def research_topic(topic: str, keywords=None) -> dict:
    """Full research pipeline using web tools."""
    print(f"\n  🔍 Researching: '{topic}'")

    queries = [topic]
    if keywords:
        queries.extend([f"{topic} {kw}" for kw in keywords[:3]])

    all_results = []
    seen_urls = set()
    for q in queries:
        print(f"    Searching: {q}")
        results = search(q, limit=5)
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)

    print(f"    Found {len(all_results)} unique articles")

    if not all_results:
        print("    No search results — using topic knowledge only.")
        return {
            "topic": topic,
            "articles": [],
            "keywords": keywords or [topic.lower()],
            "total_articles_found": 0,
        }

    articles = []
    for i, result in enumerate(all_results[:5]):
        title = result.get("title", "Untitled")[:60]
        url = result.get("url", "")
        print(f"    Reading {i+1}/{min(5, len(all_results))}: {title}...")
        content = extract(url) if url else None
        articles.append({
            "title": result.get("title", ""),
            "url": url,
            "snippet": result.get("snippet", ""),
            "content": content or "",
        })

    # Extract top keywords
    all_text = " ".join(a.get("content", "") or "" for a in articles)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
    word_freq = Counter(words)
    keywords_found = [
        w for w, c in word_freq.most_common(50)
        if w not in STOP_WORDS and len(w) > 3
    ][:20]

    return {
        "topic": topic,
        "articles": articles,
        "keywords": keywords_found,
        "total_articles_found": len(all_results),
    }


# ─── Content Generation ──────────────────────────────────────────────────────

def generate_post(topic: str, research: dict, keywords: list) -> str:
    """Generate the full blog post as markdown."""
    kw = keywords or research.get("keywords", [])[:10]
    t = topic.title()
    l = topic.lower()
    today = datetime.now().strftime("%Y-%m-%d")

    parts = []

    # Title
    title = f"{t}: The Complete Guide for 2025"
    parts.append(f"# {title}\n")

    # YAML frontmatter
    meta = {
        "title": title,
        "date": today,
        "description": f"A comprehensive guide to {l}.",
        "tags": [l] + [str(k).lower() for k in kw[:7]],
        "reading_time": "8 min",
    }
    parts.append("---")
    parts.append(yaml.dump(meta, default_flow_style=False).strip())
    parts.append("---\n")

    # Introduction
    parts.append("## Introduction\n")
    snippets = [a["snippet"] for a in research.get("articles", [])[:2] if a.get("snippet")]
    if snippets:
        parts.append(f"{snippets[0]}\n")
        if len(snippets) > 1:
            parts.append(f"> *{snippets[1]}*\n")

    parts.append(f"In this guide, we explore {l}, including:\n")
    sections = [
        ("background", f"What Is {t}?"),
        ("benefits", f"Top Benefits of {t}"),
        ("implementation", f"How to Get Started with {t}"),
        ("examples", "Real-World Examples"),
        ("future", f"The Future of {t}"),
    ]
    for _, title_text in sections:
        parts.append(f"- **{title_text}**\n")
    parts.append(f"By the end, you'll have a roadmap for {l}.\n")

    # Body sections
    section_content = {
        "background": [
            f"### What Is {t}?\n",
            f"{t} refers to the use of AI-powered software agents that automate and optimize business processes. These agents can perform tasks, make decisions, and interact with other systems without constant human supervision.\n",
            f"Key concepts include autonomous decision-making, workflow orchestration, and integration with existing business tools.\n",
        ],
        "benefits": [
            f"### Top Benefits of {t}\n",
            f"**1. Increased Efficiency** — AI agents handle repetitive tasks 24/7, freeing human workers for higher-value activities.\n",
            f"**2. Cost Reduction** — Automating workflows reduces operational costs by eliminating manual labor for routine processes.\n",
            f"**3. Scalability** — AI agents can handle thousands of concurrent tasks without additional headcount.\n",
            f"**4. Accuracy** — Reduce human error in data processing, reporting, and decision-making.\n",
        ],
        "implementation": [
            f"### How to Get Started with {t}\n",
            "**Step 1: Identify the right processes to automate.** Look for repetitive, rule-based tasks that consume significant employee time.\n",
            "**Step 2: Choose your AI agent platform.** Options include custom AI agent workflows, or specialized tools for specific use cases.\n",
            "**Step 3: Design and test your workflow.** Start with a single process, test thoroughly, then expand.\n",
            "**Step 4: Monitor and optimize.** Track performance metrics and iterate on your agent configurations.\n",
        ],
        "examples": [
            "### Real-World Examples\n",
            f"**Customer Support Automation** — Companies use AI agents to handle common support queries, route complex issues to humans, and maintain conversation history.\n",
            f"**Data Processing Pipelines** — AI agents extract, transform, and load data from multiple sources into analytics platforms automatically.\n",
            f"**Content Generation** — Marketing teams use AI agents to research, draft, and publish content at scale.\n",
        ],
        "future": [
            f"### The Future of {t}\n",
            f"The next 12-24 months will see AI agents become more autonomous, collaborative (multi-agent systems), and deeply integrated with existing business infrastructure. Early adopters will have a significant competitive advantage.\n",
        ],
    }

    for section_id, title_text in sections:
        parts.append(f"## {title_text}\n")
        parts.extend(section_content.get(section_id, [f"_[Content for {title_text}]_\n"]))
        parts.append("")

    # Conclusion
    parts.append("## Conclusion\n")
    parts.append(f"{t} is transforming how businesses operate. By implementing AI agents strategically, organizations can achieve significant efficiency gains, cost savings, and competitive advantages.\n")
    parts.append("**Key takeaways:**\n")
    parts.append(f"- {t} offers real, measurable benefits\n")
    parts.append("- Start small with one well-defined process\n")
    parts.append("- Measure results and iterate\n")
    parts.append("- The technology is evolving rapidly — start now\n")
    parts.append("\n---\n")
    parts.append(f"\n*Generated by the Automated SEO Content Engine*\n")

    return "".join(parts)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SEO Blog Content Engine (AI Workflow)")
    parser.add_argument("--topic", "-t", required=True, help="Blog topic")
    parser.add_argument("--keywords", "-k", help="Comma-separated keywords")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()
    topic = args.topic
    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else None

    print(f"\n{'='*60}")
    print(f"  📝 Automated SEO Blog Content Engine")
    print(f"  Topic: {topic}")
    print(f"{'='*60}")

    research = research_topic(topic, keywords)

    safe = re.sub(r"[^\w\s-]", "", topic).strip().replace(" ", "-")[:30]
    res_path = OUTPUT_DIR / f"research-{safe}.json"
    res_path.write_text(json.dumps(research, indent=2), encoding="utf-8")
    print(f"\n  📊 Research saved to: {res_path}")

    print(f"\n  ✍️  Generating blog post...")
    kws = keywords or research.get("keywords") or []
    content = generate_post(topic, research, kws)

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
    print(f"  Topic: {topic}")
    print(f"  Sources: {research['total_articles_found']} articles")
    print(f"  Words: {wc}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
