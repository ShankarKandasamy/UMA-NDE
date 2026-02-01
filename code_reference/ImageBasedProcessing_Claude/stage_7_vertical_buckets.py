"""
Stage 7: Vertical Bucket Sort

Groups text blocks into buckets based on vertical alignment and horizontal proximity.
Uses an iterative approach where elements are compared against the last element
in each existing bucket.

Input:  Horizontally merged results from Stage 6 (horizontal_merge_results/)
        Format: page_1_horizontal_merged.json, page_2_horizontal_merged.json, etc.
Output: Vertically bucketed blocks (vertical_bucket_results/)
        Format: page_1_vertical_buckets.json, page_2_vertical_buckets.json, etc.
"""

from pathlib import Path
from datetime import datetime
import json


def should_add_to_bucket(bucket_last_element, current_element, thresholds=None):
    """
    Check if current element should be added to a bucket by comparing it with
    the last element in that bucket.

    Uses adaptive thresholds if provided, otherwise falls back to legacy heuristics.

    Args:
        bucket_last_element: Last element in the reference bucket
        current_element: Element to check for bucket membership
        thresholds: Dict with adaptive thresholds (from Stage 5), or None for legacy behavior

    Returns:
        bool: True if element should be added to this bucket
    """
    # Use adaptive thresholds if available
    if thresholds:
        vertical_threshold = thresholds.get('vertical_bucket_tolerance', 70)
        horizontal_threshold = thresholds.get('horizontal_bucket_tolerance', 50)
    else:
        # Legacy fallback: Use heights and character widths (original behavior)
        height_ref = bucket_last_element.get('height', 50)
        height_current = current_element.get('height', 50)
        char_width_ref = bucket_last_element.get('character_width', 50)
        char_width_current = current_element.get('character_width', 50)

        # Ensure we don't have zero values
        if height_ref <= 0:
            height_ref = 50
        if height_current <= 0:
            height_current = 50
        if char_width_ref <= 0:
            char_width_ref = 50
        if char_width_current <= 0:
            char_width_current = 50

        vertical_threshold = 1.4 * min(height_ref, height_current)
        horizontal_threshold = min(char_width_ref, char_width_current)

    # Check vertical alignment: mid_y to mid_y distance < vertical_threshold
    mid_y_distance = abs(current_element['mid_y'] - bucket_last_element['mid_y'])

    if mid_y_distance >= vertical_threshold:
        # Not vertically aligned - put in new bucket
        return False

    # Elements are vertically aligned - check horizontal conditions (OR logic)

    # Check start_x difference < 2 * horizontal_threshold
    # (Allow more tolerance for start_x to handle indentation)
    start_x_diff = abs(current_element['start_x'] - bucket_last_element['start_x'])
    if start_x_diff < 2 * horizontal_threshold:
        return True

    # Check mid_x difference < horizontal_threshold
    mid_x_diff = abs(current_element['mid_x'] - bucket_last_element['mid_x'])
    if mid_x_diff < horizontal_threshold:
        return True

    # Check end_x difference < horizontal_threshold
    end_x_diff = abs(current_element['end_x'] - bucket_last_element['end_x'])
    if end_x_diff < horizontal_threshold:
        return True

    # None of the horizontal conditions met - put in new bucket
    return False


def create_buckets(blocks, thresholds=None):
    """
    Group blocks into buckets based on vertical alignment and horizontal proximity.

    Algorithm:
    1. Start with empty buckets list
    2. First element goes in first bucket
    3. For each subsequent element:
       - Compare with last element of each existing bucket
       - If matches criteria, add to that bucket
       - Otherwise create new bucket

    Args:
        blocks: List of block dictionaries
        thresholds: Dict with adaptive thresholds (from Stage 5), or None for legacy behavior

    Returns:
        List of buckets, where each bucket is a list of blocks
    """
    if not blocks:
        return []

    # Initialize buckets with first element
    buckets = [[blocks[0]]]

    # Process remaining elements
    for i in range(1, len(blocks)):
        current_element = blocks[i]
        element_added = False

        # Check each existing bucket
        for bucket in buckets:
            # Get last element in this bucket
            bucket_last = bucket[-1]

            # Check if current element belongs in this bucket (with adaptive thresholds)
            if should_add_to_bucket(bucket_last, current_element, thresholds):
                bucket.append(current_element)
                element_added = True
                break  # Exit once element is added to a bucket

        # If element wasn't added to any bucket, create new bucket
        if not element_added:
            buckets.append([current_element])

    return buckets


