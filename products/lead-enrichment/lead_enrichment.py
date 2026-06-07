#!/usr/bin/env python3
"""
Lead Enrichment Tool — Hermes Workflow
=======================================
Enrich company lists with web-researched data for CRM import.

Usage (execute_code):
    # Set COMPANIES list, then run this script
    python3 lead_enrichment.py --input leads.csv --output enriched.csv
    # or paste company names directly:
    python3 lead_enrichment.py --names "Company A, Company B, Company C"
"""

import argparse
import csv
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


# Try Hermes tools
def search_company(name: str) -> list[dict]:
    """Search for company information using Hermes web_search."""
    try:
        from hermes_tools import web_search
        results = []
        # Search with specific queries for best results
        queries = [
            f"{name} company overview",
            f"{name} company about",
        ]
        for q in queries:
            result = web_search(query=q, limit=3)
            data = result.get("data", {})
            items = data.get("web", []) or data.get("results", [])
            for r in items:
                url = r.get("url", "")
                title = r.get("title", "")
                snippet = r.get("description", r.get("snippet", ""))
                results.append({"title": title, "url": url, "snippet": snippet})
            time.sleep(0.3)
        return results
    except ImportError:
        return []


def extract_info(url: str) -> Optional[str]:
    """Extract page content via Hermes web_extract."""
    try:
        from hermes_tools import web_extract
        result = web_extract(urls=[url])
        for r in result.get("results", []):
            if not r.get("error"):
                return r.get("content", "")[:2000]
    except:
        pass
    return None


def enrich_company(name: str) -> dict:
    """Enrich a single company name with web-researched data."""
    print(f"  🔍 Enriching: {name}")

    result = search_company(name)

    # Extract the best info from search results
    company_data = {
        "company_name": name,
        "website": "",
        "description": "",
        "industry": "",
        "headquarters": "",
        "estimated_size": "",
        "linkedin": "",
        "source_urls": [],
        "search_snippets": [],
    }

    if not result:
        print(f"    ⚠️  No results for {name}")
        return company_data

    # Track URLs and snippets
    for r in result:
        url = r.get("url", "")
        snippet = r.get("snippet", "")
        title = r.get("title", "")
        company_data["source_urls"].append(url)
        if snippet:
            company_data["search_snippets"].append(snippet)

        # Extract website from URL
        if not company_data["website"]:
            domain_match = re.search(r'https?://([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                # Skip search engine URLs and social media for primary website
                skip_domains = ['google.com', 'bing.com', 'duckduckgo.com', 'linkedin.com',
                               'facebook.com', 'twitter.com', 'youtube.com', 'wikipedia.org',
                               'crunchbase.com', 'bloomberg.com']
                if not any(sd in domain for sd in skip_domains):
                    company_data["website"] = f"https://{domain}"

        # Extract description from snippet
        if not company_data["description"] and snippet and len(snippet) > 50:
            company_data["description"] = snippet

        # Extract LinkedIn
        if "linkedin.com/company" in url and not company_data["linkedin"]:
            company_data["linkedin"] = url

        # Try to extract industry from snippet keywords
        if not company_data["industry"]:
            industry_keywords = {
                "tech": ["software", "technology", "saas", "cloud", "ai", "data", "digital", "tech"],
                "finance": ["finance", "banking", "insurance", "fintech", "investment"],
                "healthcare": ["healthcare", "health", "medical", "pharma", "biotech", "hospital"],
                "ecommerce": ["ecommerce", "retail", "shop", "store", "marketplace"],
                "consulting": ["consulting", "consultancy", "advisory", "professional services"],
                "manufacturing": ["manufacturing", "industrial", "factory", "production"],
                "marketing": ["marketing", "advertising", "media", "agency", "brand"],
                "education": ["education", "learning", "training", "school", "university"],
            }
            snippet_lower = (snippet or "").lower()
            for ind, keywords in industry_keywords.items():
                if any(kw in snippet_lower for kw in keywords):
                    if not company_data["industry"]:
                        company_data["industry"] = ind
                    else:
                        break  # Found one, good enough

        # Try to extract headquarters from snippet
        if not company_data["headquarters"]:
            location_patterns = [
                r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})',
                r'based\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'headquartered\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]
            for pat in location_patterns:
                match = re.search(pat, snippet or "")
                if match:
                    company_data["headquarters"] = match.group(1)
                    break

        # Try to extract employee count / size
        if not company_data["estimated_size"]:
            size_patterns = [
                r'(\d[\d,]*)\+?\s*employees',
                r'(\d[\d,]*)\s*-\s*(\d[\d,]*)\s*employees',
                r'(?:over|about|approximately|more than)\s+(\d[\d,]*)',
            ]
            for pat in size_patterns:
                match = re.search(pat, snippet or "", re.IGNORECASE)
                if match:
                    company_data["estimated_size"] = match.group(0)
                    break

    # Try to enrich further by extracting Wikipedia or Crunchbase content
    for r in result:
        url = r.get("url", "")
        if any(domain in url for domain in ["wikipedia.org", "crunchbase.com", "bloomberg.com"]):
            content = extract_info(url)
            if content:
                # Extract better description
                if not company_data["description"] or len(company_data["description"]) < len(content):
                    # Find first substantive paragraph
                    paragraphs = re.findall(r'([A-Z][^.]{50,200}\.)', content)
                    if paragraphs:
                        company_data["description"] = paragraphs[0]
                break

    company_data["enriched_at"] = datetime.now().isoformat()
    print(f"    ✅ Found: website={company_data.get('website','N/A')[:30]}, "
          f"industry={company_data.get('industry','N/A')}")
    return company_data


