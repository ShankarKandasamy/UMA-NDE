"""
Stage 6: Horizontal Merge

Recursively merges text blocks that belong on the same line based on vertical
alignment and horizontal gap analysis.

Input:  Metrics results from Stage 5 (metrics_test_int/)
        Format: page_1_metrics.json, page_2_metrics.json, etc.
Output: Horizontally merged blocks (horizontal_merge_results/)
        Format: page_1_horizontal_merged.json, page_2_horizontal_merged.json, etc.
"""

from pathlib import Path
from datetime import datetime
import json
from stage_5_metrics import calculate_block_metrics


def merge_two_blocks(block1, block2):
    """
    Merge two blocks into one, combining their text and updating spatial metrics.
    
    Args:
        block1: First block dict
        block2: Second block dict
    
    Returns:
        Merged block dict
    """
    # Determine which block comes first horizontally (smaller start_x)
    if block1['start_x'] <= block2['start_x']:
        first_block = block1
        second_block = block2
    else:
        first_block = block2
        second_block = block1
    
    # Merge text with a space between blocks
    merged_text = first_block['text'] + ' ' + second_block['text']
    
    # Calculate new bounding box (encompassing both blocks)
    new_start_x = min(first_block['start_x'], second_block['start_x'])
    new_end_x = max(first_block['end_x'], second_block['end_x'])
    new_start_y = min(first_block['start_y'], second_block['start_y'])
    new_end_y = max(first_block['end_y'], second_block['end_y'])
    
    # Calculate new midpoints
    new_mid_x = (new_start_x + new_end_x) / 2
    new_mid_y = (new_start_y + new_end_y) / 2
    # Calculate mid_y_x: mid_y + start_x / 50 (matching existing formula)
    new_mid_y_x = new_mid_y + new_start_x / 50
    
    # Calculate new dimensions
    new_width = new_end_x - new_start_x
    new_height = new_end_y - new_start_y
    
    # Combine character and word counts (add 1 for the space)
    new_char_count = first_block['char_count'] + second_block['char_count'] + 1
    new_word_count = first_block['word_count'] + second_block['word_count']
    
    # Calculate new character width
    if new_char_count > 0:
        new_character_width = int(round(new_width / new_char_count))
    else:
        new_character_width = first_block.get('character_width') or second_block.get('character_width')
    
    # Use maximum confidence (or average if preferred)
    new_confidence = max(first_block.get('confidence', 0), second_block.get('confidence', 0))
    
    # Keep source quadrant from first block (or combine if needed)
    new_source_quadrant = first_block.get('source_quadrant', 'unknown')
    
    # Create merged block
    merged_block = {
        'text': merged_text,
        'start_x': int(round(new_start_x)),
        'end_x': int(round(new_end_x)),
        'start_y': int(round(new_start_y)),
        'end_y': int(round(new_end_y)),
        'mid_x': int(round(new_mid_x)),
        'mid_y': int(round(new_mid_y)),
        'mid_y_x': int(round(new_mid_y_x)),
        'height': int(round(new_height)),
        'confidence': new_confidence,
        'char_count': new_char_count,
        'word_count': new_word_count,
        'source_quadrant': new_source_quadrant,
        'width': int(round(new_width)),
        'character_width': new_character_width,
        # Reset relationship metrics (will be recalculated if needed)
        'prev_mid_y_diff': None,
        'prev_horizontal_gap': None,
        'prev_vertical_gap': None,
        'prev_overlap_x': None,
        'prev_overlap_y': None,
        'prev_distance': None
    }
    
    return merged_block


