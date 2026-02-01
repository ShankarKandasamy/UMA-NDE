"""
Stage 11: LLM Reorder - Use GPT-4o-mini to reconstruct document with proper reading order

Reads LLM-ready JSON from Stage 10 and screenshots from Stage 1, then uses GPT-4o-mini
with vision to reconstruct the document in correct reading order with:
- Proper heading hierarchy (Markdown #, ##, ###)
- OCR error correction
- Multi-column reading flow
- De-hyphenation and text merging

Input:
  - Stage 10 LLM-ready JSON (e.g., page_1_llm_ready.json)
  - Stage 1 screenshots (e.g., page_1.png)
Output:
  - Markdown files (e.g., page_1_reordered.md)

Usage:
    python stage_11_llm_reorder.py --input_dir <stage10_dir> --screenshots_dir <screenshots_dir> --output_dir <output_dir>
"""

import base64
import argparse
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def encode_image(image_path):
    """
    Encode image to base64 string.

    Args:
        image_path: Path to image file

    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def format_buckets_for_llm(page_data):
    """
    Format bucket data for LLM processing, including previous page context.

    Args:
        page_data: Page data dict from Stage 10

    Returns:
        Formatted string with bucket content and metadata
    """
    buckets = page_data['buckets']
    page_number = page_data['page_number']
    last_bucket_prev = page_data.get('last_bucket_previous_page')

    formatted = f"PAGE {page_number} CONTENT:\n\n"

    # Add previous page context if available
    if last_bucket_prev:
        texts = last_bucket_prev.get('texts', [])
        text_content = '\n'.join(texts)
        formatted += "CONTEXT FROM PREVIOUS PAGE (Last Bucket):\n"
        formatted += f"  Position: {last_bucket_prev.get('position', 'unknown')}, "
        formatted += f"Width: {last_bucket_prev.get('width_category', 'unknown')}\n"
        formatted += f"  Content:\n{text_content}\n\n"
        formatted += "---\n\n"

    for bucket in buckets:
        bucket_id = bucket['id']
        position = bucket['position']
        width = bucket['width_category']
        y_group = bucket['y_group_id']
        confidence = bucket['confidence_avg']

        # Format text content
        texts = bucket['texts']
        text_content = '\n'.join(texts)

        formatted += f"BUCKET {bucket_id}:\n"
        formatted += f"  Position: {position}, Width: {width}, Y-Group: {y_group}, Confidence: {confidence}\n"
        formatted += f"  Content:\n{text_content}\n\n"

    return formatted


def create_bucket_checklist(buckets):
    """
    Create a bucket checklist to help LLM ensure complete coverage.

    Args:
        buckets: List of bucket dicts

    Returns:
        Formatted checklist string
    """
    checklist = "BUCKET CHECKLIST (You MUST include ALL buckets):\n"
    for bucket in buckets:
        checklist += f"  - Bucket {bucket['id']}: position={bucket['position']}, y_group={bucket['y_group_id']}, chars={bucket['char_count']}\n"

    return checklist


def reorder_page_with_llm(page_data, screenshot_path, client):
    """
    Use GPT-4o-mini to reconstruct page with proper reading order.

    Args:
        page_data: Page data dict from Stage 10
        screenshot_path: Path to screenshot image
        client: OpenAI client instance

    Returns:
        Reconstructed markdown text
    """
    # Encode the screenshot
    base64_image = encode_image(screenshot_path)

    # Prepare bucket content
    buckets_text = format_buckets_for_llm(page_data)
    bucket_checklist = create_bucket_checklist(page_data['buckets'])

    # System prompt (recovered from git history with improvements)
    system_prompt = """Act as an expert in OCR post-processing and document reconstruction. You are provided with three inputs:
1) A screenshot of a document page,
2) A list of text buckets extracted from that page with spatial metadata, and
3) The last bucket (paragraph(s)) from the previous page (if available) for context continuity.

Your objective is to output a single, coherent Markdown document that includes all the given buckets (blocks) of text and perfectly represents the
original page's content in the correct reading order.


