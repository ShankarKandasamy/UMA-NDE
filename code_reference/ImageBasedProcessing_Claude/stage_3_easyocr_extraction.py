"""
Stage 3: EasyOCR Extraction

Runs EasyOCR on each quadrant image to extract text with bounding boxes.

Input:  Quadrant PNG images from Stage 2 (quadrants/)
Output: JSON files with text + bbox coordinates (ocr_results/)
        Format: page_1_top_left_ocr.json, page_1_top_right_ocr.json, etc.
"""

import easyocr
import numpy as np
from PIL import Image
from pathlib import Path
from datetime import datetime
import json


def run_easyocr_on_quadrant(image_path, reader):
    """
    Run EasyOCR on a single quadrant image.

    Args:
        image_path: Path to quadrant PNG
        reader: EasyOCR Reader instance

    Returns:
        List of text blocks with bbox, text, and confidence
    """
    # Load image
    img = Image.open(image_path)
    img_array = np.array(img)

    # Run EasyOCR
    results = reader.readtext(img_array)

    # Format results
    ocr_blocks = []
    for bbox, text, confidence in results:
        # EasyOCR returns bbox as [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        # Convert to standard format with integers
        bbox_clean = [[int(x), int(y)] for x, y in bbox]

        # Extract simplified bounding box coordinates
        # start_x: leftmost x (left edge)
        # end_x: rightmost x (right edge)
        # start_y: topmost y (top edge)
        # end_y: bottommost y (bottom edge)
        # mid_x: horizontal center
        # mid_y: vertical center
        all_x = [point[0] for point in bbox_clean]
        all_y = [point[1] for point in bbox_clean]

        start_x = min(all_x)
        end_x = max(all_x)
        start_y = min(all_y)
        end_y = max(all_y)
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        height = end_y - start_y

        # Calculate composite sort key (mid_y with start_x tiebreaker)
        mid_y_rounded = round(mid_y)
        start_x_rounded = round(start_x)
        mid_y_x = mid_y_rounded + start_x_rounded / 50

        ocr_blocks.append({
            'text': text,
            'start_x': start_x_rounded,
            'end_x': round(end_x),
            'start_y': round(start_y),
            'end_y': round(end_y),
            'mid_x': round(mid_x),
            'mid_y': mid_y_rounded,
            'mid_y_x': mid_y_x,
            'height': round(height),
            'confidence': float(confidence),
            'char_count': len(text),
            'word_count': len(text.split())
        })

    return ocr_blocks


def adjust_right_quadrant_x_coordinates(quadrant_result, left_quadrant_width):
    """
    Adjust x-coordinates for right quadrants to create continuous coordinate space.

    Adds left_quadrant_width to all x-coordinates in right quadrants (top_right, bottom_right)
    to position them relative to the full page width.

    Args:
        quadrant_result: Quadrant result dict with blocks
        left_quadrant_width: Width of left quadrant image (e.g., 2550 for upscaled quadrant)
    """
    # Adjust per-block x-coordinates
    for block in quadrant_result['blocks']:
        block['start_x'] += left_quadrant_width
        block['end_x'] += left_quadrant_width
        block['mid_x'] += left_quadrant_width
        # Recalculate mid_y_x with updated start_x
        block['mid_y_x'] = block['mid_y'] + block['start_x'] / 50

    # Adjust quadrant-level x-bounds
    if quadrant_result['min_x'] is not None:
        quadrant_result['min_x'] += left_quadrant_width
        quadrant_result['max_x'] += left_quadrant_width


def adjust_bottom_quadrant_y_coordinates(quadrant_result, top_quadrant_height):
    """
    Adjust y-coordinates for bottom quadrants to create continuous coordinate space.

    Adds top_quadrant_height to all y-coordinates in bottom quadrants (bottom_left, bottom_right)
    to position them relative to the full page height.

    Args:
        quadrant_result: Quadrant result dict with blocks
        top_quadrant_height: Height of top quadrant image (e.g., 3300 for upscaled quadrant)
    """
    # Adjust per-block y-coordinates
    for block in quadrant_result['blocks']:
        block['start_y'] += top_quadrant_height
        block['end_y'] += top_quadrant_height
        block['mid_y'] += top_quadrant_height
        # Recalculate mid_y_x with updated mid_y
        block['mid_y_x'] = block['mid_y'] + block['start_x'] / 50

    # Adjust quadrant-level y-bounds
    if quadrant_result['min_y'] is not None:
        quadrant_result['min_y'] += top_quadrant_height
        quadrant_result['max_y'] += top_quadrant_height


