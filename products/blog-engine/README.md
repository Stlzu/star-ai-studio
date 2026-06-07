# Automated SEO Blog Content Engine

**Product #1 of The $1M Hermes Roadmap**

An AI-powered blog content engine that researches topics from the web and generates SEO-optimized blog posts — all driven by Hermes Agent.

## What It Does

1. **Researches** any topic — searches the web, reads top-ranking articles, extracts key insights
2. **Generates** a complete, structured blog post with YAML frontmatter for SEO
3. **Publishes** as markdown — ready for any static site (Hugo, Jekyll, Ghost, WordPress)

## How to Use

### Option 1: Via Hermes execute_code (recommended)
```python
# In execute_code, set TOPIC and KEYWORDS, then run the workflow
# See blog_engine_workflow.py for the full script
```

### Option 2: Standalone CLI
```bash
python3 blog_engine.py --topic "Your Topic" --keywords "kw1, kw2" --output post.md
```

## Example Output

Try: `python3 blog_engine_workflow.py --topic "AI agents for business automation"`

Generates a 600-1200 word blog post with:
- SEO-optimized title and metadata
- 5-7 professionally structured sections
- Real web-sourced research and examples
- 10-15 target keywords extracted from competitor content
- Call-to-action and reading time estimate

## Business Model

**Target customers:** Marketing agencies, content teams, SaaS companies, freelance writers

**Pricing options:**
- One-off: $97 per report
- Monthly: $297/mo (up to 30 posts)
- Enterprise: Custom pricing

**Potential monthly revenue at 50 customers × $297 = $14,850/mo**

## Technical Architecture

```
blog_engine_workflow.py  →  Hermes web_search  →  research.json
                         →  Hermes web_extract →  article content
                         →  content generator  →  output .md file
```

Built with Python 3, uses Hermes Agent tools for web research and content generation.

## Files

| File | Description |
|------|-------------|
| `blog_engine_workflow.py` | Hermes-native version (runs in execute_code) |
| `blog_engine_hermes.py` | Universal version (hermes_tools or fallback) |
| `blog_engine.py` | Standalone Python version (requests-based) |
| `output/` | Generated blog posts and research data |
