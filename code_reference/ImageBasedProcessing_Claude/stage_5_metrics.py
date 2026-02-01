"""
Stage 5: Calculate Spatial Metrics

Calculates spatial metrics and relationships for merged blocks.

Input:  Merged page results from Stage 4 (merged_results/)
        Format: page_1_merged.json, page_2_merged.json, etc.
Output: Enhanced blocks with spatial metrics (metrics_results/)
        Format: page_1_metrics.json, page_2_metrics.json, etc.
"""

from pathlib import Path
from datetime import datetime
import json
import math
import numpy as np


def calculate_adaptive_thresholds(blocks):
    """
    Calculate adaptive thresholds from page statistics.

    Analyzes the actual spacing patterns in the document to determine
    optimal thresholds for horizontal merging (Stage 6) and bucket sorting (Stage 7).

    Args:
        blocks: List of block dictionaries with spatial metrics

    Returns:
        Dict with adaptive threshold values:
        {
            'vertical_merge_tolerance': float,      # Stage 6: max vertical distance for merging
            'horizontal_merge_gap': float,          # Stage 6: max horizontal gap for merging
            'vertical_bucket_tolerance': float,     # Stage 7: max vertical distance for bucketing
            'horizontal_bucket_tolerance': float,   # Stage 7: max horizontal distance for bucketing
            'metadata': {
                'median_height': float,
                'median_vertical_spacing': float,
                'median_char_width': float,
                'line_spacing_ratio': float,
                'total_blocks_analyzed': int
            }
        }
    """
    if not blocks or len(blocks) < 10:
        # Not enough blocks for reliable statistics - use defaults
        return {
            'vertical_merge_tolerance': 50,
            'horizontal_merge_gap': 100,
            'vertical_bucket_tolerance': 70,
            'horizontal_bucket_tolerance': 50,
            'metadata': {
                'median_height': 50,
                'median_vertical_spacing': 75,
                'median_char_width': 50,
                'line_spacing_ratio': 1.5,
                'total_blocks_analyzed': len(blocks),
                'used_defaults': True
            }
        }

    # Extract statistics from blocks
    vertical_diffs = []
    heights = []
    char_widths = []

    for block in blocks:
        # Vertical spacing between consecutive blocks
        if block.get('prev_mid_y_diff') is not None and block['prev_mid_y_diff'] > 0:
            vertical_diffs.append(block['prev_mid_y_diff'])

        # Block heights (font sizes)
        if block.get('height') is not None and block['height'] > 0:
            heights.append(block['height'])

        # Character widths
        if block.get('character_width') is not None and block['character_width'] > 0:
            char_widths.append(block['character_width'])

    # Calculate robust statistics (percentiles avoid outliers)
    median_height = np.median(heights) if heights else 50
    p25_vertical_spacing = np.percentile(vertical_diffs, 25) if vertical_diffs else median_height
    median_vertical_spacing = np.median(vertical_diffs) if vertical_diffs else median_height * 1.5
    median_char_width = np.median(char_widths) if char_widths else 50

    # Calculate line spacing ratio (how much space between lines relative to text height)
    line_spacing_ratio = median_vertical_spacing / median_height if median_height > 0 else 1.5

    # Calculate adaptive thresholds
    thresholds = {
        # Stage 6: Horizontal merge
        # Vertical tolerance: 80% of tight line spacing (p25)
        # Ensures blocks on same line are merged even with slight vertical misalignment
        'vertical_merge_tolerance': max(p25_vertical_spacing * 0.8, median_height * 0.5),

        # Horizontal gap: 2.5x character width (typical space + small gap)
        # Allows merging words separated by normal word spacing
        'horizontal_merge_gap': median_char_width * 2.5,

        # Stage 7: Bucket sort
        # Vertical tolerance: Use whichever is larger to handle both tight and normal spacing
        # - For normal spacing (1.2x-1.5x): median_vertical_spacing * 1.2 works well
        # - For tight spacing (<1.0x): median_height * 1.4 prevents over-segmentation
        'vertical_bucket_tolerance': max(
            median_vertical_spacing * 1.2,  # Spacing-based (works for normal docs)
            median_height * 1.4              # Height-based (works for tight-spaced docs)
        ),

        # Horizontal tolerance: 1.5x character width
        # Allows grouping blocks with similar horizontal alignment
        'horizontal_bucket_tolerance': median_char_width * 1.5,

        # Metadata for debugging and analysis
        'metadata': {
            'median_height': float(median_height),
            'median_vertical_spacing': float(median_vertical_spacing),
            'median_char_width': float(median_char_width),
            'line_spacing_ratio': float(line_spacing_ratio),
            'total_blocks_analyzed': len(blocks),
            'used_defaults': False
        }
    }

    return thresholds


