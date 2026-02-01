"""
Stage 12: Bucket Recovery - Detect and recover missing buckets from Stage 11

This stage analyzes Stage 11 output to find buckets that were not included in the
LLM-generated markdown. It uses:
1. Pre-filtering to skip empty/whitespace/very short buckets
2. Hybrid matching (fuzzy + word coverage + n-gram) to detect truly missing buckets
3. GPT-4o-mini vision to determine if missing buckets are OCR errors or legitimate
4. Insertion of legitimate missing buckets into the correct location in markdown

Input:
  - Stage 10 LLM-ready JSON (e.g., page_1_llm_ready.json)
  - Stage 11 metadata JSON (e.g., page_1_metadata.json)
  - Stage 11 markdown (e.g., page_1_reordered.md)
  - Stage 1 screenshots (e.g., page_1.png)
Output:
  - Final markdown files (e.g., page_1_final.md)
  - Recovery reports (e.g., page_1_recovery_report.json)

Usage:
    python stage_12_bucket_recovery.py --stage10_dir <dir> --stage11_dir <dir> --screenshots_dir <dir> --output_dir <dir>
"""

import base64
import argparse
import json
import re
import sys
import io
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os
from difflib import SequenceMatcher
from rapidfuzz import fuzz

# Load environment variables
load_dotenv()


def should_skip_bucket(bucket):
    """
    Pre-filter buckets that are clearly invalid (empty, whitespace, very short).

    Args:
        bucket: Bucket dict from Stage 10

    Returns:
        (bool, str): (True/False, reason for skipping)
    """
    texts = bucket.get('texts', [])

    if not texts:
        return (True, "empty_texts")

    # Join all texts and check
    combined_text = ' '.join(texts).strip()

    if not combined_text:
        return (True, "whitespace_only")

    if len(combined_text) < 3:
        return (True, "too_short")

    # Check if it's just punctuation or special characters
    if all(not c.isalnum() for c in combined_text):
        return (True, "punctuation_only")

    return (False, "")


def normalize_text(text):
    """
    Normalize text for comparison (lowercase, alphanumeric + spaces only).

    Args:
        text: Input text string

    Returns:
        Normalized text string
    """
    # Convert to lowercase and keep only alphanumeric + spaces
    normalized = ''.join(c.lower() if c.isalnum() or c.isspace() else ' ' for c in text)
    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized


def calculate_word_coverage(bucket_text, markdown_text):
    """
    Calculate what percentage of bucket words appear in markdown.

    Args:
        bucket_text: Text from bucket
        markdown_text: Markdown output text

    Returns:
        Float coverage ratio (0.0 to 1.0)
    """
    bucket_normalized = normalize_text(bucket_text)
    markdown_normalized = normalize_text(markdown_text)

    bucket_words = set(bucket_normalized.split())
    markdown_words = set(markdown_normalized.split())

    # Remove common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    bucket_words = bucket_words - stopwords
    markdown_words = markdown_words - stopwords

    if not bucket_words:
        return 0.0

    matched_words = bucket_words & markdown_words
    coverage = len(matched_words) / len(bucket_words)

    return coverage


def calculate_ngram_overlap(bucket_text, markdown_text, n=5):
    """
    Calculate n-gram overlap between bucket and markdown.

    Args:
        bucket_text: Text from bucket
        markdown_text: Markdown output text
        n: N-gram size (default 5 characters)

    Returns:
        Float overlap ratio (0.0 to 1.0)
    """
    bucket_normalized = normalize_text(bucket_text)
    markdown_normalized = normalize_text(markdown_text)

    if len(bucket_normalized) < n:
        # For very short text, use full string
        return 1.0 if bucket_normalized in markdown_normalized else 0.0

    # Generate n-grams from bucket
    bucket_ngrams = set()
    for i in range(len(bucket_normalized) - n + 1):
        bucket_ngrams.add(bucket_normalized[i:i+n])

    if not bucket_ngrams:
        return 0.0

    # Count how many appear in markdown
    matched = sum(1 for ngram in bucket_ngrams if ngram in markdown_normalized)
    overlap = matched / len(bucket_ngrams)

    return overlap


