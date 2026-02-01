"""
Stage 8: Horizontal Bucket Sort

Groups vertical buckets into horizontal buckets based on vertical proximity and horizontal alignment.
Each vertical bucket (from Stage 7) represents text that is horizontally aligned.
This stage stacks them vertically into reading-order groups.

Input:  Vertical bucket results from Stage 7 (vertical_bucket_results/)
        Format: page_1_buckets.json, page_2_buckets.json, etc.
Output: Horizontal buckets (horizontal_bucket_results/)
        Format: page_1_horizontal_buckets.json, page_2_horizontal_buckets.json, etc.
"""

from pathlib import Path
from datetime import datetime
import json


def calculate_avg_block_height(vertical_bucket):
    """
    Calculate average height of all blocks in a vertical bucket.

    Args:
        vertical_bucket: Vertical bucket dict with 'blocks' list

    Returns:
        float: Average height of blocks
    """
    blocks = vertical_bucket['blocks']
    if not blocks:
        return 50  # Default fallback

    total_height = sum(block.get('height', 50) for block in blocks)
    return total_height / len(blocks)


def calculate_avg_char_width(vertical_bucket):
    """
    Calculate average character width of all blocks in a vertical bucket.

    Args:
        vertical_bucket: Vertical bucket dict with 'blocks' list

    Returns:
        float: Average character width
    """
    blocks = vertical_bucket['blocks']
    if not blocks:
        return 20  # Default fallback

    total_char_width = sum(block.get('character_width', 20) for block in blocks)
    return total_char_width / len(blocks)


def should_add_to_horizontal_bucket(horizontal_bucket, current_vb):
    """
    Check if current vertical bucket should be added to a horizontal bucket
    by comparing it with the last vertical bucket in that horizontal bucket.

    Algorithm:
    1. Check vertical gap against average height threshold
    2. If gap is small enough, check horizontal alignment (start_x, mid_x, end_x)
    3. If any alignment matches, return True

    Args:
        horizontal_bucket: List of vertical buckets in this horizontal bucket
        current_vb: Current vertical bucket to check

    Returns:
        bool: True if should add to this bucket
    """
    # Get last vertical bucket in the horizontal bucket
    ref_vb = horizontal_bucket[-1]

    # Calculate average heights
    avg_height_ref = calculate_avg_block_height(ref_vb)
    avg_height_current = calculate_avg_block_height(current_vb)
    height_threshold = (avg_height_ref + avg_height_current) / 2

    # Calculate vertical gap
    vertical_gap = current_vb['start_y'] - ref_vb['end_y']

    # If vertical gap is too large, don't add to this bucket
    if vertical_gap >= height_threshold:
        return False

    # Vertical gap is small enough - now check horizontal alignment
    # Calculate average character widths
    avg_char_width_ref = calculate_avg_char_width(ref_vb)
    avg_char_width_current = calculate_avg_char_width(current_vb)
    char_width_threshold = (avg_char_width_ref + avg_char_width_current) / 2

    # Check start_x alignment
    start_x_diff = abs(current_vb['start_x'] - ref_vb['start_x'])
    if start_x_diff < char_width_threshold:
        return True

    # Check mid_x alignment
    mid_x_diff = abs(current_vb['mid_x'] - ref_vb['mid_x'])
    if mid_x_diff < char_width_threshold:
        return True

    # Check end_x alignment
    end_x_diff = abs(current_vb['end_x'] - ref_vb['end_x'])
    if end_x_diff < char_width_threshold:
        return True

    # No alignment matched - don't add to this bucket
    return False


def create_horizontal_buckets(vertical_buckets):
    """
    Group vertical buckets into horizontal buckets based on vertical proximity
    and horizontal alignment.

    Algorithm:
    1. Start with first vertical bucket in first horizontal bucket
    2. For each subsequent vertical bucket:
       - Check each existing horizontal bucket (starting from first)
       - Compare with last vertical bucket in that horizontal bucket
       - If conditions match, add to that bucket and break
       - If no match found, create new horizontal bucket

    Args:
        vertical_buckets: List of vertical bucket dicts from Stage 7

    Returns:
        List of horizontal buckets, where each horizontal bucket is a list of vertical buckets
    """
    if not vertical_buckets:
        return []

    # Initialize with first vertical bucket in first horizontal bucket
    horizontal_buckets = [[vertical_buckets[0]]]

    # Process remaining vertical buckets
    for i in range(1, len(vertical_buckets)):
        current_vb = vertical_buckets[i]
        found_match = False

        # Check each existing horizontal bucket
        for h_bucket in horizontal_buckets:
            if should_add_to_horizontal_bucket(h_bucket, current_vb):
                # Add to this horizontal bucket
                h_bucket.append(current_vb)
                found_match = True
                break  # Exit once added to a bucket

        # If no match found, create new horizontal bucket
        if not found_match:
            horizontal_buckets.append([current_vb])

    return horizontal_buckets