def calculate_block_metrics(blocks):
    """
    Calculate spatial metrics for blocks, comparing each block with the previous one.
    
    Args:
        blocks: List of block dictionaries sorted by mid_y_x
    
    Returns:
        List of blocks with added spatial metrics
    """
    if not blocks:
        return blocks
    
    enhanced_blocks = []
    
    for i, block in enumerate(blocks):
        # Basic geometric properties (for each block)
        width = block['end_x'] - block['start_x']
        block['width'] = int(round(width))
        
        # Character width: average width per character
        char_count = block.get('char_count', 0)
        if char_count > 0:
            block['character_width'] = int(round(width / char_count))
        else:
            block['character_width'] = None  # Avoid division by zero
        
        # Adjacent block relationships (comparing with previous block)
        if i > 0:
            prev_block = blocks[i - 1]
            
            # mid_y to mid_y difference between adjacent blocks
            mid_y_diff = block['mid_y'] - prev_block['mid_y']
            block['prev_mid_y_diff'] = int(round(mid_y_diff))
            
            # end_x (previous block) to start_x (next block) between adjacent blocks
            # This is the horizontal gap: start_x of current - end_x of previous
            horizontal_gap = block['start_x'] - prev_block['end_x']
            block['prev_horizontal_gap'] = int(round(horizontal_gap))
            
            # vertical_gap: start_y of next - end_y of current
            # When comparing adjacent blocks: start_y of current - end_y of previous
            vertical_gap = block['start_y'] - prev_block['end_y']
            block['prev_vertical_gap'] = int(round(vertical_gap))
            
            # overlap_x: horizontal overlap amount
            # Positive if overlapping, negative if gap (same as horizontal_gap but with different interpretation)
            # Overlap = min(end_x, prev_end_x) - max(start_x, prev_start_x)
            # If negative, it's a gap; if positive, it's overlap
            overlap_x = min(block['end_x'], prev_block['end_x']) - max(block['start_x'], prev_block['start_x'])
            block['prev_overlap_x'] = int(round(overlap_x))
            
            # overlap_y: vertical overlap amount
            # Positive if overlapping, negative if gap
            overlap_y = min(block['end_y'], prev_block['end_y']) - max(block['start_y'], prev_block['start_y'])
            block['prev_overlap_y'] = int(round(overlap_y))
            
            # distance: Euclidean distance between block centers
            mid_x_diff = block['mid_x'] - prev_block['mid_x']
            distance = math.sqrt((mid_x_diff ** 2) + (mid_y_diff ** 2))
            block['prev_distance'] = int(round(distance))
        else:
            # First block - no previous relationships
            block['prev_mid_y_diff'] = None
            block['prev_horizontal_gap'] = None
            block['prev_vertical_gap'] = None
            block['prev_overlap_x'] = None
            block['prev_overlap_y'] = None
            block['prev_distance'] = None
        
        # Convert all coordinate and dimension fields to integers (except confidence)
        block['start_x'] = int(round(block['start_x']))
        block['end_x'] = int(round(block['end_x']))
        block['start_y'] = int(round(block['start_y']))
        block['end_y'] = int(round(block['end_y']))
        block['mid_x'] = int(round(block['mid_x']))
        block['mid_y'] = int(round(block['mid_y']))
        block['mid_y_x'] = int(round(block['mid_y_x']))
        block['height'] = int(round(block['height']))
        # char_count and word_count should already be integers, but ensure they are
        block['char_count'] = int(block['char_count'])
        block['word_count'] = int(block['word_count'])
        # confidence remains as float - do not convert
        
        enhanced_blocks.append(block)
    
    return enhanced_blocks