def is_bucket_in_markdown(bucket_text, markdown_text):
    """
    Use hybrid approach to determine if bucket is in markdown.

    Combines multiple methods:
    - Exact substring match (normalized)
    - Fuzzy string matching (rapidfuzz)
    - Word coverage
    - N-gram overlap

    Args:
        bucket_text: Text from bucket
        markdown_text: Markdown output text

    Returns:
        (bool, float, str): (is_included, confidence, method_used)
    """
    bucket_normalized = normalize_text(bucket_text)
    markdown_normalized = normalize_text(markdown_text)

    # Method 1: Exact substring match
    if bucket_normalized in markdown_normalized:
        return (True, 1.0, "exact_match")

    # Method 2: Fuzzy partial ratio (rapidfuzz)
    fuzzy_score = fuzz.partial_ratio(bucket_normalized, markdown_normalized) / 100.0
    if fuzzy_score >= 0.90:
        return (True, fuzzy_score, "fuzzy_match")

    # Method 3: Word coverage
    word_coverage = calculate_word_coverage(bucket_text, markdown_text)
    if word_coverage >= 0.70:  # 70% of meaningful words present
        return (True, word_coverage, "word_coverage")

    # Method 4: N-gram overlap
    ngram_overlap = calculate_ngram_overlap(bucket_text, markdown_text, n=5)
    if ngram_overlap >= 0.65:  # 65% of 5-char n-grams present
        return (True, ngram_overlap, "ngram_overlap")

    # Not found - return max confidence among methods
    max_confidence = max(fuzzy_score, word_coverage, ngram_overlap)
    return (False, max_confidence, "missing")


def find_missing_buckets(stage10_data, stage11_metadata, stage11_markdown):
    """
    Identify buckets that are missing from Stage 11 markdown.

    Uses hybrid matching approach to account for LLM modifications.

    Args:
        stage10_data: Page data from Stage 10 (LLM-ready JSON)
        stage11_metadata: Metadata from Stage 11 with bucket tracking
        stage11_markdown: Markdown text from Stage 11

    Returns:
        Dict with filtered, matched, and missing bucket info
    """
    all_buckets = stage10_data['buckets']
    llm_reported_missing = stage11_metadata.get('missing_buckets', [])

    filtered_buckets = []
    matched_buckets = []
    missing_buckets = []

    for bucket in all_buckets:
        bucket_id = bucket['id']
        texts = bucket.get('texts', [])
        combined_text = ' '.join(texts)

        # Pre-filter invalid buckets
        should_skip, skip_reason = should_skip_bucket(bucket)
        if should_skip:
            filtered_buckets.append({
                'bucket_id': bucket_id,
                'text': combined_text,
                'reason': skip_reason
            })
            continue

        # Check if bucket is in markdown using hybrid approach
        is_included, confidence, method = is_bucket_in_markdown(combined_text, stage11_markdown)

        if is_included:
            matched_buckets.append({
                'bucket_id': bucket_id,
                'text': combined_text,
                'confidence': confidence,
                'method': method
            })
        else:
            missing_buckets.append({
                'bucket_id': bucket_id,
                'text': combined_text,
                'texts': texts,
                'position': bucket.get('position', 'unknown'),
                'width_category': bucket.get('width_category', 'unknown'),
                'y_group_id': bucket.get('y_group_id', -1),
                'confidence_avg': bucket.get('confidence_avg', 0.0),
                'char_count': bucket.get('char_count', 0),
                'word_count': bucket.get('word_count', 0),
                'confidence_missing': 1.0 - confidence,
                'method_tried': method
            })

    return {
        'total_buckets': len(all_buckets),
        'filtered_buckets': filtered_buckets,
        'matched_buckets': matched_buckets,
        'missing_buckets': missing_buckets,
        'llm_reported_missing': llm_reported_missing
    }


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


