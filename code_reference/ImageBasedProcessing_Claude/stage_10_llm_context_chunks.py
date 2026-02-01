"""
Stage 10: LLM-Ready Simplified JSON

Converts Stage 9 vertical stacked bucket JSON into simplified format for LLM refinement.
Reduces verbosity while preserving essential spatial and quality metadata.

Input: Stage 9 vertical stacked bucket JSON files (e.g., page_1_vertical_stacked.json)
Output: Simplified JSON files ready for LLM (e.g., page_1_llm_ready.json)

Simplifications:
- Flattens nested vertical_buckets → blocks into texts array
- Derives position hints (left/center/right)
- Derives width categories (narrow/medium/wide)
- Calculates y_group_id for same-row grouping
- Aggregates confidence, char_count, word_count
- Uses normalized edge coordinates from Stage 8/9 (already 0-100 scale)
- Removes redundant coordinate fields and page dimensions

Usage:
    python stage_10_llm_context_chunks.py --input_dir <vertical_stacked_dir> --output_dir <llm_ready_dir>
"""

import json
import argparse
from pathlib import Path


def derive_position(left_edge, right_edge):
    """
    Derive horizontal position category based on normalized edge coordinates.

    Args:
        left_edge: Left edge coordinate (0-100 scale)
        right_edge: Right edge coordinate (0-100 scale)

    Returns:
        str: "left" | "center" | "right"
    """
    mid_x = (left_edge + right_edge) / 2

    if mid_x < 33:
        return "left"
    elif mid_x < 67:
        return "center"
    else:
        return "right"


def derive_width_category(left_edge, right_edge):
    """
    Derive width category based on normalized edge coordinates.

    Args:
        left_edge: Left edge coordinate (0-100 scale)
        right_edge: Right edge coordinate (0-100 scale)

    Returns:
        str: "narrow" | "medium" | "wide"
    """
    width = right_edge - left_edge

    if width < 40:
        return "narrow"
    elif width < 70:
        return "medium"
    else:
        return "wide"


def calculate_y_groups(horizontal_buckets, tolerance=5):
    """
    Group horizontal buckets by Y position (same-row grouping).
    Buckets within ±tolerance percentage are considered in the same row.

    Args:
        horizontal_buckets: List of horizontal bucket dicts
        tolerance: Y-position tolerance in percentage (0-100 scale)

    Returns:
        Dict mapping bucket index to y_group_id
    """
    if not horizontal_buckets:
        return {}

    # Sort by top_edge to process top-to-bottom
    sorted_indices = sorted(
        range(len(horizontal_buckets)),
        key=lambda i: horizontal_buckets[i]['top_edge']
    )

    y_groups = {}
    current_group_id = 0
    current_group_y = None

    for idx in sorted_indices:
        bucket = horizontal_buckets[idx]
        bucket_y = bucket['top_edge']

        if current_group_y is None:
            # First bucket
            current_group_y = bucket_y
            y_groups[idx] = current_group_id
        elif abs(bucket_y - current_group_y) <= tolerance:
            # Within tolerance of current group
            y_groups[idx] = current_group_id
        else:
            # Start new group
            current_group_id += 1
            current_group_y = bucket_y
            y_groups[idx] = current_group_id

    return y_groups


def flatten_texts_and_calculate_stats(horizontal_bucket):
    """
    Extract texts from nested vertical_buckets → blocks structure
    and calculate aggregate statistics.

    Args:
        horizontal_bucket: Horizontal bucket dict with vertical_buckets

    Returns:
        Tuple of (texts_list, confidence_avg, char_count, word_count)
    """
    texts = []
    confidences = []
    total_chars = 0
    total_words = 0

    vertical_buckets = horizontal_bucket.get('vertical_buckets', [])

    for vb in vertical_buckets:
        blocks = vb.get('blocks', [])

        for block in blocks:
            text = block.get('text', '').strip()
            if text:
                texts.append(text)
                confidences.append(block.get('confidence', 1.0))
                total_chars += block.get('char_count', len(text))
                total_words += block.get('word_count', len(text.split()))

    # Calculate average confidence
    confidence_avg = sum(confidences) / len(confidences) if confidences else 0.0

    return texts, confidence_avg, total_chars, total_words


def simplify_bucket(horizontal_bucket, bucket_index, y_group_id):
    """
    Convert a horizontal bucket to simplified format using normalized coordinates.

    Args:
        horizontal_bucket: Horizontal bucket dict from Stage 9
        bucket_index: Index of this bucket in the page
        y_group_id: Y-group assignment for this bucket

    Returns:
        Dict with simplified bucket format (coordinates already normalized to 0-100)
    """
    # Extract normalized edge coordinates (already 0-100 scale from Stage 8/9)
    left_edge = horizontal_bucket.get('left_edge', 0)
    right_edge = horizontal_bucket.get('right_edge', 100)
    top_edge = horizontal_bucket.get('top_edge', 0)
    bottom_edge = horizontal_bucket.get('bottom_edge', 100)

    # Derive position and width category (using normalized coordinates)
    position = derive_position(left_edge, right_edge)
    width_category = derive_width_category(left_edge, right_edge)

    # Flatten texts and calculate stats
    texts, confidence_avg, char_count, word_count = flatten_texts_and_calculate_stats(horizontal_bucket)

    return {
        'id': bucket_index,
        'left_edge': left_edge,
        'top_edge': top_edge,
        'right_edge': right_edge,
        'bottom_edge': bottom_edge,
        'position': position,
        'width_category': width_category,
        'y_group_id': y_group_id,
        'confidence_avg': round(confidence_avg, 2),
        'char_count': char_count,
        'word_count': word_count,
        'texts': texts
    }


