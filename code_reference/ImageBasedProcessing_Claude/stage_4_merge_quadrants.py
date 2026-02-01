"""
Stage 4: Merge Quadrants

Merges OCR results from all 4 quadrants into a single sorted list per page.

Input:  OCR results from Stage 3 (ocr_results/)
Output: Merged text blocks sorted by mid_y_x (merged_results/)
        Format: page_1_merged.json, page_2_merged.json, etc.
"""

from pathlib import Path
from datetime import datetime
import json


def scale_coordinates_to_original(blocks):
    """
    Scale coordinates back to original screenshot size.

    Since quadrants were upscaled 2x for OCR, we need to divide all
    coordinates by 2 to get back to the original screenshot coordinate space.

    Args:
        blocks: List of text blocks with coordinates

    Returns:
        List of blocks with scaled coordinates
    """
    for block in blocks:
        # Scale all coordinate values by 0.5
        block['start_x'] = round(block['start_x'] / 2)
        block['end_x'] = round(block['end_x'] / 2)
        block['mid_x'] = round(block['mid_x'] / 2)
        block['start_y'] = round(block['start_y'] / 2)
        block['end_y'] = round(block['end_y'] / 2)
        block['mid_y'] = round(block['mid_y'] / 2)
        block['height'] = round(block['height'] / 2)

        # Recalculate mid_y_x with scaled coordinates
        block['mid_y_x'] = block['mid_y'] + block['start_x'] / 50

    return blocks


def merge_page_quadrants(page_ocr_data, min_confidence=0.3):
    """
    Merge all quadrants for a single page and sort by mid_y_x.
    Filters out blocks with confidence below the threshold.

    Args:
        page_ocr_data: OCR data for a page (from ocr_metadata.json)
        min_confidence: Minimum confidence threshold (default: 0.3)

    Returns:
        Dict with merged and sorted text blocks
    """
    page_num = page_ocr_data['page_number']
    all_blocks = []
    total_blocks_before_filter = 0
    total_blocks_filtered = 0

    # Collect blocks from all quadrants
    for quadrant_data in page_ocr_data['quadrants']:
        quadrant_name = quadrant_data['quadrant_name']
        blocks = quadrant_data['blocks']
        total_blocks_before_filter += len(blocks)

        # Filter blocks by confidence and add quadrant source
        filtered_blocks = []
        for block in blocks:
            block['source_quadrant'] = quadrant_name
            
            # Filter by confidence threshold
            confidence = block.get('confidence', 0)
            if confidence >= min_confidence:
                filtered_blocks.append(block)
            else:
                total_blocks_filtered += 1

        all_blocks.extend(filtered_blocks)
        print(f"    {quadrant_name}: {len(filtered_blocks)} blocks (filtered {len(blocks) - len(filtered_blocks)})")

    # Sort by mid_y_x (ascending)
    all_blocks.sort(key=lambda b: b['mid_y_x'])

    # Scale coordinates back to original screenshot size (halve all coordinates)
    all_blocks = scale_coordinates_to_original(all_blocks)

    print(f"  ✓ Total blocks merged: {len(all_blocks)} (filtered out {total_blocks_filtered} low-confidence blocks)")
    print(f"  ✓ Coordinates scaled back to original screenshot size")

    return {
        'page_number': page_num,
        'total_blocks': len(all_blocks),
        'blocks': all_blocks,
        'blocks_filtered': total_blocks_filtered
    }


def merge_all_pages(ocr_dir, output_dir, min_confidence=0.3):
    """
    Merge quadrants for all pages.

    Args:
        ocr_dir: Path to OCR results directory (stage_3_OCR/)
        output_dir: Path to save merged results
        min_confidence: Minimum confidence threshold for filtering (default: 0.3)

    Returns:
        Dict with processing results
    """
    ocr_dir = Path(ocr_dir)
    output_dir = Path(output_dir)

    # Load OCR metadata
    metadata_path = ocr_dir / 'ocr_metadata.json'
    if not metadata_path.exists():
        raise FileNotFoundError(f"OCR metadata not found: {metadata_path}")

    with open(metadata_path, 'r', encoding='utf-8') as f:
        ocr_metadata = json.load(f)

    print(f"Merging quadrants for {len(ocr_metadata['pages'])} pages...")
    print(f"Confidence threshold: {min_confidence} (blocks below this will be filtered out)")
    print()

    all_page_results = []
    total_blocks = 0
    total_filtered = 0

    # Process each page
    for page_data in ocr_metadata['pages']:
        page_num = page_data['page_number']
        print(f"Processing page {page_num}...")

        # Merge quadrants with confidence filtering
        page_result = merge_page_quadrants(page_data, min_confidence=min_confidence)
        all_page_results.append(page_result)
        total_blocks += page_result['total_blocks']
        total_filtered += page_result.get('blocks_filtered', 0)

        # Save individual page merged result
        merged_filename = f"page_{page_num}_merged.json"
        merged_path = output_dir / merged_filename
        with open(merged_path, 'w', encoding='utf-8') as f:
            json.dump(page_result, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved: {merged_filename}")
        print()

    # Save combined metadata
    combined_metadata = {
        'pdf_name': ocr_metadata['pdf_name'],
        'total_pages': len(all_page_results),
        'total_blocks': total_blocks,
        'total_blocks_filtered': total_filtered,
        'min_confidence_threshold': min_confidence,
        'coordinates_scaled': True,
        'coordinate_space': 'original_screenshot',
        'scaling_note': 'All coordinates scaled by 0.5 to match original screenshot size (quadrants were 2x upscaled for OCR)',
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_results
    }

    metadata_path = output_dir / 'merged_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(combined_metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path}")
    print(f"✓ Total blocks filtered: {total_filtered}")

    return {
        'total_pages': len(all_page_results),
        'total_blocks': total_blocks,
        'total_blocks_filtered': total_filtered,
        'metadata': combined_metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.

    Usage:
        python stage_4_merge_quadrants.py <ocr_dir> [output_dir]
    """
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Usage: python stage_4_merge_quadrants.py <ocr_dir> [output_dir]")
        print("\nExample:")
        print("  python stage_4_merge_quadrants.py ocr_test/ merged_test/")
        sys.exit(1)

    ocr_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "merged_test"

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Merge quadrants
    results = merge_all_pages(ocr_dir, output_dir)

    print(f"\n✓ Success! {results['total_blocks']} text blocks merged across {results['total_pages']} pages")