def normalize_bucket_coordinates(bucket_data, page_width=2550, page_height=3300):
    """
    Add normalized coordinates (0-100 range) to each horizontal bucket.

    Normalizes coordinates relative to page dimensions (not content bounds).

    Args:
        bucket_data: List of horizontal bucket dicts
        page_width: Page width in pixels (default: 2550 for 300 DPI A4)
        page_height: Page height in pixels (default: 3300 for 300 DPI A4)

    Returns:
        List of horizontal buckets with added normalized edge fields
    """
    if not bucket_data:
        return bucket_data

    # Avoid division by zero
    if page_width == 0:
        page_width = 2550
    if page_height == 0:
        page_height = 3300

    # Add normalized coordinates to each bucket
    for bucket in bucket_data:
        # Normalize to 0-100 range (percentage) as integers
        # Using absolute page dimensions, not content bounds
        bucket['left_edge'] = int(round((bucket['start_x'] / page_width) * 100))
        bucket['right_edge'] = int(round((bucket['end_x'] / page_width) * 100))
        bucket['top_edge'] = int(round((bucket['start_y'] / page_height) * 100))
        bucket['bottom_edge'] = int(round((bucket['end_y'] / page_height) * 100))

    return bucket_data


def process_page_horizontal_buckets(page_data):
    """
    Process horizontal buckets for a single page.

    Args:
        page_data: Page data dict with vertical buckets from Stage 7

    Returns:
        Dict with horizontal bucketed vertical buckets
    """
    vertical_buckets = page_data['buckets']

    # Create horizontal buckets
    horizontal_buckets = create_horizontal_buckets(vertical_buckets)

    # Create bucket data structure with statistics
    bucket_data = []
    total_vertical_buckets = 0
    total_text_blocks = 0

    for idx, h_bucket in enumerate(horizontal_buckets):
        # Count vertical buckets and text blocks in this horizontal bucket
        num_vertical_buckets = len(h_bucket)
        num_text_blocks = sum(vb['num_blocks'] for vb in h_bucket)

        total_vertical_buckets += num_vertical_buckets
        total_text_blocks += num_text_blocks

        # Calculate horizontal bucket bounding box
        bucket_start_x = min(vb['start_x'] for vb in h_bucket)
        bucket_end_x = max(vb['end_x'] for vb in h_bucket)
        bucket_start_y = min(vb['start_y'] for vb in h_bucket)
        bucket_end_y = max(vb['end_y'] for vb in h_bucket)

        bucket_mid_x = (bucket_start_x + bucket_end_x) / 2
        bucket_mid_y = (bucket_start_y + bucket_end_y) / 2

        # Get the minimum mid_y_x from all vertical buckets for sorting
        bucket_min_mid_y_x = min(vb['min_mid_y_x'] for vb in h_bucket)

        bucket_info = {
            'horizontal_bucket_id': idx,
            'num_vertical_buckets': num_vertical_buckets,
            'num_text_blocks': num_text_blocks,
            'start_x': bucket_start_x,
            'end_x': bucket_end_x,
            'start_y': bucket_start_y,
            'end_y': bucket_end_y,
            'mid_x': bucket_mid_x,
            'mid_y': bucket_mid_y,
            'min_mid_y_x': bucket_min_mid_y_x,
            'width': bucket_end_x - bucket_start_x,
            'height': bucket_end_y - bucket_start_y,
            'vertical_buckets': h_bucket
        }
        bucket_data.append(bucket_info)

    # Sort horizontal buckets by min_mid_y_x (reading order)
    bucket_data = sorted(bucket_data, key=lambda b: b['min_mid_y_x'])

    # Add normalized coordinates (0-100 range)
    bucket_data = normalize_bucket_coordinates(bucket_data)

    # Prepare output
    output = {
        'page_number': page_data['page_number'],
        'total_text_blocks': total_text_blocks,
        'total_vertical_buckets': total_vertical_buckets,
        'total_horizontal_buckets': len(horizontal_buckets),
        'horizontal_buckets': bucket_data
    }

    # Propagate adaptive_thresholds if available
    if 'adaptive_thresholds' in page_data:
        output['adaptive_thresholds'] = page_data['adaptive_thresholds']

    return output