def extract_all_quadrants(quadrants_dir, output_dir, gpu=False):
    """
    Run EasyOCR on all quadrant images.

    Args:
        quadrants_dir: Path to directory containing quadrant images
        output_dir: Path to save OCR results
        gpu: Use GPU acceleration if available (default: False)

    Returns:
        Dict with processing results
    """
    quadrants_dir = Path(quadrants_dir)
    output_dir = Path(output_dir)

    # Load quadrant metadata
    metadata_path = quadrants_dir / 'quadrant_metadata.json'
    if not metadata_path.exists():
        raise FileNotFoundError(f"Quadrant metadata not found: {metadata_path}")

    with open(metadata_path, 'r', encoding='utf-8') as f:
        quadrant_metadata = json.load(f)

    print(f"Initializing EasyOCR reader...")
    print(f"GPU acceleration: {'Enabled' if gpu else 'Disabled'}")
    reader = easyocr.Reader(['en'], gpu=gpu)
    print(f"✓ EasyOCR reader initialized")
    print()

    pages = quadrant_metadata['pages']
    total_pages = len(pages)
    total_quadrants = 0
    total_blocks = 0
    all_ocr_results = []

    # Process each page's quadrants
    for page_idx, page_info in enumerate(pages, 1):
        page_num = page_info['page_number']
        quadrants = page_info['quadrants']

        print(f"Processing page {page_num} ({page_idx}/{total_pages})...")

        page_ocr_results = {
            'page_number': page_num,
            'quadrants': []
        }

        # Track dimensions for coordinate adjustment
        left_quadrant_width = None
        top_quadrant_height = None

        # Process each quadrant
        for quadrant_info in quadrants:
            quadrant_name = quadrant_info['quadrant_name']
            quadrant_filename = quadrant_info['filename']
            quadrant_path = quadrants_dir / quadrant_filename

            if not quadrant_path.exists():
                print(f"  ✗ Quadrant not found: {quadrant_path}")
                continue

            print(f"  {quadrant_name}...", end=" ", flush=True)

            # Run OCR
            ocr_blocks = run_easyocr_on_quadrant(quadrant_path, reader)
            total_blocks += len(ocr_blocks)
            total_quadrants += 1

            # Calculate quadrant-level bounding statistics
            if ocr_blocks:
                min_x = min(block['start_x'] for block in ocr_blocks)
                max_x = max(block['end_x'] for block in ocr_blocks)
                min_y = min(block['start_y'] for block in ocr_blocks)
                max_y = max(block['end_y'] for block in ocr_blocks)
            else:
                # No text detected in this quadrant
                min_x = max_x = min_y = max_y = None

            # Store results with metadata
            quadrant_result = {
                'quadrant_name': quadrant_name,
                'page_number': page_num,
                'source_image': quadrant_filename,
                'image_width': quadrant_info['width_px'],
                'image_height': quadrant_info['height_px'],
                'offset_x': quadrant_info['offset_x'],
                'offset_y': quadrant_info['offset_y'],
                'crop_box': quadrant_info['crop_box'],
                'total_blocks': len(ocr_blocks),
                'min_x': min_x,
                'max_x': max_x,
                'min_y': min_y,
                'max_y': max_y,
                'blocks': ocr_blocks
            }

            # Store dimensions for adjusting coordinates
            if quadrant_name in ['top_left', 'bottom_left']:
                left_quadrant_width = quadrant_info['width_px']
            if quadrant_name in ['top_left', 'top_right']:
                top_quadrant_height = quadrant_info['height_px']

            # Adjust x-coordinates for right quadrants
            if quadrant_name in ['top_right', 'bottom_right'] and left_quadrant_width:
                adjust_right_quadrant_x_coordinates(quadrant_result, left_quadrant_width)

            # Adjust y-coordinates for bottom quadrants
            if quadrant_name in ['bottom_left', 'bottom_right'] and top_quadrant_height:
                adjust_bottom_quadrant_y_coordinates(quadrant_result, top_quadrant_height)

            page_ocr_results['quadrants'].append(quadrant_result)

            # Save individual quadrant OCR result
            ocr_filename = quadrant_filename.replace('.png', '_ocr.json')
            ocr_path = output_dir / ocr_filename
            with open(ocr_path, 'w', encoding='utf-8') as f:
                json.dump(quadrant_result, f, indent=2, ensure_ascii=False)

            print(f"✓ {len(ocr_blocks)} blocks extracted")

        all_ocr_results.append(page_ocr_results)
        print()

    print(f"✓ Total quadrants processed: {total_quadrants}")
    print(f"✓ Total text blocks extracted: {total_blocks}")

    # Save combined metadata
    metadata = {
        'pdf_name': quadrant_metadata['pdf_name'],
        'total_pages': total_pages,
        'total_quadrants': total_quadrants,
        'total_blocks': total_blocks,
        'gpu_enabled': gpu,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_ocr_results
    }

    metadata_path = output_dir / 'ocr_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path}")

    return {
        'total_pages': total_pages,
        'total_quadrants': total_quadrants,
        'total_blocks': total_blocks,
        'metadata': metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.

    Usage:
        python stage_3_easyocr_extraction.py <quadrants_dir> [output_dir] [gpu]
    """
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Usage: python stage_3_easyocr_extraction.py <quadrants_dir> [output_dir] [gpu]")
        print("\nExample:")
        print("  python stage_3_easyocr_extraction.py quadrants/ ocr_results/ False")
        sys.exit(1)

    quadrants_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "ocr_results"
    gpu = sys.argv[3].lower() in ['true', '1', 'yes'] if len(sys.argv) > 3 else False

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Run OCR
    results = extract_all_quadrants(quadrants_dir, output_dir, gpu)

    print(f"\n✓ Success! {results['total_blocks']} text blocks extracted to: {output_dir}")