def format_missing_buckets(missing_buckets):
    """
    Format missing buckets for LLM prompt.

    Args:
        missing_buckets: List of missing bucket dicts

    Returns:
        Formatted string
    """
    formatted = ""
    for bucket in missing_buckets:
        formatted += f"BUCKET {bucket['bucket_id']}:\n"
        formatted += f"  Position: {bucket['position']}, Width: {bucket['width_category']}\n"
        formatted += f"  Y-Group: {bucket['y_group_id']}, OCR Confidence: {bucket['confidence_avg']:.2f}\n"
        formatted += f"  Content:\n"
        for text in bucket['texts']:
            formatted += f"    {text}\n"
        formatted += "\n"

    return formatted


def recover_missing_buckets_with_llm(missing_buckets, stage11_markdown, screenshot_path, client):
    """
    Use GPT-4o-mini to recover missing buckets.

    Args:
        missing_buckets: List of missing bucket dicts
        stage11_markdown: Current markdown from Stage 11
        screenshot_path: Path to page screenshot
        client: OpenAI client instance

    Returns:
        Dict with recovered markdown and analysis
    """
    if not missing_buckets:
        return {
            'markdown': stage11_markdown,
            'buckets_recovered': [],
            'buckets_gibberish': [],
            'recovery_notes': 'No missing buckets to recover'
        }

    # Encode screenshot
    base64_image = encode_image(screenshot_path)

    # Format missing buckets
    missing_text = format_missing_buckets(missing_buckets)

    system_prompt = """You are an expert in OCR post-processing and document reconstruction.

You previously created a markdown document from OCR text blocks (also called 'buckets'). However, some blocks may have been missed.

Your task:
1. **Analyze each missing bucket** to determine if it's OCR gibberish/error or legitimate text
2. **For OCR errors**: Flag as gibberish (examples: repeated characters "aaaaa", random symbols "!@#$%", garbled text "xkcd2019")
3. **For legitimate text**: Determine the correct insertion point in the markdown
4. **Insert legitimate missing text** in the proper reading order location

Use the page screenshot to verify text legitimacy and determine placement.

**Output Format:** Return a JSON object:
```json
{
  "markdown": "... corrected markdown with missing buckets inserted ...",
  "buckets_recovered": [3, 5, 7],
  "buckets_gibberish": [2, 9],
  "recovery_notes": "Brief explanation of changes made"
}
```

- `markdown`: The final corrected markdown
- `buckets_recovered`: List of bucket IDs that were inserted
- `buckets_gibberish`: List of bucket IDs that are OCR errors (not inserted)
- `recovery_notes`: Brief summary of what you did

Provide ONLY valid JSON. Do not include markdown code fences."""

    user_prompt = f"""**Current Markdown:**
```markdown
{stage11_markdown}
```

**Missing Buckets ({len(missing_buckets)} total):**
{missing_text}

**Instructions:**
For each missing bucket, check the screenshot to verify if it's legitimate text or OCR gibberish.
If legitimate, insert it at the correct location in the markdown.
Return the corrected markdown and tracking information in JSON format."""

    # Call OpenAI API with JSON mode to ensure proper LaTeX escaping
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
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
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        recovery_data = json.loads(response_text)
        return {
            'markdown': recovery_data.get('markdown', stage11_markdown),
            'buckets_recovered': recovery_data.get('buckets_recovered', []),
            'buckets_gibberish': recovery_data.get('buckets_gibberish', []),
            'recovery_notes': recovery_data.get('recovery_notes', '')
        }
    except json.JSONDecodeError as e:
        # With JSON mode enabled, this should rarely happen
        # If it does, log the error and fall back to stage 11 markdown
        print(f"    ✗ JSON parsing failed despite JSON mode: {e}")
        print(f"    Falling back to Stage 11 markdown")

        # Save debug output for investigation
        try:
            debug_output_dir = Path(output_dir) if 'output_dir' in locals() else Path('.')
            debug_file = debug_output_dir / f"debug_json_parse_error_{hash(response_text)}.txt"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Error: {e}\n\n")
                f.write(f"Raw response:\n{response_text}")
            print(f"    Debug output saved to: {debug_file}")
        except Exception as debug_error:
            print(f"    Could not save debug output: {debug_error}")

        return {
            'markdown': stage11_markdown,
            'buckets_recovered': [],
            'buckets_gibberish': [],
            'recovery_notes': f'JSON parsing failed with JSON mode enabled: {e}'
        }