def process_all_pages(input_dir, output_dir):
    """
    Process horizontal buckets for all pages.

    Args:
        input_dir: Path to directory containing vertical bucket JSON files (from Stage 7)
        output_dir: Path to save horizontal bucket results

    Returns:
        Dict with processing results
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all vertical bucket JSON files
    bucket_files = sorted(input_dir.glob('page_*_buckets.json'))

    if not bucket_files:
        raise FileNotFoundError(f"No vertical bucket JSON files found in: {input_dir}")

    print(f"Creating horizontal buckets for {len(bucket_files)} pages...")
    print()

    all_page_results = []
    total_text_blocks = 0
    total_vertical_buckets = 0
    total_horizontal_buckets = 0

    # Process each page file
    for bucket_file in bucket_files:
        print(f"Processing {bucket_file.name}...")

        # Load page data
        with open(bucket_file, 'r', encoding='utf-8') as f:
            page_data = json.load(f)

        # Process horizontal buckets
        h_bucket_page = process_page_horizontal_buckets(page_data)
        all_page_results.append(h_bucket_page)

        text_blocks = h_bucket_page['total_text_blocks']
        v_buckets = h_bucket_page['total_vertical_buckets']
        h_buckets = h_bucket_page['total_horizontal_buckets']

        total_text_blocks += text_blocks
        total_vertical_buckets += v_buckets
        total_horizontal_buckets += h_buckets

        # Save individual page horizontal bucket result
        page_num = h_bucket_page['page_number']
        h_bucket_filename = f"page_{page_num}_horizontal_buckets.json"
        h_bucket_path = output_dir / h_bucket_filename

        with open(h_bucket_path, 'w', encoding='utf-8') as f:
            json.dump(h_bucket_page, f, indent=2, ensure_ascii=False)

        print(f"  ✓ {v_buckets} vertical buckets → {h_buckets} horizontal buckets")
        print(f"  ✓ Total text blocks: {text_blocks}")
        print(f"  ✓ Saved: {h_bucket_filename}")
        print()

    # Save combined metadata
    # Try to get PDF name from bucket_metadata.json if it exists
    pdf_name = "unknown"
    bucket_metadata_path = input_dir / 'bucket_metadata.json'
    if bucket_metadata_path.exists():
        with open(bucket_metadata_path, 'r', encoding='utf-8') as f:
            bucket_metadata = json.load(f)
            pdf_name = bucket_metadata.get('pdf_name', 'unknown')

    combined_metadata = {
        'pdf_name': pdf_name,
        'total_pages': len(all_page_results),
        'total_text_blocks': total_text_blocks,
        'total_vertical_buckets': total_vertical_buckets,
        'total_horizontal_buckets': total_horizontal_buckets,
        'avg_vertical_buckets_per_horizontal_bucket': total_vertical_buckets / total_horizontal_buckets if total_horizontal_buckets > 0 else 0,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_results
    }

    metadata_path = output_dir / 'horizontal_bucket_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(combined_metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path}")

    return {
        'total_pages': len(all_page_results),
        'total_text_blocks': total_text_blocks,
        'total_vertical_buckets': total_vertical_buckets,
        'total_horizontal_buckets': total_horizontal_buckets,
        'average_vertical_buckets_per_horizontal_bucket': total_vertical_buckets / total_horizontal_buckets if total_horizontal_buckets > 0 else 0,
        'metadata': combined_metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.

    Usage:
        python stage_8_horizontal_buckets.py <vertical_bucket_dir> [output_dir]
    """
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Usage: python stage_8_horizontal_buckets.py <vertical_bucket_dir> [output_dir]")
        print("\nExample:")
        print("  python stage_8_horizontal_buckets.py vertical_bucket_results/ horizontal_bucket_results/")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "horizontal_bucket_results"

    # Process horizontal buckets
    results = process_all_pages(input_dir, output_dir)

    print("\n✓ Success! Horizontal bucket creation complete:")
    print(f"  Total text blocks: {results['total_text_blocks']}")
    print(f"  Total vertical buckets: {results['total_vertical_buckets']}")
    print(f"  Total horizontal buckets: {results['total_horizontal_buckets']}")
    print(f"  Avg vertical buckets per horizontal bucket: {results['metadata']['avg_vertical_buckets_per_horizontal_bucket']:.2f}")