def should_merge_blocks(ref_block, current_block, thresholds=None):
    """
    Check if two blocks should be merged based on vertical alignment and horizontal gap.

    Uses adaptive thresholds if provided, otherwise falls back to legacy heuristics.

    Args:
        ref_block: Reference block (the one we're comparing against)
        current_block: Current block to check
        thresholds: Dict with adaptive thresholds (from Stage 5), or None for legacy behavior

    Returns:
        Tuple (should_merge: bool, gap: float)
    """
    # Use adaptive thresholds if available
    if thresholds:
        vertical_tolerance = thresholds.get('vertical_merge_tolerance', 50)

        # NEW: Use local pairwise char width average instead of global median
        # This allows headers/captions with larger fonts to have more permissive thresholds
        ref_char_width = ref_block.get('character_width')
        if ref_char_width is None or ref_char_width == 0:
            ref_char_width = 36  # Fallback to typical median

        current_char_width = current_block.get('character_width')
        if current_char_width is None or current_char_width == 0:
            current_char_width = 36  # Fallback to typical median

        # Calculate local median from the two candidate blocks
        local_median_char_width = (ref_char_width + current_char_width) / 2
        horizontal_gap_threshold = local_median_char_width * 3.0
    else:
        # Legacy fallback: Use character widths (original behavior)
        ref_char_width = ref_block.get('character_width')
        if ref_char_width is None or ref_char_width == 0:
            ref_char_width = 50

        current_char_width = current_block.get('character_width')
        if current_char_width is None or current_char_width == 0:
            current_char_width = 50

        # Use minimum for conservative merging
        vertical_tolerance = min(ref_char_width, current_char_width)
        horizontal_gap_threshold = 2 * min(ref_char_width, current_char_width)

    # Check vertical alignment: |mid_y_current - mid_y_reference| < vertical_tolerance
    mid_y_diff = abs(current_block['mid_y'] - ref_block['mid_y'])
    if mid_y_diff >= vertical_tolerance:
        return False, None

    # Calculate horizontal gap
    if current_block['start_x'] < ref_block['start_x']:
        # Current block is to the left of reference
        gap = ref_block['start_x'] - current_block['end_x']
    else:
        # Current block is to the right of reference
        gap = current_block['start_x'] - ref_block['end_x']

    # Check if gap is small enough
    if gap < horizontal_gap_threshold:
        return True, gap

    return False, None


def merge_blocks_recursive(blocks, thresholds=None):
    """
    Optimized: Merge blocks that belong on the same line without full restarts.

    Algorithm:
    - Starting at the top block (i=0)
    - For the next 20 blocks, check if they should be merged
    - If merge occurs, re-check current position against new lookahead window
    - If no merge found, advance to next position (i++)
    - Continue until all blocks processed

    Complexity: O(N * K) where K=20, effectively O(N) linear time
    (Original algorithm was O(N²) due to full restarts)

    Args:
        blocks: List of block dictionaries (should be sorted by mid_y_x)
        thresholds: Dict with adaptive thresholds (from Stage 5), or None for legacy behavior

    Returns:
        List of merged blocks
    """
    if not blocks or len(blocks) < 2:
        return blocks

    # Make a copy to avoid modifying the original
    merged_blocks = blocks.copy()
    max_lookahead = 20

    i = 0

    # Process blocks from top to bottom
    while i < len(merged_blocks):
        ref_block = merged_blocks[i]

        # Keep trying to merge current block until no more merges possible
        merge_found = True
        while merge_found:
            merge_found = False

            # Check next max_lookahead blocks
            for j in range(i + 1, min(i + 1 + max_lookahead, len(merged_blocks))):
                current_block = merged_blocks[j]

                # Check if blocks should be merged (with adaptive thresholds)
                should_merge, gap = should_merge_blocks(ref_block, current_block, thresholds)

                if should_merge:
                    # Merge the blocks
                    merged_block = merge_two_blocks(ref_block, current_block)

                    # Replace reference block with merged block
                    merged_blocks[i] = merged_block
                    ref_block = merged_block  # Update reference for next iteration

                    # Remove the current block
                    merged_blocks.pop(j)

                    merge_found = True
                    break  # Restart lookahead window from current position

        # No more merges for current block, advance to next
        i += 1

    return merged_blocks


def merge_horizontal_for_page(page_data):
    """
    Perform horizontal merging for a single page.

    Args:
        page_data: Page data dict with blocks from metrics JSON

    Returns:
        Dict with horizontally merged blocks
    """
    blocks = page_data['blocks']

    # Get adaptive thresholds (if available from Stage 5)
    thresholds = page_data.get('adaptive_thresholds', None)

    # Ensure blocks are sorted by mid_y_x (top to bottom, left to right)
    blocks = sorted(blocks, key=lambda b: b['mid_y_x'])

    # Perform recursive horizontal merge with adaptive thresholds
    merged_blocks = merge_blocks_recursive(blocks, thresholds)

    # Re-sort after merging (in case mid_y_x changed)
    merged_blocks = sorted(merged_blocks, key=lambda b: b['mid_y_x'])

    # Recalculate relationship metrics after merging
    merged_blocks = calculate_block_metrics(merged_blocks)

    return {
        'page_number': page_data['page_number'],
        'total_blocks': len(merged_blocks),
        'adaptive_thresholds': thresholds,  # Pass through for Stage 7
        'blocks': merged_blocks
    }