def process_page_file(input_file, output_dir, last_bucket_from_prev_page=None):
    """
    Process a single page's vertical stacked JSON file and convert to simplified format.

    Args:
        input_file: Path to vertical stacked JSON file
        output_dir: Directory to save simplified JSON
        last_bucket_from_prev_page: Last bucket from previous page (for context), or None for page 1

    Returns:
        Dict with processing stats and simplified buckets for next iteration
    """
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    page_number = data.get('page_number', 'unknown')
    horizontal_buckets = data.get('horizontal_buckets', [])

    # Calculate y_group assignments (using normalized coordinates)
    y_group_mapping = calculate_y_groups(horizontal_buckets, tolerance=5)

    # Convert each bucket to simplified format
    simplified_buckets = []

    for idx, h_bucket in enumerate(horizontal_buckets):
        y_group_id = y_group_mapping.get(idx, 0)
        simplified_bucket = simplify_bucket(h_bucket, idx, y_group_id)
        simplified_buckets.append(simplified_bucket)

    # Build output structure
    output_data = {
        'page_number': page_number,
        'total_buckets': len(simplified_buckets),
        'last_bucket_previous_page': last_bucket_from_prev_page,  # NEW: context from previous page
        'buckets': simplified_buckets
    }

    # Write output file
    output_file = output_dir / input_file.name.replace('_vertical_stacked.json', '_llm_ready.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Calculate stats
    total_chars = sum(b['char_count'] for b in simplified_buckets)
    total_words = sum(b['word_count'] for b in simplified_buckets)
    total_texts = sum(len(b['texts']) for b in simplified_buckets)

    return {
        'page_number': page_number,
        'input_file': str(input_file),
        'output_file': str(output_file),
        'num_buckets': len(simplified_buckets),
        'num_texts': total_texts,
        'total_chars': total_chars,
        'total_words': total_words,
        'simplified_buckets': simplified_buckets  # Return for next iteration
    }


def process_all_pages(input_dir, output_dir):
    """
    Process all vertical stacked JSON files in the input directory.
    Includes last bucket from previous page for cross-page context.

    Args:
        input_dir: Directory containing vertical stacked JSON files from Stage 9
        output_dir: Directory to save simplified JSON files

    Returns:
        Dict with overall statistics
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all vertical stacked JSON files and sort by page number
    bucket_files = sorted(
        input_dir.glob('*_vertical_stacked.json'),
        key=lambda f: int(f.stem.split('_')[1])  # Extract page number from "page_N_vertical_stacked"
    )

    if not bucket_files:
        print(f"No vertical stacked JSON files found in {input_dir}")
        return {
            'total_pages': 0,
            'total_buckets': 0,
            'total_texts': 0,
            'pages': []
        }

    print(f"Found {len(bucket_files)} vertical stacked file(s)")
    print()

    page_results = []
    total_buckets = 0
    total_texts = 0
    total_chars = 0
    total_words = 0

    # Track last bucket from previous page
    last_bucket_prev_page = None

    for bucket_file in bucket_files:
        print(f"Processing: {bucket_file.name}")
        result = process_page_file(bucket_file, output_dir, last_bucket_prev_page)
        page_results.append(result)

        total_buckets += result['num_buckets']
        total_texts += result['num_texts']
        total_chars += result['total_chars']
        total_words += result['total_words']

        print(f"  Page {result['page_number']}: {result['num_buckets']} buckets, {result['num_texts']} texts")
        print(f"  Content: {result['total_chars']:,} chars, {result['total_words']:,} words")
        print(f"  Output: {result['output_file']}")
        print()

        # Save last bucket for next page's context
        if result['simplified_buckets']:
            last_bucket_prev_page = result['simplified_buckets'][-1]
        else:
            last_bucket_prev_page = None

    return {
        'total_pages': len(bucket_files),
        'total_buckets': total_buckets,
        'total_texts': total_texts,
        'total_chars': total_chars,
        'total_words': total_words,
        'pages': page_results
    }


def main():
    parser = argparse.ArgumentParser(
        description='Stage 10: Convert vertical stacked bucket JSON to simplified LLM-ready format'
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        required=True,
        help='Input directory containing vertical stacked JSON files from Stage 9'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for simplified LLM-ready JSON files'
    )

    args = parser.parse_args()

    print("="*80)
    print("STAGE 10: LLM-Ready Simplified JSON")
    print("="*80)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    results = process_all_pages(args.input_dir, args.output_dir)

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total pages processed: {results['total_pages']}")
    print(f"Total buckets: {results['total_buckets']}")
    print(f"Total text blocks: {results['total_texts']}")
    print(f"Total characters: {results['total_chars']:,}")
    print(f"Total words: {results['total_words']:,}")
    print()
    print("Simplifications applied:")
    print("  [x] Flattened vertical_buckets -> blocks into texts array")
    print("  [x] Derived position hints (left/center/right)")
    print("  [x] Derived width categories (narrow/medium/wide)")
    print("  [x] Calculated y_group_id for same-row grouping")
    print("  [x] Aggregated confidence, char_count, word_count")
    print("  [x] Used normalized edge coordinates from Stage 9 (0-100 scale)")
    print("  [x] Removed redundant coordinate fields")
    print()
    print("Output files are ready for LLM refinement!")
    print()


if __name__ == '__main__':
    main()
