# Agency Operations Pipeline — Star AI Studio

**Internal playbook:** Client intake → proposal → delivery → billing → post-delivery.

This document is the operational backbone for Star AI Studio. Every step from first contact to final invoice is documented here so any team member can run the pipeline without guesswork.

---

## 1. Client Intake Process

### 1.1 Lead Sources

| Source | Best For | Volume Target | Notes |
|--------|----------|---------------|-------|
| **Fiverr** | Warm product buyers (blog engine, invoice extractor, lead enrichment) | 5–10 inquiries/wk | Gig packages ($150–$2,500) act as lead gen. Upgrade to custom builds. |
| **Upwork** | Custom automation projects ($2k–$15k) | 3–5 proposals/wk | Target fixed-price projects. Avoid hourly. |
| **LinkedIn DM** | Agency owners, sales leaders, CPAs | 10–20 DMs/wk | Use the LinkedIn DM script in `sales-templates.md`. |
| **Cold email** | Local businesses, specific verticals | 10–20 emails/day | Sequences from `outreach-email-campaign.md`. Send Tue–Thu, 7:30–9:00 AM. |
| **Referrals** | Existing clients, network | Build over time | Ask after every delivered project (see Section 6.3). |

**Priority order for outreach:** Referrals > warm LinkedIn intros > cold email > Fiverr/Upwork replies.

### 1.2 Intake Form Questions

Send these questions (email, Calendly booking page, or intake form) *before* the discovery call:

1. **What's your name and role?** (Confirm decision-maker status.)
2. **What business/industry are you in?**
3. **Describe the task or process you want automated.** (Be specific — what goes in, what comes out?)
4. **How much time does this take per week/month?** (Quantify the pain.)
5. **What's your budget range for this project?** (If they say "I don't know," ask what they'd pay to make the problem go away.)
6. **What's your ideal timeline?** (Urgency signal — next week vs. "someday.")
7. **Have you tried solving this before?** (If yes, what didn't work?)
8. **Who else would be involved in the decision?** (Identify stakeholders.)

### 1.3 Discovery Call Script (30 Minutes)

Book a 15–30 min video or phone call after intake form is received.

**Opening (2 min)**
> "Thanks for jumping on. Quick intro — I build custom AI tools that automate repetitive business processes. My clients typically save 80%+ on time and costs. To see if I can help you, I'd love to hear about what's taking up the most time in your day-to-day."

**8 Qualification Questions (15 min)**

1. *"Walk me through the task you described in the form — what's the step-by-step process today?"*
   - Forces them to articulate the workflow. Listen for manual steps, data transfers, and decision points.

2. *"How many times do you do this per week/month?"*
   - Volume = revenue potential. 500 invoices/month vs. 10 changes the solution scope.

3. *"What happens if this doesn't get done — or gets done wrong?"*
   - Uncover the real pain. A 5% error rate on $500k invoices is different from a blog typo.

4. *"Who's currently doing this work, and what would they do with the freed-up time?"*
   - Identifies whether this replaces a role or augments one. Affects pricing.

5. *"Have you tried any software or tool for this before? What happened?"*
   - Reveals past failures, budget already spent, and what NOT to do.

6. *"If I could automate this in [3–7 days], what would that be worth to you in dollar terms?"*
   - Direct budget question framed as value, not cost.

7. *"Are there any related processes that should be automated alongside this?"*
   - Upsell path. Invoice extraction often leads to PO matching or reconciliation automation.

8. *"What does 'done' look like for this project — what would make you say it was a success?"*
   - Defines acceptance criteria. Write these down — they become the QA checklist.

**Demo/Pitch (10 min)**
> "Based on what you've shared, here's what I'd build for you..."

Adapt the demo to their vertical. Reference existing products:
- **Content/marketing pain** → Show SEO Blog Engine output (case study: `case-studies/seo-blog-engine.md`)
- **Sales/research pain** → Show Lead Enrichment Tool output (case study: `case-studies/lead-enrichment-tool.md`)
- **Invoice/accounting pain** → Show Invoice Extractor output (case study: `case-studies/invoice-extractor.md`)
- **Custom/unclear** → Show any relevant product output as proof of capability

**Close (3 min)**
> "Does this sound like it'd solve your problem? Great — I'll send you a simple proposal by tomorrow. If it looks good, I can start building [next week / as soon as we get the first payment]."

### 1.4 Qualification Criteria

A lead is **qualified** when all four conditions are met:

| Criteria | Why | Green Flag | Red Flag |
|----------|-----|------------|----------|
| **Budget $2k+** | Projects under $2k don't justify the intake/proposal effort. | They answer the budget question or say "$2k–$5k." | "I was hoping for something free/cheap." |
| **Clear pain point** | Vague problems lead to scope creep. | They can describe the task, volume, and pain clearly. | "I just want AI." Need to dig or pass. |
| **Decision-maker** | You can't sell to someone who needs permission. | They are the owner, partner, or have budget authority. | "I'll need to check with my partner/manager." |
| **Reasonable timeline** | "Need it yesterday" = bad fit. "Next quarter" = cold. | 1–4 weeks is ideal. Immediate = they'll pay premium. | "Maybe next year" or "I need it today for free." |

If any red flag appears during the intake form or first 5 minutes of the discovery call, **do not proceed to proposal**. Instead:
- Offer a free consultation (5-min assessment of their biggest time sink) to build relationship
- Send them to a relevant case study
- Move to nurture sequence (check back in 30–60 days)

### 1.5 CRM Tracking

We use a lightweight file-based CRM — no paid tools required.

**File:** `content/crm.csv` (create it on first lead)

Columns:
```
date_added,name,company,email,source,vertical,budget_range,timeline,status,notes,next_action
```

**Status values:**
- `lead` — Initial contact, not yet qualified
- `qualified` — Passed qualification criteria
- `proposal_sent` — Proposal delivered
- `negotiating` — Price/timeline discussion
- `won` — Paid, project started
- `lost` — Closed lost (log reason)
- `nurture` — Good lead but wrong timing

**Weekly review:** Check CRM every Monday. Follow up on stale leads (>7 days without action). Close lost leads or move to nurture.

---

## 2. Proposal Template

Send within 24 hours of the discovery call. Keep it to one page (or equivalent).

```
## Proposal for [Client Name]
**Prepared by:** Star AI Studio
**Date:** [Date]
**Status:** Draft for review

---

### 1. Problem Statement
[Client] spends [X hours per week/month] manually doing [specific task].
This costs [Y dollars in time] and results in [Z error rate / bottleneck / missed opportunity].
The current process: [brief 1-2 line description of manual workflow.]

### 2. Solution Overview
We will build a custom [AI-powered automation tool name] that:
- [Capability 1 — what the tool does]
- [Capability 2 — benefit in time/accuracy]
- [Capability 3 — output format or integration]

This is NOT a generic chatbot or SaaS subscription. It's a purpose-built tool
for [Client's] exact workflow, developed using our proven agent-based automation
methodology (same approach used for our [Blog Engine / Lead Enrichment / Invoice Extractor] products).

### 3. Deliverables
- ✅ Working automation tool (source code owned by client)
- ✅ [Volume] units processed — e.g., 500 invoices, 2,000 leads, 30 blog posts
- ✅ Structured output — CSV / JSON / direct API integration
- ✅ User documentation (how to run, what to expect)
- ✅ [X] days of post-delivery support

### 4. Timeline
| Phase | Duration | Details |
|-------|----------|---------|
| Discovery & Planning | 1 day | Clarify requirements, gather sample data |
| Build | [2–5] days | Development with parallel automated agents |
| Testing & QA | 1 day | Validate against real data, fix edge cases |
| Client Review | 1 day | You test, we iterate |
| Handover | 1 day | Documentation, walkthrough, support setup |
| **Total** | **[X] days** | From kickoff to handover |

### 5. Pricing

**Option A — Setup + Monthly (Recommended)**
| Item | Amount |
|------|--------|
| Setup fee (one-time) | $[2,500–5,000] |
| Monthly maintenance & hosting | $[300–1,000]/mo |
| **Total first month** | **$[2,800–6,000]** |

**Option B — One-Time Build**
| Item | Amount |
|------|--------|
| Full project (includes [X] days support) | $[3,000–8,000] |
| Ongoing support (optional) | $[300–500]/mo |

**Payment terms:** 50% upfront, 50% on delivery. No contracts — cancel anytime.

### 6. What We Need From You
To start, please provide:
- [Specific data samples — e.g., 5–10 sample invoices]
- [Access to relevant systems or accounts, if applicable]
- [Brief walkthrough of current process — recorded Loom or written steps]
- [Point of contact for questions during build]

### 7. Next Steps
1. Review this proposal
2. Reply with questions or acceptance
3. I send payment link for 50% deposit
4. We schedule a 30-min kickoff call
5. I start building

**This proposal is valid for 14 days.**
```

Save to `content/proposals/` as `[client-name]-proposal.md`.

---

## 3. Client Onboarding

### 3.1 Welcome Email Template

Send immediately after deposit is received.

```
Subject: Welcome to Star AI Studio — let's build your [tool name]

Hi [Name],

Thanks for the deposit — you're officially locked in. Here's what happens next:

**Step 1: Kickoff Call**
We'll schedule 30 minutes this week to review the plan, go over sample data,
and set expectations. Pick a time: [Calendly link]

**Step 2: What I Need From You**
Before the build starts, please send:
1. [Sample data requirement — e.g., 10 sample invoices, 50 company names]
2. [Access/credentials if needed]
3. [Any specific formatting preferences]

**Step 3: Daily Updates**
During the build (estimated [X] days), I'll send a brief daily update
covering what was done, what's next, and anything I need from you.

**Step 4: Review & Launch**
When the tool is ready, I'll share the output and walk you through how to use it.
You'll have [X] days to test and request changes.

Quick link to pay remaining 50% on delivery: [Stripe/PayPal payment link]

Questions before we start? Hit reply.

Best,
[Your Name]
Star AI Studio
```

### 3.2 Information Gathering Checklist

Tick these before the build phase begins:

- [ ] Sample input data received (5–10 real examples minimum)
- [ ] Desired output format confirmed (CSV, JSON, API, etc.)
- [ ] Edge cases identified (dates, empty fields, different formats)
- [ ] Integration requirements scoped (CRM, accounting software, CMS)
- [ ] Deployment preference confirmed (local machine, cloud, or both)
- [ ] Communication channel agreed (email, Slack, Telegram)
- [ ] NDA signed (if requested — use free template: https://www.rocketlawyer.com/business-and-contracts/business-operations/nda-and-confidentiality)

### 3.3 NDA Template

We don't require NDA by default — most clients don't request it. If they do, use a standard mutual NDA from RocketLawyer or similar service:

> **Recommended free NDA template:** https://www.hellobonsai.com/templates/nda
> **Alternative:** https://www.rocketlawyer.com/business-and-contracts/business-operations/nda-and-confidentiality

Fill in parties, effective date, and scope. Both parties sign. Store in `clients/[client-name]/nda.pdf`.

### 3.4 Project Kickoff Checklist

Use this during the 30-min kickoff call:

- [ ] Confirm project scope and deliverables (reference proposal)
- [ ] Review sample data together (confirm it's representative)
- [ ] Set daily update time and channel
- [ ] Establish how feedback will be submitted (inline comments, Loom video, email)
- [ ] Set review window length (typically 3 business days for client review phase)
- [ ] Confirm payment link works for final 50%
- [ ] Set handover date expectation

### 3.5 Communication Schedule

| Phase | Frequency | Format | Content |
|-------|-----------|--------|---------|
| **Build** | Daily (EOD) | Email or message | What was built, what's next, blockers |
| **Test & QA** | Per iteration | Message or Loom | Results, accuracy metrics, asks for review |
| **Client Review** | Per feedback round | Depends on client | Updated output, change log |
| **Post-delivery** | Weekly (monthly clients) | Email | Uptime, usage stats, opportunities |

Keep all communication documented in the client's folder: `clients/[client-name]/`.

---

## 4. Delivery Process

### 4.1 Phase 1: Research & Plan (Day 1)

**Goal:** Understand the data, design the automation pipeline.

Steps:
1. Review sample data — identify format, variations, edge cases.
2. Design the agent pipeline (input → processing → output stages).
3. Identify which of our 3 existing products (if any) provide reusable components:
   - **Blog Engine agents** → reuse for any content generation task
   - **Lead Enrichment agents** → reuse for any web research/parsing task
   - **Invoice Extractor agents** → reuse for any document/data extraction task
4. Document the plan in `clients/[client-name]/build-plan.md`.
5. Send plan to client for confirmation before coding.

### 4.2 Phase 2: Build with Parallel Subagents (Days 2–6)

**Goal:** Build the automation using parallel agent pipelines for speed.

Architecture pattern (adapt from our existing products):

```
Client Input Data
       │
       ▼
┌─────────────────────┐
│  Input Agent         │  Validate, parse, standardize input
│  (data prep)         │  (Reuse: Blog Engine data prep)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Processing Agent(s) │  Run 2–5 parallel subagents depending on task:
│  (core logic)        │  - Extraction agent (reuse: Invoice Extractor)
│                      │  - Research agent (reuse: Lead Enrichment)
│                      │  - Generation agent (reuse: Blog Engine)
│                      │  - Validation agent
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Output Agent        │  Format, structure, export
│  (data delivery)     │  CSV / JSON / API / File
└─────────────────────┘
```

**Development principles:**
- Each subagent is an independent module — testable in isolation.
- Run agents in parallel where possible to reduce total build time.
- Use our existing products as starting points; modify for client-specific needs.
- Log all processing steps for debugging and client transparency.

**Daily deliverable for client:** Brief status update with a real output sample if possible.

### 4.3 Phase 3: Test & QA (1 Day)

**Goal:** Validate against real data, catch edge cases.

QA checklist:
- [ ] Process the client's sample data — all records processed without errors
- [ ] Spot-check [10] random outputs for accuracy
- [ ] Test edge cases: empty fields, unusual formatting, missing data
- [ ] Test performance: [volume] records in `< [expected]` time
- [ ] Verify output format matches specification (columns, data types, encoding)
- [ ] Run a full batch end-to-end without manual intervention

**Acceptance criteria:** Meet the client's "done" definition from the discovery call (Section 1.3, Q8).

If accuracy < 90% on spot checks, iterate on the processing agent before going to client.

### 4.4 Phase 4: Client Review & Iterate (1–3 Days)

**Goal:** Client validates the tool against their real-world needs.

Process:
1. Share output (sample and/or full batch) with the client.
2. Client reviews within agreed window (typically 3 business days).
3. Client provides feedback — categorized as:
   - **Bug:** Tool produced incorrect output → fix immediately (within 24 hrs)
   - **Enhancement:** Additional capability not in original scope → evaluate for scope change or future iteration
   - **Preference:** Formatting, labeling, output order → address within 2 hrs
4. Maximum 2 feedback rounds included. Additional rounds billed at $150/hr.

### 4.5 Phase 5: Handover & Documentation (Day 7+)

**Goal:** Client can run and maintain the tool independently.

Deliverables to hand over:
- [ ] Working tool (source code, executable, or both per agreement)
- [ ] User documentation (`clients/[client-name]/handoff-documentation.md`)
- [ ] Sample input/output for reference
- [ ] Loom walkthrough recording (5–10 min, screen share)
- [ ] Support agreement details (response times, channels, SLA)

### 4.6 Handoff Documentation Template

Create `clients/[client-name]/handoff-documentation.md`:

```
# [Tool Name] — User Guide
**Client:** [Client Name]
**Delivered:** [Date]
**Version:** 1.0

---

## What This Tool Does
[1–2 sentence summary]

## How to Use

### Step 1: Prepare Your Input
- Format: [CSV / PDF / text / etc.]
- Required columns/fields: [list]
- Place files in: [path or upload location]

### Step 2: Run the Tool
[Command or UI instructions]
```
[Example command]
```

### Step 3: Get Your Output
- Output location: [path]
- Format: [CSV / JSON / etc.]
- What each column/field means: [table]

## Expected Performance
- [Volume] records processed in ~[time]
- Accuracy: ~[X]% on standard inputs

## Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| [Issue] | [Cause] | [Fix] |

## Support
- Response time: [24 hrs / 4 hrs urgent]
- Contact: [email/channel]
- Escalation: [contact]

## Change Log
| Date | Change | Author |
|------|--------|--------|
| [Date] | Initial delivery | [Name] |
```

---

## 5. Billing & Invoicing

### 5.1 Payment Terms

| Payment | Amount | Timing | Method |
|---------|--------|--------|--------|
| **Deposit** | 50% of total | Before build starts | Stripe / PayPal link |
| **Final** | 50% of total | On delivery, before handover | Stripe / PayPal link |
| **Monthly** | Agreed monthly rate | 1st of each month, post-delivery | Recurring Stripe / manual invoice |

Exception: For clients under $1,000 total, collect 100% upfront.

### 5.2 Invoice Template

Send invoices as PDF or markdown converted to PDF. Store in `clients/[client-name]/invoices/`.

```
# INVOICE
**Star AI Studio**

**Invoice #:** INV-[YYYY]-[XXX]  (e.g., INV-2025-001)
**Date:** [Date]
**Due Date:** [Date + 7 days]

**Bill To:**
[Client Name]
[Client Company]

**Description:**
[Project Name] — [Brief description of deliverable]

| Item | Amount |
|------|--------|
| Setup Fee (50% deposit) | $[Amount] |
| **Total Due** | **$[Amount]** |

**Payment Methods:**
- Stripe: [payment link]
- PayPal: [payment link]
- Bank Transfer: [details on request]

**Terms:** Due within 7 days. Late payments subject to [interest/fee policy].

Thank you for your business!
```

### 5.3 Recurring Billing Setup (Monthly Retainer)

For monthly clients:

1. **Stripe:** Create a Subscription product with the agreed monthly amount. Send the customer a payment link that sets up auto-pay.
2. **PayPal:** Create a PayPal Subscription button or send an invoice with "Make this recurring" enabled.
3. **Manual (fallback):** Send a manual invoice on the 1st of each month via email with a payment link.

**Billing reminder schedule for monthly clients:**
- 3 days before due date: automated reminder
- On due date: invoice sent
- 7 days overdue: gentle reminder with payment link
- 14 days overdue: service pause notice
- 30 days overdue: service suspended, collections if > $2k

### 5.4 Late Payment Policy

```
**Late Payment Policy — Star AI Studio**

- **7 days past due:** Reminder sent. No service interruption.
- **14 days past due:** Service partially restricted (no new builds, no modifications).
- **21 days past due:** Full service suspension. Client notified in writing.
- **30+ days past due:** Service terminated. Outstanding balance sent to collections
  (for amounts over $2,000). Past-due clients must pay in full + a $50 late fee
  before reactivation.

We understand things happen — if you need an extension, just ask before the due date.
```

### 5.5 Stripe/PayPal Payment Links

Payment link format for invoices:

- **Stripe Payment Link:** `https://buy.stripe.com/[custom-link-id]`
- **PayPal Payment Link:** `https://paypal.me/[username]/[amount]`

For recurring monthly billing:
- **Stripe Subscription Link:** `https://buy.stripe.com/[subscription-link-id]`
- **PayPal Subscription:** Create at https://www.paypal.com/webapps/mpp/subscriptions

**Naming convention for payment links:**
- One-time deposit: `stariai-[clientname]-deposit`
- One-time final: `stariai-[clientname]-final`
- Monthly retainer: `stariai-[clientname]-retainer`

---

## 6. Post-Delivery

### 6.1 Support SLA

| Tier | Response Time | Hours | Channel | Included In |
|------|---------------|-------|---------|-------------|
| **Standard** (one-time builds) | 24 hrs | Mon–Fri, 9–5 | Email | 7 days post-handover |
| **Monthly Retainer** | 24 hrs | Mon–Fri, 9–5 | Email + priority channel | Ongoing |
| **Premium Retainer** ($1k+/mo) | 4 hrs | 24/7 | Slack/Discord + email | Ongoing |

**What's covered:**
- Bug fixes in delivered tool
- Data processing failures
- Usage questions
- Integration issues (client-side)

**What's not covered (separate scope):**
- New features or capabilities
- Volume scaling beyond agreed limits
- Integration with new third-party tools
- Training new team members beyond initial walkthrough

**Escalation path:** If no response within SLA time + 2 hours, escalate to phone/text: [your number].

### 6.2 Case Study Creation Process

After each successful delivery, create a case study. This is our primary marketing asset.

**Step 1 — Interview (15 min call or async questions)**

Send these questions to the client:
1. "What was the problem you were trying to solve?"
2. "What was life like before the automation? (Time spent, frustration, cost)"
3. "How did you hear about us?"
4. "What was the implementation process like?"
5. "What are the measurable results? (Hours saved, cost reduced, errors eliminated)"
6. "What would you say to someone considering a similar solution?"
7. "Can we attribute a quote to you? (Name, title, company)"

**Step 2 — Draft**

Use the case study template in Section 7. Keep it to 300–500 words.
Include specific numbers (hours saved, % improvement, $ cost).

**Step 3 — Client Approval**

Send the draft to the client with:
> "Here's the case study draft based on our conversation. Please confirm:
> 1. All facts and numbers are accurate
> 2. You're comfortable with the quote attribution
> 3. Any edits or redactions needed
>
> Happy to adjust anything. Thanks for helping us showcase your results!"

**Step 4 — Publish**

Once approved:
- Save to `case-studies/[client-name].md`
- Add to website landing page
- Post on LinkedIn (tag client if they're comfortable)
- Add to proposal template as reference

**Target:** 1 case study per delivered project (aim for 80%+ opt-in rate).

### 6.3 Referral Request Template

Send 1 week after handover (after they've used the tool successfully).

```
Subject: Quick question about [tool name] + a referral ask

Hi [Name],

Now that you've had [tool name] running for a week — how's it going?
Anything I can adjust or improve?

If you're happy with the result, I have a small ask:
Do you know anyone else who might benefit from the same kind of automation?
I'm currently offering a referral fee of [15% of first project / $500]
for any introduction that turns into a client.

No pressure either way — just wanted to check in and make sure everything's working.

Best,
[Your Name]
```

**Referral incentive structure:**
- **Flat fee per referral:** $500 paid after referred client pays their first invoice
- **Percentage:** 15% of the referred client's first project fee
- **Discount:** Offer the referring client 1 month free on their monthly retainer

### 6.4 Upsell/Cross-Sell Opportunities

After delivery, look for natural expansion paths:

| Current Product | Upsell Opportunity | Cross-Sell Opportunity |
|----------------|--------------------|------------------------|
| **Invoice Extractor** | PO matching, reconciliation automation, AP workflow | Lead enrichment for vendor management |
| **Lead Enrichment** | CRM integration, automated outreach, scoring pipeline | Blog engine for sales content |
| **Blog Engine** | Content calendar automation, social repurposing, analytics | Lead enrichment for content promotion contacts |
| **Custom tool (any)** | Add monthly analytics/reporting dashboard | Add another workflow automation in same business |

**Timing:** Wait 2–4 weeks after handover before suggesting upsells. Let the client feel the value first.

**The ask:**
> "Now that [tool] is running smoothly, I noticed [Client] also does [related process]. Would it be helpful if I built something similar for that? I can typically do it faster since we already have the infrastructure."

---

## 7. Case Study Creation Workflow

### 7.1 Case Study Template

Save as `case-studies/[client-name]-case-study.md`.

```
# How [Client Name] Saved [X Hours/Month] Using [Tool Name]

**Industry:** [Industry]
**Tool:** [Tool Name]
**Timeline:** [Build time]
**Results:** [Key metric — e.g., 90% faster, $XXk saved]

---

## The Problem

[Client] was spending [X hours/month] on [specific task].
[Describe the pain — manual work, errors, bottleneck, cost.]

> "[Client quote about the problem before]"

## The Solution

We built a custom [tool type] that [key capability].
[2–3 sentences on how it works, what it automates.]

**Key features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

## The Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| [Metric 1] | [Before value] | [After value] | [X]% |
| [Metric 2] | [Before value] | [After value] | [X]% |

> "[Client testimonial quote]"

**Bottom line:** [Summary of impact — dollars saved, time regained, errors eliminated.]

[Optional screenshot or diagram of the tool output]
```

### 7.2 Screenshot/Recording Process

For every delivered project, document visually:

1. **Before screenshot** — What the manual process looks like (spreadsheet, inbox, PDF stack)
2. **Tool input screenshot** — Shows the input format
3. **Tool output screenshot** — Shows the structured result (CSV, JSON, formatted report)
4. **Loom recording** (optional but powerful) — 2–3 min screen recording:
   - Show the input → run the tool → show the output
   - Narrate: "This used to take [X] hours. Now it takes [X] seconds."

**Storage:** Save screenshots to `case-studies/assets/[client-name]/`.

### 7.3 Approval Workflow

```
Draft written → Client reviews → Edits applied → Client approves → Published

Approval checklist:
□ Client confirms facts and numbers are accurate
□ Client approves quoted statements (or provides edits)
□ Client confirms they're comfortable with their name/company attribution
□ No confidential data exposed in screenshots or descriptions
```

**If client declines case study:**
- Ask if they'll provide a private testimonial (not published) for use in proposals
- Create a generic/anonymized version: "An accounting firm processing 500 invoices/month..."
- File for future reference — they may agree later after more time with the tool

---

## Quick Reference: Our 3 Products

These products form the foundation of our delivery capability. Every custom build reuses components from one or more of them.

| Product | What It Does | Reusable Components | Case Study |
|---------|-------------|---------------------|------------|
| **SEO Blog Engine** | Researches topics, generates SEO-optimized blog posts in 2 min | Web search agent, content analyzer, blog writer agent, SEO template engine | [`case-studies/seo-blog-engine.md`](../case-studies/seo-blog-engine.md) |
| **Lead Enrichment Tool** | Enriches company names with researched data (website, LinkedIn, industry, size) | Web search agent, data extraction agent, data enrichment agent, CSV output formatter | [`case-studies/lead-enrichment-tool.md`](../case-studies/lead-enrichment-tool.md) |
| **Invoice Extractor** | Extracts structured data from invoice PDFs with 95%+ accuracy | Document parser agent, field extraction agent, line item agent, validation agent | [`case-studies/invoice-extractor.md`](../case-studies/invoice-extractor.md) |

**Source docs:** `products/blog-engine/`, `products/lead-enrichment/`, `products/invoice-extractor/`

---

## Appendix: Directory Structure

```
hermes-million/
├── content/
│   ├── agency-pipeline.md           ← This document
│   ├── sales-templates.md           ← Pitch scripts, pricing, objection handling
│   ├── outreach-email-campaign.md   ← Cold email sequences by vertical
│   ├── fiverr-gig-content.md        ← Fiverr gig descriptions
│   ├── upwork-profile.md            ← Upwork profile content
│   ├── linkedin-strategy.md         ← LinkedIn outreach strategy
│   ├── twitter-threads.md           ← Promotional Twitter thread content
│   ├── posting-schedule.md          ← Content calendar
│   ├── landing.html                 ← Website landing page
│   ├── serve_landing.py             ← Landing page server
│   ├── crm.csv                      ← Lead tracking
│   └── proposals/                   ← Client proposals (one per client)
├── case-studies/
│   ├── phase-0-builds.md            ← Summary index
│   ├── seo-blog-engine.md           ← Blog engine case study
│   ├── lead-enrichment-tool.md      ← Lead enrichment case study
│   ├── invoice-extractor.md         ← Invoice extractor case study
│   └── assets/                      ← Screenshots, diagrams
├── products/
│   ├── blog-engine/                 ← Product #1
│   ├── lead-enrichment/             ← Product #2
│   └── invoice-extractor/           ← Product #3
└── clients/                         ← Per-client folders (create as needed)
    └── [client-name]/
        ├── intake-form.md
        ├── build-plan.md
        ├── handoff-documentation.md
        ├── nda.pdf
        └── invoices/
```

---

*Last updated: June 2025*
*Maintainer: Star AI Studio Ops*
