#!/usr/bin/env python3
"""
Invoice/Receipt Data Extractor — AI-Powered Workflow
==================================================
Extract structured data from invoices and receipts automatically.

Usage:
    python3 invoice_extractor.py --input invoice.pdf --output data.csv
    python3 invoice_extractor.py --text "INVOICE #123..." --output data.json
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─── PDF Text Extraction ────────────────────────────────────────────────────


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF using pdftotext."""
    cmd = ["pdftotext", "-layout", pdf_path, "-"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"  [!] pdftotext error: {result.stderr}", file=sys.stderr)
            return ""
    except FileNotFoundError:
        print("  [!] pdftotext not found. Install poppler-utils.", file=sys.stderr)
        return ""
    except subprocess.TimeoutExpired:
        print("  [!] pdftotext timed out", file=sys.stderr)
        return ""


# ─── Invoice Parsing ────────────────────────────────────────────────────────


def parse_invoice(text: str) -> dict:
    """Parse invoice text into structured data using regex patterns."""
    data = {
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "vendor_name": "",
        "vendor_address": "",
        "vendor_email": "",
        "vendor_phone": "",
        "customer_name": "",
        "customer_address": "",
        "subtotal": "",
        "tax": "",
        "total": "",
        "currency": "USD",
        "line_items": [],
        "notes": "",
        "raw_text_length": len(text),
    }

    if not text.strip():
        return data

    lines = text.split("\n")
    text_block = text.strip()

    # ── Invoice Number ──
    patterns = [
        r'(?:invoice\s*number|inv\s*#|inv\s*number)[:.]?\s*([A-Z0-9][-A-Z0-9/]{3,30})',
        r'(?:number)\s*[:#]?\s*([A-Z0-9][-A-Z0-9/]{3,30})',
        r'#\s*([A-Z0-9][-A-Z0-9]{3,20})\s',
        r'(INV-\d+)',
    ]
    for pat in patterns:
        m = re.search(pat, text_block, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            # Filter out false positives — reject if the entire match is just a label word
            label_words = {'invoice', 'number', 'date'}
            if val.lower() not in label_words and len(val) > 2:
                data["invoice_number"] = val
                break

    # ── Dates ──
    date_pats = [
        r'(?:date|invoice\s*date)[:.\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:date|invoice\s*date)[:.\s]*(\w+\s+\d{1,2},?\s*\d{4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        r'(\d{4}-\d{2}-\d{2})',
    ]
    for pat in date_pats:
        m = re.search(pat, text_block, re.IGNORECASE)
        if m:
            data["invoice_date"] = m.group(1).strip()
            break

    due_pats = [
        r'(?:due\s*date|payment\s*due)[:.\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:due\s*date)[:.\s]*(\w+\s+\d{1,2},?\s*\d{4})',
        r'(?:Due\s*Date)\s*:\s*(\d{4}-\d{2}-\d{2})',
        r'(?:Due\s*Date)\s*:\s*(\d{2}/\d{2}/\d{4})',
    ]
    for pat in due_pats:
        m = re.search(pat, text_block, re.IGNORECASE)
        if m:
            data["due_date"] = m.group(1).strip()
            break

    # ── Total ──
    total_pats = [
        r'(?:total\s*due|amount\s*due|balance\s*due)[:.\s]*\$?([0-9,]+\.?\d{0,2})',
        r'(?:^|\n)\s*TOTAL\s*[:.\s]*\$?\s*([0-9,]+\.\d{2})',
        r'(?:^|\n)\s*Total\s*[:.\s]*\$?\s*([0-9,]+\.\d{2})',
    ]
    for pat in total_pats:
        m = re.search(pat, text_block, re.IGNORECASE | re.MULTILINE)
        if m:
            data["total"] = m.group(1).strip().replace(",", "")
            break
    # Fallback: find the last price-looking number that's not "subtotal"
    if not data["total"]:
        amounts = re.findall(r'\$?([0-9,]+\.\d{2})', text_block)
        if amounts:
            data["total"] = amounts[-1].replace(",", "")

    # ── Subtotal & Tax ──
    sub_pats = [r'(?:subtotal)[:.\s]*\$?([0-9,]+\.?\d{0,2})']
    for pat in sub_pats:
        m = re.search(pat, text_block, re.IGNORECASE)
        if m:
            data["subtotal"] = m.group(1).strip()
            break

    tax_pats = [
        r'(?:tax|vat|hst|gst)[:.\s]*\$?([0-9,]+\.?\d{0,2})',
        r'tax\s*[(]\s*([\d.]+%)',
        r'(?:Tax|TAX)\s*[(][^)]*[)][:.\s]*\$?([0-9,]+\.\d{2})',
    ]
    for pat in tax_pats:
        m = re.search(pat, text_block, re.IGNORECASE)
        if m:
            data["tax"] = m.group(1).strip()
            break

    # ── Currency ──
    if "€" in text_block:
        data["currency"] = "EUR"
    elif "£" in text_block:
        data["currency"] = "GBP"
    elif "¥" in text_block:
        data["currency"] = "JPY"

    # ── Vendor Name ──
    # Usually on a "From:" line or the first company-looking line
    vendor_found = False
    for i, line in enumerate(lines):
        bl = line.strip().lower()
        if bl.startswith("from:") or bl.startswith("from :"):
            data["vendor_name"] = lines[i + 1].strip() if i + 1 < len(lines) else ""
            vendor_found = True
            break
    
    if not data.get("vendor_name"):
        # Try: first line that looks like a company (has title case, 2-8 words)
        lines_clean = [l.strip() for l in lines if l.strip()]
        skip_headers = {"invoice", "receipt", "bill", "statement", "page", "date",
                        "number", "from:", "to:", "bill to:", "ship to:"}
        for line in lines_clean[:8]:
            words = line.split()
            if (2 <= len(words) <= 10 and
                not any(h in line.lower() for h in skip_headers) and
                not re.match(r'^[\d\s/\-,:#()$€£¥.]+$', line) and
                line[0].isupper()):
                data["vendor_name"] = line
                break

    # ── Vendor Email ──
    email_match = re.search(r'([\w.+-]+@[\w-]+\.[\w.]+)', text_block)
    if email_match:
        data["vendor_email"] = email_match.group(1)

    # ── Vendor Phone ──
    phone_match = re.search(r'(\+?1?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', text_block)
    if phone_match:
        data["vendor_phone"] = phone_match.group(1).strip()

    # ── Line Items ──
    # Look for tabular data with descriptions and amounts
    for i, line in enumerate(lines):
        line = line.strip()
        # Match lines that look like line items: description + amount
        item_match = re.match(
            r'(.+?)\s{2,}\$?([0-9,]+\.?\d{0,2})\s*$', line
        )
        if item_match and not any(
            kw in line.lower() for kw in ["total", "subtotal", "tax", "balance"]
        ):
            desc = item_match.group(1).strip()
            amt = item_match.group(2).strip()
            # Skip if it's a header row
            if not any(h in desc.lower() for h in ["description", "item", "product", "qty"]):
                data["line_items"].append({
                    "description": desc,
                    "amount": amt,
                })

    # ── Notes ──
    # Look for "notes" or "terms" section
    for i, line in enumerate(lines):
        if re.search(r'\b(notes|terms|remarks|comments)\b', line, re.IGNORECASE):
            notes = []
            for j in range(i + 1, min(i + 5, len(lines))):
                nl = lines[j].strip()
                if nl and not re.search(r'total|subtotal|tax|balance', nl, re.IGNORECASE):
                    notes.append(nl)
            if notes:
                # Check notes isn't just more line items
                non_amount = [n for n in notes if not re.search(r'\$?\d+\.\d{2}', n)]
                if non_amount:
                    data["notes"] = " | ".join(non_amount)
            break

    # ── Customer Name ──
    # Look for "bill to", "customer", "ship to"
    for i, line in enumerate(lines):
        bl = line.strip().lower()
        if re.search(r'(bill\s*to|customer|ship\s*to|sold\s*to)', bl):
            if i + 1 < len(lines):
                data["customer_name"] = lines[i + 1].strip()
            break

    return data


def parse_multiple(text_blocks: list[str]) -> list[dict]:
    """Parse multiple invoice texts."""
    return [parse_invoice(t) for t in text_blocks]


# ─── File I/O ───────────────────────────────────────────────────────────────


def read_input(input_path: str) -> str:
    """Read invoice data from a file (PDF or text)."""
    path = Path(input_path)
    if not path.exists():
        print(f"  [!] File not found: {input_path}", file=sys.stderr)
        return ""

    ext = path.suffix.lower()
    if ext == ".pdf":
        print(f"  📄 Extracting text from PDF: {input_path}")
        return extract_text_from_pdf(str(path))
    else:
        return path.read_text(encoding="utf-8", errors="replace")


def save_output(data: dict | list, output_path: str):
    """Save parsed invoice data as CSV or JSON."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    records = data if isinstance(data, list) else [data]

    ext = path.suffix.lower()
    if ext == ".csv":
        # Flatten line items into separate rows for CSV
        flat_records = []
        for r in records:
            items = r.pop("line_items", [])
            if items:
                for item in items:
                    flat = {**r, "item_description": item["description"], "item_amount": item["amount"]}
                    flat_records.append(flat)
            else:
                r["item_description"] = ""
                r["item_amount"] = ""
                flat_records.append(r)

        with open(path, "w", newline="", encoding="utf-8") as f:
            if flat_records:
                writer = csv.DictWriter(f, fieldnames=flat_records[0].keys())
                writer.writeheader()
                writer.writerows(flat_records)
        print(f"  📄 CSV saved: {path} ({len(flat_records)} rows)")
    else:
        path.write_text(
            json.dumps(records, indent=2, default=str), encoding="utf-8"
        )
        print(f"  📊 JSON saved: {path} ({len(records)} invoices)")

    return path


# ─── Demo / Sample ──────────────────────────────────────────────────────────


def get_sample_invoice() -> str:
    """Return a sample invoice for testing."""
    return """INVOICE

Invoice Number: INV-2025-0042
Date: 2025-06-15
Due Date: 2025-07-15

From:
CloudTech Solutions Inc.
123 Innovation Drive, Suite 400
San Francisco, CA 94105
billing@cloudtech.io
(415) 555-0198

Bill To:
Acme Corporation
456 Business Ave
New York, NY 10001

Description                    Amount
Website Development            $5,000.00
UI/UX Design                   $3,500.00
Server Setup & Configuration   $1,200.00
Monthly Maintenance            $800.00

Subtotal:                      $10,500.00
Tax (8.5%):                    $892.50
Total Due:                     $11,392.50

Payment Terms: Net 30
Notes: Thank you for your business! Please include invoice number with payment.
"""


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Invoice/Receipt Data Extractor")
    parser.add_argument("--input", "-i", help="Invoice file (PDF or text)")
    parser.add_argument("--text", "-t", help="Invoice text (paste directly)")
    parser.add_argument("--output", "-o", default="invoice_data.csv", help="Output file (.csv or .json)")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample invoice")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  📄 Invoice/Receipt Data Extractor")
    print(f"{'='*60}")

    texts = []

    if args.demo:
        texts.append(get_sample_invoice())
        print(f"  Running demo with sample invoice...\n")
    elif args.text:
        texts.append(args.text)
    elif args.input:
        text = read_input(args.input)
        if text:
            texts.append(text)
    else:
        # Default: run demo
        texts.append(get_sample_invoice())
        print(f"  No input provided. Running demo with sample invoice...\n")

    if not texts or not any(texts):
        print("  [!] No invoice text to process.", file=sys.stderr)
        sys.exit(1)

    results = []
    for i, text in enumerate(texts):
        print(f"  Processing invoice {i + 1}/{len(texts)}...")
        parsed = parse_invoice(text)
        results.append(parsed)

        # Print summary
        print(f"  {'─' * 50}")
        print(f"  Invoice # : {parsed.get('invoice_number', 'N/A')}")
        print(f"  Date      : {parsed.get('invoice_date', 'N/A')}")
        print(f"  Vendor    : {parsed.get('vendor_name', 'N/A')}")
        print(f"  Customer  : {parsed.get('customer_name', 'N/A')}")
        print(f"  Total     : {parsed.get('currency', 'USD')} {parsed.get('total', 'N/A')}")
        print(f"  Items     : {len(parsed.get('line_items', []))} line items")
        print(f"  Tax       : {parsed.get('tax', 'N/A')}")
        print(f"  {'─' * 50}")

    # Save output
    out_path = save_output(results, args.output)

    # Print detailed results for demo mode
    if args.demo or not args.input:
        print(f"\n  Full parsed data:")
        print(f"  {json.dumps(results[0], indent=2)}")

    print(f"\n{'='*60}")
    print(f"  ✅ Extraction Complete!")
    print(f"  📄 Output: {out_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