0. **Cross-Page Context:**
   * If "last_bucket_previous_page" is provided (not null), use it to understand how this page connects to the previous one.
   * Use the "last_bucket_previous_page" content to determine which text bucket in the current page is the continuation of the previous page.
   * If continuation is detected, seamlessly merge the content WITHOUT repeating the previous page's text.

1. **Complete Bucket Coverage (CRITICAL):**
   * You MUST include ALL text content from ALL buckets in your output.
   * Verify that you've processed every bucket ID (0 through N).
   * Do NOT skip any buckets, even if they seem redundant or transitional.
   * Use the bucket metadata (position, y_group_id) and the screenshot as hints to aid in correct placement.
   * Preserve fragmented text at the location it appears in the screenshot and as it appears in the list of text buckets.

2. **Visual Layout Analysis:**
   * If the document is multi-column, read down the first column entirely before moving to the second.
   * Use visual layout and font analysis to correctly reconstruct the hierarchy of the text.
   * Any text identified as a sidebar, marginal note, or explanatory callout MUST be preserved and formatted using Markdown blockquotes (>) immediately following the paragraph it is spatially adjacent to


3. **Text Reconstruction & Cleaning:**
   * **Merge Chunks:** The input text is fragmented. You must merge split sentences and paragraphs
     to ensure a continuous flow. Do not leave line breaks where they don't belong.
   * **De-Hyphenation:** If a word was split by a hyphen at the end of a line (e.g., "process- ing"),
     rejoin it ("processing").
   * **OCR Repair:** Fix obvious typos (e.g., '1' vs 'l', 'rn' vs 'm', 'Iniversity' vs 'University')
     by comparing the text context with the visual evidence in the screenshot. Remove random noise characters.
   * Use the Confidence Score as a clue to help you determine if the text is correct.

