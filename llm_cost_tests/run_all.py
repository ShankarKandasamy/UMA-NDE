"""
Run all model x PDF combinations and produce a comparison table.
Saves individual extraction results and a summary table.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
DOCS_DIR = SCRIPT_DIR.parent / "docs" / "GreatLakesDataset" / "documents"

PDFS = [
    DOCS_DIR / "GLCP-RFQ-2024-089.pdf",
    DOCS_DIR / "GLCP-NDT-001.pdf",
    DOCS_DIR / "pdf_sample_textbook.pdf",
    DOCS_DIR / "Farm Financial Health_10pages.pdf",
]

# (provider_script, model_id, input_$/MTok, output_$/MTok, max_tokens, display_name)
MODELS = [
    ("test_anthropic.py", "claude-opus-4-6",          5.00, 25.00, 32768, "Claude Opus 4.6"),
    ("test_anthropic.py", "claude-opus-4-5-20251101", 5.00, 25.00, 32768, "Claude Opus 4.5"),
    ("test_openai.py",    "gpt-4.1",                  2.00,  8.00, 32768, "GPT-4.1"),
    ("test_openai.py",    "gpt-4o",                   2.50, 10.00, 16384, "GPT-4o"),
    ("test_openai.py",    "gpt-4o-mini",              0.15,  0.60, 16384, "GPT-4o-mini"),
]


def run_test(script, model, input_cost, output_cost, max_tokens, pdf_path):
    """Run a single test and return parsed results dict."""
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / script),
        model,
        str(input_cost),
        str(output_cost),
        str(max_tokens),
        str(pdf_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            return {"error": result.stderr.strip()[-500:] or "Unknown error", "model": model, "pdf_file": pdf_path.name}
        lines = result.stdout.strip().split("\n")
        return json.loads(lines[-1])
    except subprocess.TimeoutExpired:
        return {"error": "Timeout (600s)", "model": model, "pdf_file": pdf_path.name}
    except Exception as e:
        return {"error": str(e), "model": model, "pdf_file": pdf_path.name}


def quality_metrics(r):
    """Extract quality metrics from a successful result."""
    if "error" in r or not r.get("parse_ok"):
        return {"json_valid": False}

    ext = r.get("extraction", {})
    summary = ext.get("summary", "")
    sections = ext.get("sections", [])
    tables = ext.get("tables", [])
    images = ext.get("images", [])
    charts = ext.get("charts", [])

    return {
        "json_valid": True,
        "has_title": bool(ext.get("title")),
        "has_pages": isinstance(ext.get("pages"), int),
        "summary_len": len(summary),
        "summary_in_range": 550 <= len(summary) <= 1100,
        "num_sections": len(sections),
        "num_tables": len(tables),
        "total_table_rows": sum(len(t.get("rows", [])) for t in tables),
        "num_images": len(images),
        "num_charts": len(charts),
    }


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    all_results = []

    for script, model_id, in_cost, out_cost, max_tok, display_name in MODELS:
        for pdf_path in PDFS:
            label = f"{display_name} | {pdf_path.name}"
            print(f"  Running: {label} ...", end="", flush=True)
            result = run_test(script, model_id, in_cost, out_cost, max_tok, pdf_path)
            result["display_name"] = display_name
            all_results.append(result)

            if "error" in result:
                print(f" ERROR: {result['error'][:80]}")
            else:
                print(f" ${result['cost_usd']['total']:.4f} | {result['time_seconds']}s | parse={'OK' if result['parse_ok'] else 'FAIL'}")

                # Save individual extraction JSON
                safe_model = model_id.replace("/", "_")
                safe_pdf = pdf_path.stem
                ind_path = RESULTS_DIR / f"{safe_model}__{safe_pdf}.json"
                ind_path.write_text(json.dumps(result, indent=2))

    # Save all results
    out_path = RESULTS_DIR / "all_results.json"
    out_path.write_text(json.dumps(all_results, indent=2))

    # ---- Cost comparison table ----
    print(f"\n{'='*110}")
    print(f"  COST & PERFORMANCE TABLE")
    print(f"{'='*110}")
    header = (
        f"{'Model':<22} {'PDF':<24} {'Parse':>5} "
        f"{'In Tok':>8} {'Out Tok':>8} {'Time':>7} "
        f"{'In $':>9} {'Out $':>9} {'TOTAL $':>9}"
    )
    print(header)
    print("-" * 110)

    for r in all_results:
        if "error" in r:
            print(f"{r.get('display_name','?'):<22} {r['pdf_file']:<24} {'ERROR: ' + r['error'][:60]}")
        else:
            print(
                f"{r['display_name']:<22} "
                f"{r['pdf_file']:<24} "
                f"{'OK' if r['parse_ok'] else 'FAIL':>5} "
                f"{r['tokens']['input']:>8,} "
                f"{r['tokens']['output']:>8,} "
                f"{r['time_seconds']:>6.1f}s "
                f"${r['cost_usd']['input']:>8.4f} "
                f"${r['cost_usd']['output']:>8.4f} "
                f"${r['cost_usd']['total']:>8.4f}"
            )

    print("-" * 110)

    # ---- Quality metrics table ----
    print(f"\n{'='*110}")
    print(f"  EXTRACTION QUALITY TABLE")
    print(f"{'='*110}")
    qheader = (
        f"{'Model':<22} {'PDF':<24} {'JSON':>4} "
        f"{'Title':>5} {'Pages':>5} {'SumLen':>6} {'InRng':>5} "
        f"{'Sects':>5} {'Tbls':>5} {'TRows':>5} {'Imgs':>5} {'Chrts':>5}"
    )
    print(qheader)
    print("-" * 110)

    for r in all_results:
        if "error" in r:
            continue
        q = quality_metrics(r)
        yn = lambda v: "Y" if v else "N"
        print(
            f"{r['display_name']:<22} "
            f"{r['pdf_file']:<24} "
            f"{yn(q['json_valid']):>4} "
            f"{yn(q.get('has_title')):>5} "
            f"{yn(q.get('has_pages')):>5} "
            f"{q.get('summary_len', 0):>6} "
            f"{yn(q.get('summary_in_range')):>5} "
            f"{q.get('num_sections', 0):>5} "
            f"{q.get('num_tables', 0):>5} "
            f"{q.get('total_table_rows', 0):>5} "
            f"{q.get('num_images', 0):>5} "
            f"{q.get('num_charts', 0):>5}"
        )

    print("-" * 110)

    # ---- Summary averages ----
    print(f"\n{'Model':<22} {'Avg Cost':>10} {'Avg Time':>10} {'Avg OutTok':>10} {'JSON OK':>8}")
    print("-" * 62)
    for _, model_id, _, _, _, display_name in MODELS:
        mr = [r for r in all_results if r.get("display_name") == display_name and "error" not in r]
        if mr:
            avg_cost = sum(r["cost_usd"]["total"] for r in mr) / len(mr)
            avg_time = sum(r["time_seconds"] for r in mr) / len(mr)
            avg_out = sum(r["tokens"]["output"] for r in mr) / len(mr)
            json_ok = sum(1 for r in mr if r.get("parse_ok"))
            print(f"{display_name:<22} ${avg_cost:>9.4f} {avg_time:>9.1f}s {avg_out:>10.0f} {json_ok}/{len(mr):>6}")
        else:
            print(f"{display_name:<22} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>8}")

    print(f"\nResults saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