def merge_horizontal_for_all_pages(metrics_dir, output_dir):
    """
    Perform horizontal merging for all pages.
    
    Args:
        metrics_dir: Path to directory containing metrics JSON files
        output_dir: Path to save horizontally merged results
    
    Returns:
        Dict with processing results
    """
    metrics_dir = Path(metrics_dir)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all metrics JSON files (page_*_metrics.json)
    metrics_files = sorted(metrics_dir.glob('page_*_metrics.json'))
    
    if not metrics_files:
        raise FileNotFoundError(f"No metrics JSON files found in: {metrics_dir}")
    
    print(f"Performing horizontal merge for {len(metrics_files)} pages...")
    print()
    
    all_page_results = []
    total_blocks_before = 0
    total_blocks_after = 0
    
    # Process each metrics page file
    for metrics_file in metrics_files:
        print(f"Processing {metrics_file.name}...")
        
        # Load metrics page data
        with open(metrics_file, 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        blocks_before = page_data['total_blocks']
        total_blocks_before += blocks_before
        
        # Perform horizontal merge
        merged_page = merge_horizontal_for_page(page_data)
        all_page_results.append(merged_page)
        
        blocks_after = merged_page['total_blocks']
        total_blocks_after += blocks_after
        
        reduction = blocks_before - blocks_after
        reduction_pct = (reduction / blocks_before * 100) if blocks_before > 0 else 0
        
        # Save individual page horizontally merged result
        page_num = merged_page['page_number']
        merged_filename = f"page_{page_num}_horizontal_merged.json"
        merged_path = output_dir / merged_filename
        
        with open(merged_path, 'w', encoding='utf-8') as f:
            json.dump(merged_page, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Blocks: {blocks_before} → {blocks_after} (reduced by {reduction}, {reduction_pct:.1f}%)")
        print(f"  ✓ Saved: {merged_filename}")
        print()
    
    # Save combined metadata
    # Try to get PDF name from metrics_metadata.json if it exists
    pdf_name = "unknown"
    metrics_metadata_path = metrics_dir / 'metrics_metadata.json'
    if metrics_metadata_path.exists():
        with open(metrics_metadata_path, 'r', encoding='utf-8') as f:
            metrics_metadata = json.load(f)
            pdf_name = metrics_metadata.get('pdf_name', 'unknown')
    
    combined_metadata = {
        'pdf_name': pdf_name,
        'total_pages': len(all_page_results),
        'total_blocks_before': total_blocks_before,
        'total_blocks_after': total_blocks_after,
        'total_blocks_reduced': total_blocks_before - total_blocks_after,
        'reduction_percentage': ((total_blocks_before - total_blocks_after) / total_blocks_before * 100) if total_blocks_before > 0 else 0,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_results
    }
    
    metadata_path = output_dir / 'horizontal_merge_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(combined_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metadata saved: {metadata_path}")
    
    return {
        'total_pages': len(all_page_results),
        'total_blocks_before': total_blocks_before,
        'total_blocks_after': total_blocks_after,
        'total_blocks_reduced': total_blocks_before - total_blocks_after,
        'metadata': combined_metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.
    
    Usage:
        python stage_6_horizontal_merge.py <metrics_dir> [output_dir]
    """
    import sys
    import io
    
    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python stage_6_horizontal_merge.py <metrics_dir> [output_dir]")
        print("\nExample:")
        print("  python stage_6_horizontal_merge.py metrics_test_int/ horizontal_merge_test/")
        sys.exit(1)
    
    metrics_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "horizontal_merge_test"
    
    # Perform horizontal merge
    results = merge_horizontal_for_all_pages(metrics_dir, output_dir)
    
    print("\n✓ Success! Horizontal merge complete:")
    print(f"  Blocks before: {results['total_blocks_before']}")
    print(f"  Blocks after: {results['total_blocks_after']}")
    print(f"  Blocks reduced: {results['total_blocks_reduced']}")
    print(f"  Reduction: {((results['total_blocks_reduced'] / results['total_blocks_before']) * 100):.1f}%")