def calculate_metrics_for_page(page_data):
    """
    Calculate metrics for a single page.

    Args:
        page_data: Page data dict with blocks from merged JSON

    Returns:
        Dict with enhanced blocks and adaptive thresholds
    """
    blocks = page_data['blocks']
    enhanced_blocks = calculate_block_metrics(blocks)

    # Calculate adaptive thresholds based on page statistics
    adaptive_thresholds = calculate_adaptive_thresholds(enhanced_blocks)

    return {
        'page_number': page_data['page_number'],
        'total_blocks': page_data['total_blocks'],
        'adaptive_thresholds': adaptive_thresholds,  # NEW: Adaptive thresholds for Stages 6-7
        'blocks': enhanced_blocks
    }


def calculate_metrics_for_all_pages(merged_dir, output_dir):
    """
    Calculate metrics for all merged pages.
    
    Args:
        merged_dir: Path to directory containing merged JSON files
        output_dir: Path to save metrics results
    
    Returns:
        Dict with processing results
    """
    merged_dir = Path(merged_dir)
    output_dir = Path(output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all merged JSON files (page_*_merged.json)
    merged_files = sorted(merged_dir.glob('page_*_merged.json'))
    
    if not merged_files:
        raise FileNotFoundError(f"No merged JSON files found in: {merged_dir}")
    
    print(f"Calculating metrics for {len(merged_files)} pages...")
    print()
    
    all_page_results = []
    total_blocks = 0
    
    # Process each merged page file
    for merged_file in merged_files:
        print(f"Processing {merged_file.name}...")
        
        # Load merged page data
        with open(merged_file, 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        # Calculate metrics
        enhanced_page = calculate_metrics_for_page(page_data)
        all_page_results.append(enhanced_page)
        total_blocks += enhanced_page['total_blocks']
        
        # Save individual page metrics result
        page_num = enhanced_page['page_number']
        metrics_filename = f"page_{page_num}_metrics.json"
        metrics_path = output_dir / metrics_filename
        
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_page, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Saved: {metrics_filename}")
        print()
    
    # Save combined metadata
    # Try to get PDF name from merged_metadata.json if it exists
    pdf_name = "unknown"
    merged_metadata_path = merged_dir / 'merged_metadata.json'
    if merged_metadata_path.exists():
        with open(merged_metadata_path, 'r', encoding='utf-8') as f:
            merged_metadata = json.load(f)
            pdf_name = merged_metadata.get('pdf_name', 'unknown')
    
    combined_metadata = {
        'pdf_name': pdf_name,
        'total_pages': len(all_page_results),
        'total_blocks': total_blocks,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_results
    }
    
    metadata_path = output_dir / 'metrics_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(combined_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metadata saved: {metadata_path}")
    
    return {
        'total_pages': len(all_page_results),
        'total_blocks': total_blocks,
        'metadata': combined_metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.
    
    Usage:
        python stage_5_metrics.py <merged_dir> [output_dir]
    """
    import sys
    import io
    
    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    if len(sys.argv) < 2:
        print("Usage: python stage_5_metrics.py <merged_dir> [output_dir]")
        print("\nExample:")
        print("  python stage_5_metrics.py merged_test/ metrics_test/")
        sys.exit(1)
    
    merged_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "metrics_test"
    
    # Calculate metrics
    results = calculate_metrics_for_all_pages(merged_dir, output_dir)
    
    print(f"\n✓ Success! Metrics calculated for {results['total_blocks']} blocks across {results['total_pages']} pages")