def process_page(page_num, stage10_dir, stage11_dir, screenshots_dir, output_dir, client):
    """
    Process a single page: detect and recover missing buckets.

    Args:
        page_num: Page number
        stage10_dir: Directory with Stage 10 LLM-ready JSON files
        stage11_dir: Directory with Stage 11 output
        screenshots_dir: Directory with screenshots
        output_dir: Directory to save final output
        client: OpenAI client instance

    Returns:
        Dict with processing results
    """
    stage10_dir = Path(stage10_dir)
    stage11_dir = Path(stage11_dir)
    screenshots_dir = Path(screenshots_dir)
    output_dir = Path(output_dir)

    # Load Stage 10 data
    stage10_file = stage10_dir / f"page_{page_num}_llm_ready.json"
    if not stage10_file.exists():
        print(f"  ✗ Stage 10 file not found: {stage10_file}")
        return None

    with open(stage10_file, 'r', encoding='utf-8') as f:
        stage10_data = json.load(f)

    # Load Stage 11 metadata
    stage11_metadata_file = stage11_dir / f"page_{page_num}_metadata.json"
    if not stage11_metadata_file.exists():
        print(f"  ✗ Stage 11 metadata not found: {stage11_metadata_file}")
        return None

    with open(stage11_metadata_file, 'r', encoding='utf-8') as f:
        stage11_metadata = json.load(f)

    # Load Stage 11 markdown
    stage11_markdown_file = stage11_dir / f"page_{page_num}_reordered.md"
    if not stage11_markdown_file.exists():
        print(f"  ✗ Stage 11 markdown not found: {stage11_markdown_file}")
        return None

    with open(stage11_markdown_file, 'r', encoding='utf-8') as f:
        stage11_markdown = f.read()

    # Find screenshot
    screenshot_file = None
    screenshot_candidate = screenshots_dir / f"page_{page_num}.png"
    if screenshot_candidate.exists():
        screenshot_file = screenshot_candidate
    else:
        screenshot_candidates = list(screenshots_dir.glob(f"page_{page_num}_*.png"))
        if screenshot_candidates:
            screenshot_file = screenshot_candidates[0]

    if not screenshot_file or not screenshot_file.exists():
        print(f"  ✗ Screenshot not found for page {page_num}")
        return None

    print(f"  Total buckets: {stage10_data['total_buckets']}")

    # Find missing buckets using hybrid matching
    analysis = find_missing_buckets(stage10_data, stage11_metadata, stage11_markdown)

    print(f"  Filtered: {len(analysis['filtered_buckets'])} (invalid)")
    print(f"  Matched: {len(analysis['matched_buckets'])} (found in markdown)")
    print(f"  Missing: {len(analysis['missing_buckets'])} (need recovery)")

    if not analysis['missing_buckets']:
        print(f"  ✓ No missing buckets - using Stage 11 markdown as final")

        # Copy Stage 11 markdown to final output
        final_markdown_file = output_dir / f"page_{page_num}_final.md"
        with open(final_markdown_file, 'w', encoding='utf-8') as f:
            f.write(stage11_markdown)

        # Save analysis report
        report_file = output_dir / f"page_{page_num}_recovery_report.json"
        report = {
            'page_number': page_num,
            'analysis': analysis,
            'recovery': {
                'buckets_recovered': [],
                'buckets_gibberish': [],
                'recovery_notes': 'No missing buckets'
            }
        }
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return {
            'page_number': page_num,
            'missing_count': 0,
            'recovered_count': 0,
            'gibberish_count': 0
        }

    # Recover missing buckets with LLM
    print(f"  Sending {len(analysis['missing_buckets'])} missing buckets to GPT-4o-mini...")
    recovery = recover_missing_buckets_with_llm(
        analysis['missing_buckets'],
        stage11_markdown,
        screenshot_file,
        client
    )

    print(f"  ✓ Recovered: {len(recovery['buckets_recovered'])} buckets")
    print(f"  ✓ Gibberish: {len(recovery['buckets_gibberish'])} buckets")

    # Save final markdown
    final_markdown_file = output_dir / f"page_{page_num}_final.md"
    with open(final_markdown_file, 'w', encoding='utf-8') as f:
        f.write(recovery['markdown'])

    # Save recovery report
    report_file = output_dir / f"page_{page_num}_recovery_report.json"
    report = {
        'page_number': page_num,
        'analysis': analysis,
        'recovery': recovery
    }
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return {
        'page_number': page_num,
        'missing_count': len(analysis['missing_buckets']),
        'recovered_count': len(recovery['buckets_recovered']),
        'gibberish_count': len(recovery['buckets_gibberish']),
        'recovery_notes': recovery['recovery_notes']
    }


