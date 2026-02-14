"""
Test: Process a PDF with any OpenAI model and measure cost/time.
Usage: python test_openai.py <model_id> <input_$/MTok> <output_$/MTok> <pdf_path>
"""

import base64
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from extraction_prompt import SYSTEM_MSG, EXTRACTION_PROMPT

load_dotenv(Path(__file__).parent / ".env")


def main():
    if len(sys.argv) != 6:
        print("Usage: python test_openai.py <model_id> <input_cost_per_MTok> <output_cost_per_MTok> <max_tokens> <pdf_path>")
        sys.exit(1)

    model = sys.argv[1]
    input_cost_per_m = float(sys.argv[2])
    output_cost_per_m = float(sys.argv[3])
    max_tokens = int(sys.argv[4])
    pdf_path = Path(sys.argv[5])

    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    pdf_bytes = pdf_path.read_bytes()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    client = OpenAI()

    start = time.perf_counter()

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {
                            "filename": pdf_path.name,
                            "file_data": f"data:application/pdf;base64,{pdf_b64}",
                        },
                    },
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            },
        ],
    )

    elapsed = time.perf_counter() - start

    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = input_tokens + output_tokens

    input_cost = (input_tokens / 1_000_000) * input_cost_per_m
    output_cost = (output_tokens / 1_000_000) * output_cost_per_m
    total_cost = input_cost + output_cost

    raw_text = response.choices[0].message.content
    try:
        extraction = json.loads(raw_text)
        parse_ok = True
    except json.JSONDecodeError:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            cleaned = cleaned.rsplit("```", 1)[0]
        try:
            extraction = json.loads(cleaned)
            parse_ok = True
        except json.JSONDecodeError:
            extraction = {"_raw": raw_text, "_parse_error": True}
            parse_ok = False

    results = {
        "model": model,
        "pdf_file": pdf_path.name,
        "pdf_size_bytes": len(pdf_bytes),
        "parse_ok": parse_ok,
        "extraction": extraction,
        "tokens": {"input": input_tokens, "output": output_tokens, "total": total_tokens},
        "cost_usd": {
            "input": round(input_cost, 6),
            "output": round(output_cost, 6),
            "total": round(total_cost, 6),
        },
        "time_seconds": round(elapsed, 2),
    }

    print(json.dumps(results))


if __name__ == "__main__":
    main()
