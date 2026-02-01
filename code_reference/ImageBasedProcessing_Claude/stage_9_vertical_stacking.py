"""
Stage 9: Vertical Column Stacking Sort

Takes horizontal buckets from Stage 8 and performs a vertical column stacking sort.
This groups vertically-aligned buckets that should be read top-to-bottom.

Uses normalized coordinates (0-100 range) from Stage 8 for resolution-independent processing.

Algorithm:
1. Start with first horizontal bucket as "ref"
2. For each remaining bucket below it as "current":
   - If vertically aligned (left OR right edge within 3%) AND
     vertically close (gap <= 3%)
   - Move "current" to be immediately after "ref" in the list
3. Move to next bucket in the newly-reordered list as new "ref"
4. Repeat until all buckets have been "ref" once

Thresholds:
- Alignment threshold: 3% (left or right edge alignment)
- Vertical gap threshold: 3% (vertical proximity)

Input:  Stage 8 horizontal buckets with normalized coordinates (e.g., page_N_horizontal_buckets.json)
Output: JSON file with re-ordered buckets in vertical column reading order

Usage:
    python stage_9_vertical_stacking.py --input_dir <horizontal_bucket_dir> --output_dir <output_dir>
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def is_vertically_aligned(ref_bucket, current_bucket, threshold=3.0):
    """
    Check if two buckets are vertically aligned using normalized coordinates.

    Buckets are aligned if left OR right edge is within threshold percentage.

    Args:
        ref_bucket: Reference bucket dict with normalized edge coordinates
        current_bucket: Current bucket dict with normalized edge coordinates
        threshold: Alignment threshold in percentage (default: 3.0%)

    Returns:
        bool: True if vertically aligned
    """
    left_diff = abs(current_bucket['left_edge'] - ref_bucket['left_edge'])
    right_diff = abs(current_bucket['right_edge'] - ref_bucket['right_edge'])

    return left_diff <= threshold or right_diff <= threshold


def is_vertically_close(ref_bucket, current_bucket, threshold=3.0):
    """
    Check if current bucket is vertically close to ref bucket using normalized coordinates.

    Args:
        ref_bucket: Reference bucket dict with normalized edge coordinates
        current_bucket: Current bucket dict with normalized edge coordinates
        threshold: Vertical gap threshold in percentage (default: 3.0%)

    Returns:
        bool: True if vertically close
    """
    vertical_gap = current_bucket['top_edge'] - ref_bucket['bottom_edge']

    return vertical_gap <= threshold


def vertical_column_stack_sort(horizontal_buckets):
    """
    Sort horizontal buckets using vertical column stacking algorithm.

    Groups vertically-aligned buckets that should be read top-to-bottom.

    Args:
        horizontal_buckets: List of horizontal bucket dicts from Stage 8

    Returns:
        List of re-ordered horizontal bucket dicts
    """
    if not horizontal_buckets:
        return []

    # Make a copy to avoid modifying original list
    buckets = horizontal_buckets.copy()

    # Track which buckets have been "ref"
    ref_index = 0

    while ref_index < len(buckets):
        ref_bucket = buckets[ref_index]

        # Check all remaining buckets below current ref
        current_index = ref_index + 1

        while current_index < len(buckets):
            current_bucket = buckets[current_index]

            # Check if vertically aligned AND vertically close
            if (is_vertically_aligned(ref_bucket, current_bucket) and
                is_vertically_close(ref_bucket, current_bucket)):

                # Move current bucket to be immediately after ref
                # Remove from current position
                buckets.pop(current_index)

                # Insert immediately after ref
                buckets.insert(ref_index + 1, current_bucket)

                # Update ref to the newly moved bucket
                ref_index += 1
                ref_bucket = buckets[ref_index]

                # Continue checking from the next position
                current_index = ref_index + 1
            else:
                # Move to next bucket
                current_index += 1

        # Move to next bucket in the list as new ref
        ref_index += 1

    return buckets


def process_page(page_data):
    """
    Process a single page with vertical column stacking sort.

    Args:
        page_data: Page data dict from Stage 8 horizontal buckets

    Returns:
        Dict with re-ordered horizontal buckets
    """
    horizontal_buckets = page_data['horizontal_buckets']

    # Apply vertical column stacking sort
    reordered_buckets = vertical_column_stack_sort(horizontal_buckets)

    # Update bucket IDs to reflect new order
    for idx, bucket in enumerate(reordered_buckets):
        bucket['horizontal_bucket_id'] = idx

    # Create output structure
    output = {
        'page_number': page_data['page_number'],
        'total_text_blocks': page_data['total_text_blocks'],
        'total_vertical_buckets': page_data['total_vertical_buckets'],
        'total_horizontal_buckets': page_data['total_horizontal_buckets'],
        'horizontal_buckets': reordered_buckets
    }

    # Propagate adaptive_thresholds if available
    if 'adaptive_thresholds' in page_data:
        output['adaptive_thresholds'] = page_data['adaptive_thresholds']

    return output


def process_all_pages(input_dir, output_dir):
    """
    Process all pages with vertical column stacking sort.

    Args:
        input_dir: Directory containing horizontal bucket JSON files from Stage 8
        output_dir: Directory to save re-ordered results

    Returns:
        Dict with processing statistics
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all horizontal bucket JSON files
    bucket_files = sorted(input_dir.glob('page_*_horizontal_buckets.json'))

    if not bucket_files:
        raise FileNotFoundError(f"No horizontal bucket JSON files found in: {input_dir}")

    print(f"Processing {len(bucket_files)} pages with vertical column stacking sort...")
    print()

    all_page_results = []
    total_pages = 0

    for bucket_file in bucket_files:
        print(f"Processing {bucket_file.name}...")

        # Load page data
        with open(bucket_file, 'r', encoding='utf-8') as f:
            page_data = json.load(f)

        # Process page
        reordered_page = process_page(page_data)
        all_page_results.append(reordered_page)

        # Save individual page result
        page_num = reordered_page['page_number']
        output_filename = f"page_{page_num}_vertical_stacked.json"
        output_path = output_dir / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reordered_page, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Re-ordered {reordered_page['total_horizontal_buckets']} horizontal buckets")
        print(f"  ✓ Saved: {output_filename}")
        print()

        total_pages += 1

    # Save metadata
    metadata_input_path = input_dir / 'horizontal_bucket_metadata.json'
    pdf_name = "unknown"
    if metadata_input_path.exists():
        with open(metadata_input_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            pdf_name = metadata.get('pdf_name', 'unknown')

    combined_metadata = {
        'pdf_name': pdf_name,
        'total_pages': total_pages,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_results
    }

    metadata_path = output_dir / 'vertical_stacked_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(combined_metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path.name}")
    print()

    return {
        'total_pages': total_pages,
        'metadata': combined_metadata
    }


def main():
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description='Stage 9: Vertical Column Stacking Sort'
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        required=True,
        help='Directory containing horizontal bucket JSON files from Stage 8'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for re-ordered results'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("STAGE 9: Vertical Column Stacking Sort")
    print("=" * 80)
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print()

    results = process_all_pages(args.input_dir, args.output_dir)

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total pages processed: {results['total_pages']}")
    print()
    print("Vertical column stacking sort complete!")
    print()


if __name__ == '__main__':
    main()
