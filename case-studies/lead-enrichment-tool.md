# How I Built a Lead Enrichment Tool That Replaces an Entire Sales Researcher Role

## The Problem

Sales teams waste an enormous amount of time on manual prospect research. Before making a single call, SDRs spend up to **30% of their working hours** crawling websites, LinkedIn profiles, and Google searches to piece together basic company information.

| Role | Time Spent Researching | Annual Cost (Team of 5) |
|------|----------------------|------------------------|
| SDR | 12 hours / week | $75,000 lost productivity |
| Sales researcher | Full-time | $55,000 salary |
| Data entry clerk | 20 hours / week | $25,000 part-time |

For a team of 5 SDRs generating 200 leads per week, that's over **500 hours per month** of research work that could be automated.

## The Solution

A **Lead Enrichment Tool** that takes raw company names and automatically researches each one across the web — extracting website, description, industry, LinkedIn URL, location, company size, and more. The output is a clean, structured CSV ready for CRM import.

### Key Capabilities

- **Batch processing.** Paste up to 2,000 company names at once (CSV or comma-separated).
- **Multi-source enrichment.** Extracts data from websites, LinkedIn, Crunchbase, and search results.
- **CRM-ready output.** Generates a clean CSV with standardized columns for HubSpot, Salesforce, or any CRM.
- **5-second per company.** No more waiting — results in minutes, not days.

## Architecture

```
Raw Company Names (CSV or text list)
       │
       ▼
┌──────────────────────────┐
│  Web Search Agent         │  Finds company website,
│  (company discovery)      │  LinkedIn, Crunchbase
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Data Extraction Agent    │  Scrapes and structures:
│  (field extraction)       │  description, industry, size
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Data Enrichment Agent    │  Fills gaps, validates
│  (cross-reference)        │  accuracy, deduplicates
└──────────┬───────────────┘
           │
           ▼
   Clean CSV → CRM Import
```

## Demo Results

**Input companies:** Nous Research, Anthropic, Hugging Face

| Field | Nous Research | Anthropic | Hugging Face |
|-------|-------------|-----------|-------------|
| Website | nousresearch.com | anthropic.com | huggingface.co |
| LinkedIn | linkedin.com/company/nous-research | linkedin.com/company/anthropic | linkedin.com/company/hugging-face |
| Industry | AI Research | AI Safety & Research | ML / NLP Platform |
| Location | Los Angeles, CA | San Francisco, CA | New York, NY |
| Size (est.) | 10–50 | 200–500 | 200–500 |
| Description | Building frontier AI models… | Developing safe, beneficial AI… | Open-source ML community… |

**Processing time: 5 seconds per company.**
**Total for 2,000 companies: ~3 hours** — a job that would take a human researcher **over 400 hours**.

## Pricing Model

| Plan | Companies / Month | Price | Cost per Company |
|------|-------------------|-------|------------------|
| Starter | 500 | $97/mo | $0.19 |
| Growth | 2,000 | $197/mo | $0.10 |
| Scale | 10,000 | $597/mo | $0.06 |

### Revenue Projection

- **50 Growth customers:** $9,850 / month MRR
- **10x cheaper** than hiring a part-time sales researcher ($2,500+/mo)
- Setup time: 10 minutes — no API keys, no configuration

### ROI Calculator

| Manual research time | 12 hrs / week |
|----------------------|--------------|
| SDR hourly cost | $35 / hr |
| Monthly cost of manual research | $1,680 |
| Tool cost (Growth plan) | $197 / mo |
| **Monthly savings per SDR** | **$1,483** |
| Team of 5 SDRs | **$7,415 / mo saved** |

## Turn Your SDRs Into Closers Today

Stop paying your sales team to do data entry. The lead enrichment tool is live and taking new customers. Upload your list — we'll have enriched data in your CRM before your next stand-up.

**→ Reply to this message to start your free trial.**
