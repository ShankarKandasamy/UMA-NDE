"""
Test: Process a PDF with Claude Opus 4.6 and measure cost/time.
Sends the PDF as base64 to the API and asks for a 100-200 word JSON summary.

Usage: python test_claude_opus.py [path_to_pdf]
       Defaults to GLCP-RFQ-2024-089.pdf if no argument given.
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

# Load API key from local .env
load_dotenv(Path(__file__).parent / ".env")

# --- Config ---
DEFAULT_PDF = Path(__file__).parent.parent / "docs" / "GreatLakesDataset" / "documents" / "GLCP-RFQ-2024-089.pdf"
MODEL = "claude-opus-4-6"

# Pricing per million tokens (USD) - Claude Opus 4.6 (Feb 2026)
INPUT_COST_PER_M = 5.00
OUTPUT_COST_PER_M = 25.00

def main():
    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    # Read and encode PDF
    pdf_bytes = pdf_path.read_bytes()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    print(f"PDF: {pdf_path.name}  ({len(pdf_bytes):,} bytes)")

    client = Anthropic()

    prompt = (
        "Analyze this document and return ONLY a valid JSON object with a single key "
        '"summary" containing a 100-200 word summary of the document. '
        "No markdown, no code fences, just the raw JSON."
    )

    # Time the API call
    start = time.perf_counter()

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are an NDT inspection report analyst. Always respond with valid JSON only.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    elapsed = time.perf_counter() - start

    # Extract usage
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    total_tokens = input_tokens + output_tokens

    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_M
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_M
    total_cost = input_cost + output_cost

    # Parse the response
    raw_text = message.content[0].text
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {"summary": raw_text, "_parse_error": "Response was not valid JSON"}

    # Build results
    results = {
        "model": MODEL,
        "pdf_file": pdf_path.name,
        "pdf_size_bytes": len(pdf_bytes),
        "summary": result.get("summary", raw_text),
        "tokens": {
            "input": input_tokens,
            "output": output_tokens,
            "total": total_tokens,
        },
        "cost_usd": {
            "input": round(input_cost, 6),
            "output": round(output_cost, 6),
            "total": round(total_cost, 6),
        },
        "time_seconds": round(elapsed, 2),
    }

    # Save results with filename in output name
    stem = pdf_path.stem
    out_path = Path(__file__).parent / f"result_{stem}_opus.json"
    out_path.write_text(json.dumps(results, indent=2))

    # Print report
    print(f"\n{'='*60}")
    print(f"  Model:          {MODEL}")
    print(f"  PDF:            {pdf_path.name}")
    print(f"  Time:           {elapsed:.2f}s")
    print(f"{'='*60}")
    print(f"  Input tokens:   {input_tokens:,}")
    print(f"  Output tokens:  {output_tokens:,}")
    print(f"  Total tokens:   {total_tokens:,}")
    print(f"{'='*60}")
    print(f"  Input cost:     ${input_cost:.6f}")
    print(f"  Output cost:    ${output_cost:.6f}")
    print(f"  TOTAL COST:     ${total_cost:.6f}")
    print(f"{'='*60}")
    print(f"\n  Summary:\n")
    summary_text = result.get("summary", raw_text)
    words = summary_text.split()
    line = "    "
    for w in words:
        if len(line) + len(w) + 1 > 80:
            print(line)
            line = "    " + w
        else:
            line += " " + w if line.strip() else "    " + w
    if line.strip():
        print(line)

    print(f"\n  Results saved to: {out_path}")

if __name__ == "__main__":
    main()
