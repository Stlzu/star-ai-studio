# Lead Enrichment Tool

**Product #2 of The $1M Hermes Roadmap**

Automatically enrich company lists with web-researched data — perfect for CRM imports, sales prospecting, and lead qualification.

## What It Does

Takes a list of company names → researches each one via web search → outputs enriched CSV/JSON ready for CRM import.

**Enriched fields:**
- Website URL
- Company description
- Industry classification (AI, Finance, Healthcare, etc.)
- LinkedIn company page
- Headquarters location *(when available)*
- Employee count *(when available)*
- Source URLs for reference

## How to Use

### Via Hermes execute_code
```python
from hermes_tools import web_search, web_extract

# Set your companies
COMPANIES = ["Company A", "Company B"]

# Run enrichment pipeline (see lead_enrichment.py)
```

### Standalone CLI
```bash
python3 lead_enrichment.py --names "Company1, Company2, Company3" --output enriched_leads.csv
python3 lead_enrichment.py --input companies.csv --output enriched.csv
```

## Business Value

| Metric | Manual | With This Tool |
|--------|--------|----------------|
| Time per company | 5-10 min | 5-10 seconds |
| Cost per company | $2-5 | $0.01 |
| 100 companies | 8-16 hours | 10-15 minutes |
| Accuracy | Human errors | Consistent |

## Business Model

**Target customers:** Sales teams, recruiters, B2B marketers, real estate agents

**Pricing:**
- Pay-per-use: $0.10 per enriched company
- Monthly subscription: $197/mo (up to 2,000 companies)
- Enterprise: $997/mo (unlimited)

**Revenue example:** 50 customers × $197 = $9,850/mo

## Files

| File | Description |
|------|-------------|
| `lead_enrichment.py` | Main enrichment pipeline (Hermes-powered) |
| `output/enriched_leads.csv` | Sample output CSV |
| `output/enriched_leads.json` | Sample output JSON |
