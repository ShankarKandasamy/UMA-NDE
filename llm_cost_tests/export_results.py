"""
Reads each model result JSON and exports:
  - The raw extraction JSON into a model-named folder
  - Each section/chunk as a separate markdown file
  - A summary markdown with tables, images, charts info
"""

import json
import re
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
OUTPUT_DIR = Path(__file__).parent / "comparison"

# Map model IDs to clean folder names
MODEL_NAMES = {
    "claude-opus-4-6": "claude-opus-4.6",
    "claude-opus-4-5-20251101": "claude-opus-4.5",
    "gpt-4.1": "gpt-4.1",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
}


def slugify(text):
    """Turn a heading into a safe filename."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:60].strip('-')


def export_result(result_path):
    data = json.loads(result_path.read_text(encoding="utf-8"))
    model_id = data["model"]
    pdf_stem = Path(data["pdf_file"]).stem
    extraction = data.get("extraction", {})

    model_folder = MODEL_NAMES.get(model_id, model_id)
    out_dir = OUTPUT_DIR / model_folder / pdf_stem
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save raw extraction JSON
    json_path = out_dir / "extraction.json"
    json_path.write_text(json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8")

    # 2. Save cost/token metadata
    meta = {
        "model": model_id,
        "pdf_file": data["pdf_file"],
        "pdf_size_bytes": data.get("pdf_size_bytes"),
        "parse_ok": data.get("parse_ok"),
        "tokens": data.get("tokens"),
        "cost_usd": data.get("cost_usd"),
        "time_seconds": data.get("time_seconds"),
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # 3. Export each section as a markdown chunk
    sections = extraction.get("sections", [])
    for i, section in enumerate(sections):
        heading = section.get("heading", f"Section {i+1}")
        text = section.get("text", "")
        slug = slugify(heading)
        filename = f"chunk-{i+1:02d}-{slug}.md"

        md = f"# {heading}\n\n{text}\n"
        (out_dir / filename).write_text(md, encoding="utf-8")

    # 4. Summary markdown with title, summary, tables, images, charts
    summary_md = []
    summary_md.append(f"# {extraction.get('title', 'Untitled')}\n")
    summary_md.append(f"**Pages:** {extraction.get('pages', '?')}\n")
    summary_md.append(f"**Model:** {model_id}\n")
    summary_md.append(f"**Cost:** ${data.get('cost_usd', {}).get('total', '?')} | "
                       f"**Time:** {data.get('time_seconds', '?')}s | "
                       f"**Tokens:** {data.get('tokens', {}).get('input', '?')} in / "
                       f"{data.get('tokens', {}).get('output', '?')} out\n")

    summary_md.append(f"\n## Summary\n\n{extraction.get('summary', 'N/A')}\n")
    summary_md.append(f"\n*Summary length: {len(extraction.get('summary', ''))} characters*\n")

    # Tables
    tables = extraction.get("tables", [])
    if tables:
        summary_md.append(f"\n## Tables ({len(tables)} found)\n")
        for t in tables:
            title = t.get("title", "Untitled Table")
            headers = t.get("headers", [])
            rows = t.get("rows", [])
            summary_md.append(f"\n### {title}\n")
            if headers:
                summary_md.append("| " + " | ".join(str(h) for h in headers) + " |")
                summary_md.append("| " + " | ".join("---" for _ in headers) + " |")
                for row in rows:
                    summary_md.append("| " + " | ".join(str(c) for c in row) + " |")
            summary_md.append("")

    # Images
    images = extraction.get("images", [])
    if images:
        summary_md.append(f"\n## Images ({len(images)} found)\n")
        for img in images:
            summary_md.append(f"- **Page {img.get('page', '?')}:** {img.get('description', 'N/A')}")
            if img.get("ocr_text"):
                summary_md.append(f"  - OCR: {img['ocr_text']}")
        summary_md.append("")

    # Charts
    charts = extraction.get("charts", [])
    if charts:
        summary_md.append(f"\n## Charts ({len(charts)} found)\n")
        for ch in charts:
            summary_md.append(f"- **{ch.get('type', 'chart')}** (Page {ch.get('page', '?')}): {ch.get('title', 'N/A')}")
            if ch.get("insights"):
                summary_md.append(f"  - Insights: {ch['insights']}")
            if ch.get("data"):
                summary_md.append(f"  - Data: {json.dumps(ch['data'])}")
        summary_md.append("")

    # Section index
    summary_md.append(f"\n## Sections ({len(sections)} chunks)\n")
    for i, section in enumerate(sections):
        heading = section.get("heading", f"Section {i+1}")
        slug = slugify(heading)
        filename = f"chunk-{i+1:02d}-{slug}.md"
        summary_md.append(f"{i+1}. [{heading}]({filename})")

    (out_dir / "_overview.md").write_text("\n".join(summary_md), encoding="utf-8")

    return model_folder, pdf_stem, len(sections)


def main():
    result_files = sorted(RESULTS_DIR.glob("*.json"))
    result_files = [f for f in result_files if f.name != "all_results.json"]

    print(f"Exporting {len(result_files)} results...\n")

    for rf in result_files:
        try:
            model, pdf, n_chunks = export_result(rf)
            print(f"  {model:<22} {pdf:<24} -> {n_chunks} chunks")
        except Exception as e:
            print(f"  ERROR on {rf.name}: {e}")

    print(f"\nAll exported to: {OUTPUT_DIR}")
    print("\nFolder structure:")
    for model_dir in sorted(OUTPUT_DIR.iterdir()):
        if model_dir.is_dir():
            print(f"  {model_dir.name}/")
            for pdf_dir in sorted(model_dir.iterdir()):
                if pdf_dir.is_dir():
                    files = list(pdf_dir.iterdir())
                    print(f"    {pdf_dir.name}/  ({len(files)} files)")


if __name__ == "__main__":
    main()