def process_all_pages(stage10_dir, stage11_dir, screenshots_dir, output_dir):
    """
    Process all pages: detect and recover missing buckets.

    Args:
        stage10_dir: Directory with Stage 10 LLM-ready JSON files
        stage11_dir: Directory with Stage 11 output
        screenshots_dir: Directory with screenshots
        output_dir: Directory to save final output

    Returns:
        Dict with overall statistics
    """
    stage10_dir = Path(stage10_dir)
    stage11_dir = Path(stage11_dir)
    screenshots_dir = Path(screenshots_dir)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize OpenAI client
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    # Find all Stage 11 metadata files to determine which pages to process
    metadata_files = sorted(stage11_dir.glob('page_*_metadata.json'))

    if not metadata_files:
        print(f"No Stage 11 metadata files found in {stage11_dir}")
        return {
            'total_pages': 0,
            'pages': []
        }

    print(f"Found {len(metadata_files)} page(s) to process")
    print()

    page_results = []
    total_missing = 0
    total_recovered = 0
    total_gibberish = 0

    for metadata_file in metadata_files:
        # Extract page number from filename
        page_num = metadata_file.stem.replace('_metadata', '').replace('page_', '')

        print(f"Processing: Page {page_num}")

        try:
            result = process_page(page_num, stage10_dir, stage11_dir, screenshots_dir, output_dir, client)
            if result:
                page_results.append(result)
                total_missing += result['missing_count']
                total_recovered += result['recovered_count']
                total_gibberish += result['gibberish_count']

                print(f"  ✓ Final markdown: page_{page_num}_final.md")
                print()
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()
            continue

    return {
        'total_pages': len(page_results),
        'total_missing': total_missing,
        'total_recovered': total_recovered,
        'total_gibberish': total_gibberish,
        'pages': page_results
    }


def main():
    """Main entry point."""
    # Set UTF-8 encoding for console output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description='Stage 12: Bucket Recovery - Detect and recover missing buckets'
    )
    parser.add_argument(
        '--stage10_dir',
        type=str,
        required=True,
        help='Input directory with Stage 10 LLM-ready JSON files'
    )
    parser.add_argument(
        '--stage11_dir',
        type=str,
        required=True,
        help='Input directory with Stage 11 output (markdown + metadata)'
    )
    parser.add_argument(
        '--screenshots_dir',
        type=str,
        required=True,
        help='Input directory with screenshots from Stage 1'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for final markdown files'
    )

    args = parser.parse_args()

    print("="*80)
    print("STAGE 12: Bucket Recovery")
    print("="*80)
    print(f"Stage 10 directory: {args.stage10_dir}")
    print(f"Stage 11 directory: {args.stage11_dir}")
    print(f"Screenshots directory: {args.screenshots_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    results = process_all_pages(
        args.stage10_dir,
        args.stage11_dir,
        args.screenshots_dir,
        args.output_dir
    )

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total pages processed: {results['total_pages']}")
    print(f"Total missing buckets: {results['total_missing']}")
    print(f"Total recovered: {results['total_recovered']}")
    print(f"Total gibberish: {results['total_gibberish']}")
    print()

    if results['total_pages'] > 0:
        print("Per-page results:")
        for page_result in results['pages']:
            status = "✓" if page_result['missing_count'] == 0 else f"⚠ {page_result['recovered_count']}/{page_result['missing_count']} recovered"
            print(f"  Page {page_result['page_number']}: {status}")
        print()

    print("Bucket recovery complete!")
    print()


if __name__ == "__main__":
    main()