def process_page_buckets(page_data):
    """
    Process buckets for a single page.

    Args:
        page_data: Page data dict with blocks from horizontal merge JSON

    Returns:
        Dict with bucketed blocks
    """
    blocks = page_data['blocks']

    # Get adaptive thresholds (if available from Stage 5 via Stage 6)
    thresholds = page_data.get('adaptive_thresholds', None)

    # Ensure blocks are sorted by mid_y_x (top to bottom, left to right)
    blocks = sorted(blocks, key=lambda b: b['mid_y_x'])

    # Create buckets with adaptive thresholds
    buckets = create_buckets(blocks, thresholds)
    
    # Create bucket data structure with statistics
    bucket_data = []
    for idx, bucket in enumerate(buckets):
        # Calculate bucket statistics
        bucket_start_x = min(block['start_x'] for block in bucket)
        bucket_end_x = max(block['end_x'] for block in bucket)
        bucket_start_y = min(block['start_y'] for block in bucket)
        bucket_end_y = max(block['end_y'] for block in bucket)

        # Calculate geometric centers of bounding box
        bucket_mid_x = (bucket_start_x + bucket_end_x) / 2
        bucket_mid_y = (bucket_start_y + bucket_end_y) / 2

        # Calculate min mid_y and min mid_y_x among all blocks in this bucket for sorting
        bucket_min_mid_y = min(block['mid_y'] for block in bucket)
        bucket_min_mid_y_x = min(block['mid_y_x'] for block in bucket)
        
        bucket_info = {
            'bucket_id': idx,
            'num_blocks': len(bucket),
            'start_x': bucket_start_x,
            'end_x': bucket_end_x,
            'start_y': bucket_start_y,
            'end_y': bucket_end_y,
            'mid_y': bucket_mid_y,
            'mid_x': bucket_mid_x,
            'min_mid_y': bucket_min_mid_y,
            'min_mid_y_x': bucket_min_mid_y_x,
            'width': bucket_end_x - bucket_start_x,
            'height': bucket_end_y - bucket_start_y,
            'blocks': bucket
        }
        bucket_data.append(bucket_info)
    
    # Sort buckets by min(mid_y_x) element in each bucket
    bucket_data = sorted(bucket_data, key=lambda b: b['min_mid_y_x'])

    # Prepare output with adaptive thresholds (if available)
    output = {
        'page_number': page_data['page_number'],
        'total_blocks': len(blocks),
        'total_buckets': len(buckets),
        'buckets': bucket_data
    }

    # Propagate adaptive_thresholds from Stage 6 (if available)
    if thresholds:
        output['adaptive_thresholds'] = thresholds

    return output


def process_all_pages(input_dir, output_dir):
    """
    Process buckets for all pages.
    
    Args:
        input_dir: Path to directory containing horizontal merge JSON files
        output_dir: Path to save bucket results
    
    Returns:
        Dict with processing results
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all horizontal merge JSON files
    merge_files = sorted(input_dir.glob('page_*_horizontal_merged.json'))
    
    if not merge_files:
        raise FileNotFoundError(f"No horizontal merge JSON files found in: {input_dir}")
    
    print(f"Creating buckets for {len(merge_files)} pages...")
    print()
    
    all_page_results = []
    total_blocks = 0
    total_buckets = 0
    
    # Process each page file
    for merge_file in merge_files:
        print(f"Processing {merge_file.name}...")
        
        # Load page data
        with open(merge_file, 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        # Process buckets
        bucket_page = process_page_buckets(page_data)
        all_page_results.append(bucket_page)
        
        blocks_count = bucket_page['total_blocks']
        buckets_count = bucket_page['total_buckets']
        total_blocks += blocks_count
        total_buckets += buckets_count
        
        avg_blocks_per_bucket = blocks_count / buckets_count if buckets_count > 0 else 0
        
        # Save individual page bucket result
        page_num = bucket_page['page_number']
        bucket_filename = f"page_{page_num}_buckets.json"
        bucket_path = output_dir / bucket_filename
        
        with open(bucket_path, 'w', encoding='utf-8') as f:
            json.dump(bucket_page, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Blocks: {blocks_count} → {buckets_count} buckets")
        print(f"  ✓ Average blocks per bucket: {avg_blocks_per_bucket:.2f}")
        print(f"  ✓ Saved: {bucket_filename}")
        print()
    
    # Save combined metadata
    # Try to get PDF name from horizontal_merge_metadata.json if it exists
    pdf_name = "unknown"
    merge_metadata_path = input_dir / 'horizontal_merge_metadata.json'
    if merge_metadata_path.exists():
        with open(merge_metadata_path, 'r', encoding='utf-8') as f:
            merge_metadata = json.load(f)
            pdf_name = merge_metadata.get('pdf_name', 'unknown')
    
    avg_total_blocks_per_bucket = total_blocks / total_buckets if total_buckets > 0 else 0
    
    combined_metadata = {
        'pdf_name': pdf_name,
        'total_pages': len(all_page_results),
        'total_blocks': total_blocks,
        'total_buckets': total_buckets,
        'average_blocks_per_bucket': avg_total_blocks_per_bucket,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_results
    }
    
    metadata_path = output_dir / 'bucket_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(combined_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metadata saved: {metadata_path}")
    
    return {
        'total_pages': len(all_page_results),
        'total_blocks': total_blocks,
        'total_buckets': total_buckets,
        'average_blocks_per_bucket': avg_total_blocks_per_bucket,
        'metadata': combined_metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.
    
    Usage:
        python stage_7_buckets.py <horizontal_merge_dir> [output_dir]
    """
    import sys
    import io
    
    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python stage_7_buckets.py <horizontal_merge_dir> [output_dir]")
        print("\nExample:")
        print("  python stage_7_buckets.py horizontal_merge_results/ bucket_results/")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "bucket_results"
    
    # Process buckets
    results = process_all_pages(input_dir, output_dir)
    
    print("\n✓ Success! Bucket creation complete:")
    print(f"  Total blocks: {results['total_blocks']}")
    print(f"  Total buckets: {results['total_buckets']}")
    print(f"  Average blocks per bucket: {results['average_blocks_per_bucket']:.2f}")