def parse_companies(input_source: str) -> list[str]:
    """Parse company names from a file or comma-separated string."""
    path = Path(input_source)
    if path.exists():
        # It's a file
        if path.suffix.lower() == '.csv':
            with open(path, 'r') as f:
                reader = csv.reader(f)
                return [row[0].strip() for row in reader if row and row[0].strip()]
        else:
            text = path.read_text()
            return [line.strip() for line in text.split('\n') if line.strip()]
    else:
        # Comma-separated names
        return [n.strip() for n in input_source.split(',') if n.strip()]


def save_enriched(companies: list[dict], output_path: str):
    """Save enriched data as CSV."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "company_name", "website", "description", "industry",
        "headquarters", "estimated_size", "linkedin", "enriched_at"
    ]

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(companies)

    # Also save as JSON for reference
    json_path = path.with_suffix('.json')
    json_path.write_text(json.dumps(companies, indent=2, default=str), encoding='utf-8')

    return path


def main():
    parser = argparse.ArgumentParser(description="Lead Enrichment Tool — enrich company lists with web data")
    parser.add_argument("--input", "-i", help="Input CSV file (first column = company names)")
    parser.add_argument("--names", "-n", help="Comma-separated company names")
    parser.add_argument("--output", "-o", default="enriched_leads.csv", help="Output CSV path")
    parser.add_argument("--headless", action="store_true", help="Minimal output (for automation)")

    args = parser.parse_args()

    if not args.input and not args.names:
        parser.print_help()
        print("\nError: Provide --input file or --names 'Company1, Company2'")
        sys.exit(1)

    source = args.input or args.names
    companies = parse_companies(source)

    print(f"\n{'='*60}")
    print(f"  🏢 Lead Enrichment Tool")
    print(f"  Companies to enrich: {len(companies)}")
    print(f"{'='*60}")

    results = []
    for i, name in enumerate(companies, 1):
        print(f"\n  [{i}/{len(companies)}]")
        enriched = enrich_company(name)
        results.append(enriched)
        # Rate-limit politeness
        if i < len(companies):
            time.sleep(0.5)

    # Save
    output_path = save_enriched(results, args.output)
    enriched_count = sum(1 for r in results if r.get("website") or r.get("description"))
    print(f"\n{'='*60}")
    print(f"  ✅ Enrichment Complete!")
    print(f"  📄 CSV saved: {output_path}")
    print(f"  📊 JSON saved: {Path(args.output).with_suffix('.json')}")
    print(f"  🎯 Companies enriched with data: {enriched_count}/{len(companies)}")
    print(f"{'='*60}")

    # Print sample
    if not args.headless and results:
        print(f"\n  Sample enriched record:")
        print(f"  {json.dumps(results[0], indent=2)}")


if __name__ == "__main__":
    main()