4. **Formatting:**
   * Use Markdown headers (#, ##, ###) to match the visual hierarchy of titles.
   * Use [FIG-CAPTION:, [FIG-TITLE:, [FIG-LABEL: prefix for figure captions, figure titles, figure labels and sidenotes.
   * If a table exists, reconstruct it using Markdown table syntax.
   * Place figure captions in a separate block immediately following the paragraph that references the figure.
   * Preserve bold, italic, and other formatting visible in the screenshot.

**Output Format:** Return a JSON object with the following structure:
```json
{
  "markdown": "... your reconstructed markdown text here ...",
  "buckets_used": [0, 1, 2, 5, 7, ...],
  "buckets_skipped": [3, 4, 6, ...],
  "skipped_reason": "Optional: brief explanation for why buckets were skipped (e.g., 'OCR gibberish', 'duplicate content')"
}
```

The `buckets_used` array must contain the IDs of all buckets you incorporated into the markdown.
The `buckets_skipped` array should contain any bucket IDs you intentionally excluded (if any).
Provide ONLY valid JSON. Do not include markdown code fences or any other text.
"""

    user_prompt = f"""{bucket_checklist}

{buckets_text}

Remember: Include ALL {len(page_data['buckets'])} buckets in your output. Verify completeness before finishing."""

    # Call OpenAI API with vision
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=4096,
        temperature=0.1
    )

    # Parse JSON response
    response_text = response.choices[0].message.content.strip()

    # Remove markdown code fences if present
    if response_text.startswith('```json'):
        response_text = response_text[7:]  # Remove ```json
    if response_text.startswith('```'):
        response_text = response_text[3:]  # Remove ```
    if response_text.endswith('```'):
        response_text = response_text[:-3]  # Remove trailing ```

    response_text = response_text.strip()

    try:
        response_data = json.loads(response_text)
        return {
            'markdown': response_data.get('markdown', ''),
            'buckets_used': response_data.get('buckets_used', []),
            'buckets_skipped': response_data.get('buckets_skipped', []),
            'skipped_reason': response_data.get('skipped_reason', '')
        }
    except json.JSONDecodeError as e:
        # Try alternative parsing: escape backslashes that aren't part of valid escape sequences
        print(f"    ⚠ Warning: Failed to parse JSON response: {e}")
        print(f"    🔧 Attempting alternative parsing with escape sequence fix...")

        try:
            # Fix common LaTeX escape sequences by temporarily replacing them
            fixed_text = response_text

            # Replace LaTeX backslashes with a placeholder
            # In JSON, backslashes are escaped, so \frac appears as \\frac
            latex_replacements = [
                ('\\\\frac', '<<<FRAC>>>'),
                ('\\\\sin', '<<<SIN>>>'),
                ('\\\\cos', '<<<COS>>>'),
                ('\\\\tan', '<<<TAN>>>'),
                ('\\\\log', '<<<LOG>>>'),
                ('\\\\sqrt', '<<<SQRT>>>'),
                ('\\\\mathbb', '<<<MATHBB>>>'),
                ('\\\\{', '<<<LBRACE>>>'),
                ('\\\\}', '<<<RBRACE>>>'),
                ('\\\\(', '<<<LMATH>>>'),
                ('\\\\)', '<<<RMATH>>>'),
                ('\\\\[', '<<<LBIGMATH>>>'),
                ('\\\\]', '<<<RBIGMATH>>>'),
                ('\\\\leq', '<<<LEQ>>>'),
                ('\\\\geq', '<<<GEQ>>>'),
                ('\\\\neq', '<<<NEQ>>>'),
                ('\\\\in', '<<<IN>>>'),
                ('\\\\times', '<<<TIMES>>>'),
                ('\\\\left', '<<<LEFT>>>'),
                ('\\\\right', '<<<RIGHT>>>'),
            ]

            for latex, placeholder in latex_replacements:
                fixed_text = fixed_text.replace(latex, placeholder)

            # Now parse the JSON
            response_data = json.loads(fixed_text)

            # Restore LaTeX in the markdown
            # After JSON parsing, \\frac becomes \frac in the Python string
            latex_restore = [
                ('<<<FRAC>>>', '\\frac'),
                ('<<<SIN>>>', '\\sin'),
                ('<<<COS>>>', '\\cos'),
                ('<<<TAN>>>', '\\tan'),
                ('<<<LOG>>>', '\\log'),
                ('<<<SQRT>>>', '\\sqrt'),
                ('<<<MATHBB>>>', '\\mathbb'),
                ('<<<LBRACE>>>', '\\{'),
                ('<<<RBRACE>>>', '\\}'),
                ('<<<LMATH>>>', '\\('),
                ('<<<RMATH>>>', '\\)'),
                ('<<<LBIGMATH>>>', '\\['),
                ('<<<RBIGMATH>>>', '\\]'),
                ('<<<LEQ>>>', '\\leq'),
                ('<<<GEQ>>>', '\\geq'),
                ('<<<NEQ>>>', '\\neq'),
                ('<<<IN>>>', '\\in'),
                ('<<<TIMES>>>', '\\times'),
                ('<<<LEFT>>>', '\\left'),
                ('<<<RIGHT>>>', '\\right'),
            ]

            markdown = response_data.get('markdown', '')
            for placeholder, latex in latex_restore:
                markdown = markdown.replace(placeholder, latex)

            print(f"    ✓ Successfully parsed with escape sequence fix")
            return {
                'markdown': markdown,
                'buckets_used': response_data.get('buckets_used', []),
                'buckets_skipped': response_data.get('buckets_skipped', []),
                'skipped_reason': response_data.get('skipped_reason', '') + ' [escape sequence fix applied]'
            }
        except json.JSONDecodeError as e2:
            print(f"    ✗ Alternative parsing also failed: {e2}")
            print(f"    🔧 Attempting manual markdown extraction from JSON string...")

            # Last resort: try to manually extract the markdown field from the JSON string
            try:
                import re
                # Find the markdown field value in the JSON string
                # Pattern: "markdown": "..."  (handling escaped quotes and newlines)
                markdown_match = re.search(r'"markdown"\s*:\s*"((?:[^"\\]|\\.)*)(?<!\\)"', response_text, re.DOTALL)

                if markdown_match:
                    # Extract the markdown content and unescape JSON string escapes
                    markdown_content = markdown_match.group(1)
                    # Unescape common JSON escape sequences
                    markdown_content = markdown_content.replace('\\n', '\n')
                    markdown_content = markdown_content.replace('\\t', '\t')
                    markdown_content = markdown_content.replace('\\"', '"')
                    markdown_content = markdown_content.replace('\\\\', '\\')

                    print(f"    ✓ Successfully extracted markdown via regex (length: {len(markdown_content)} chars)")
                    return {
                        'markdown': markdown_content,
                        'buckets_used': [],
                        'buckets_skipped': [],
                        'skipped_reason': f'JSON parsing failed, used regex extraction'
                    }
                else:
                    # If regex extraction also fails, return the raw response
                    print(f"    ✗ Manual extraction failed - using raw response")
                    return {
                        'markdown': response_text,
                        'buckets_used': [],
                        'buckets_skipped': [],
                        'skipped_reason': f'JSON parsing failed: {e} | Alternative parsing failed: {e2} | Regex extraction failed'
                    }
            except Exception as e3:
                print(f"    ✗ Manual extraction error: {e3}")
                return {
                    'markdown': response_text,
                    'buckets_used': [],
                    'buckets_skipped': [],
                    'skipped_reason': f'JSON parsing failed: {e} | Alternative parsing failed: {e2} | Manual extraction failed: {e3}'
                }


def verify_bucket_coverage(page_data, buckets_used):
    """
    Verify that all buckets are represented in the output based on LLM's bucket tracking.

    Args:
        page_data: Page data dict from Stage 10
        buckets_used: List of bucket IDs that LLM reported as used

    Returns:
        List of missing bucket IDs
    """
    all_bucket_ids = set(bucket['id'] for bucket in page_data['buckets'])
    used_bucket_ids = set(buckets_used)

    missing_buckets = list(all_bucket_ids - used_bucket_ids)
    missing_buckets.sort()  # Sort for consistent output

    return missing_buckets


def process_page(llm_ready_file, screenshot_file, output_dir, client):
    """
    Process a single page: reconstruct with proper reading order.

    Args:
        llm_ready_file: Path to LLM-ready JSON file
        screenshot_file: Path to screenshot image
        output_dir: Directory to save output
        client: OpenAI client instance

    Returns:
        Dict with processing stats
    """
    # Read page data
    with open(llm_ready_file, 'r', encoding='utf-8') as f:
        page_data = json.load(f)

    page_num = page_data['page_number']
    total_buckets = page_data['total_buckets']

    print(f"  Buckets: {total_buckets}")
    print(f"  Sending to GPT-4o-mini...")

    # Reconstruct with LLM (returns JSON with markdown and bucket tracking)
    llm_response = reorder_page_with_llm(page_data, screenshot_file, client)

    markdown_text = llm_response['markdown']
    buckets_used = llm_response['buckets_used']
    buckets_skipped = llm_response['buckets_skipped']
    skipped_reason = llm_response['skipped_reason']

    # Verify bucket coverage
    missing_buckets = verify_bucket_coverage(page_data, buckets_used)

    if missing_buckets:
        print(f"  ⚠ WARNING: Missing buckets detected: {missing_buckets}")
        if skipped_reason:
            print(f"    Reason: {skipped_reason}")
        # TODO Stage 12: Implement missing bucket recovery

    # Write markdown output
    output_file = output_dir / f"page_{page_num}_reordered.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_text)

    # Write JSON metadata with bucket tracking
    metadata_file = output_dir / f"page_{page_num}_metadata.json"
    metadata = {
        'page_number': page_num,
        'total_buckets': total_buckets,
        'buckets_used': buckets_used,
        'buckets_skipped': buckets_skipped,
        'missing_buckets': missing_buckets,
        'skipped_reason': skipped_reason,
        'output_length': len(markdown_text)
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    return {
        'page_number': page_num,
        'input_file': str(llm_ready_file),
        'screenshot_file': str(screenshot_file),
        'output_file': str(output_file),
        'metadata_file': str(metadata_file),
        'total_buckets': total_buckets,
        'buckets_used': buckets_used,
        'buckets_skipped': buckets_skipped,
        'missing_buckets': missing_buckets,
        'output_length': len(markdown_text)
    }


def process_all_pages(input_dir, screenshots_dir, output_dir):
    """
    Process all pages in the input directory.

    Args:
        input_dir: Directory containing LLM-ready JSON files from Stage 10
        screenshots_dir: Directory containing screenshot images from Stage 1
        output_dir: Directory to save output files

    Returns:
        Dict with overall statistics
    """
    input_dir = Path(input_dir)
    screenshots_dir = Path(screenshots_dir)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    # Find all LLM-ready JSON files
    json_files = sorted(input_dir.glob('page_*_llm_ready.json'))

    if not json_files:
        print(f"No LLM-ready JSON files found in {input_dir}")
        return {
            'total_pages': 0,
            'pages': []
        }

    print(f"Found {len(json_files)} LLM-ready JSON file(s)")
    print()

    page_results = []
    total_missing_buckets = 0

    for json_file in json_files:
        # Extract page number from filename
        page_num = json_file.stem.replace('_llm_ready', '').replace('page_', '')

        # Find corresponding screenshot
        screenshot_file = None

        # Pattern 1: page_N.png
        screenshot_candidate = screenshots_dir / f"page_{page_num}.png"
        if screenshot_candidate.exists():
            screenshot_file = screenshot_candidate
        else:
            # Pattern 2: page_N_*.png (with PDF name suffix)
            screenshot_candidates = list(screenshots_dir.glob(f"page_{page_num}_*.png"))
            if screenshot_candidates:
                screenshot_file = screenshot_candidates[0]

        if not screenshot_file or not screenshot_file.exists():
            print(f"⚠ Warning: Screenshot not found for {json_file.name}, skipping...")
            continue

        print(f"Processing: Page {page_num}")
        print(f"  Input: {json_file.name}")
        print(f"  Screenshot: {screenshot_file.name}")

        try:
            result = process_page(json_file, screenshot_file, output_dir, client)
            page_results.append(result)

            if result['missing_buckets']:
                total_missing_buckets += len(result['missing_buckets'])

            print(f"  ✓ Output: {Path(result['output_file']).name}")
            print(f"  ✓ Length: {result['output_length']} characters")
            print()
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
            continue

    return {
        'total_pages': len(page_results),
        'total_missing_buckets': total_missing_buckets,
        'pages': page_results
    }


def main():
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description='Stage 11: LLM Reorder - Reconstruct document with proper reading order'
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        required=True,
        help='Input directory containing LLM-ready JSON files from Stage 10'
    )
    parser.add_argument(
        '--screenshots_dir',
        type=str,
        required=True,
        help='Input directory containing screenshot images from Stage 1'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for reordered Markdown files'
    )

    args = parser.parse_args()

    print("="*80)
    print("STAGE 11: LLM Reorder (GPT-4o-mini)")
    print("="*80)
    print(f"Input directory: {args.input_dir}")
    print(f"Screenshots directory: {args.screenshots_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    results = process_all_pages(args.input_dir, args.screenshots_dir, args.output_dir)

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total pages processed: {results['total_pages']}")

    if results['total_missing_buckets'] > 0:
        print(f"⚠ Total missing buckets: {results['total_missing_buckets']}")

    print()

    if results['total_pages'] > 0:
        print("Output files:")
        for page_result in results['pages']:
            status = "✓" if not page_result['missing_buckets'] else "⚠"
            print(f"  {status} Page {page_result['page_number']}: {page_result['output_file']}")
        print()

    print("Document reconstruction complete!")
    print()


if __name__ == '__main__':
    main()
