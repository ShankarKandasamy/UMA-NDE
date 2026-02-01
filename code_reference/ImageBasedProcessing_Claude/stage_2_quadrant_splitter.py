"""
Stage 2: Quadrant Splitter

Splits high-resolution screenshots into 4 non-overlapping quadrants.

Input:  PNG screenshots from Stage 1 (screenshots/)
Output: 4 quadrant images per page (quadrants/)
        Format: page_1_top_left.png, page_1_top_right.png, etc.
"""

from PIL import Image
from pathlib import Path
from datetime import datetime
import json


def split_into_quadrants(image_path, output_dir, page_num, pdf_name, overlap_ratio=0.0, upscale_to_original=True):
    """
    Split a single screenshot into 4 quadrants and upscale for better OCR.

    Args:
        image_path: Path to screenshot PNG
        output_dir: Directory to save quadrants
        page_num: Page number (1-indexed)
        pdf_name: Name of PDF (for filenames)
        overlap_ratio: Overlap ratio (0.0 = no overlap, 0.3 = 30% overlap)
        upscale_to_original: If True, resize each quadrant to original page size (default: True)

    Returns:
        Dict with quadrant metadata
    """
    # Load image
    img = Image.open(image_path)
    width, height = img.size

    # Calculate quadrant dimensions
    # For 0% overlap: each quadrant is exactly 50% of width and height
    # For N% overlap: each quadrant is (50% + N%) of width and height
    base_coverage = 0.5 + overlap_ratio
    quad_width = int(width * base_coverage)
    quad_height = int(height * base_coverage)

    # Calculate offsets for right and bottom quadrants
    # For 0% overlap: offset is exactly 50%
    # For N% overlap: offset is (50% - N%)
    offset_x = int(width * (0.5 - overlap_ratio))
    offset_y = int(height * (0.5 - overlap_ratio))

    # Define quadrant boundaries: (x1, y1, x2, y2)
    quadrant_coords = {
        'top_left': (0, 0, quad_width, quad_height),
        'top_right': (offset_x, 0, width, quad_height),
        'bottom_left': (0, offset_y, quad_width, height),
        'bottom_right': (offset_x, offset_y, width, height)
    }

    quadrant_metadata = []

    # Split and save each quadrant
    for quadrant_name, (x1, y1, x2, y2) in quadrant_coords.items():
        # Crop quadrant
        quadrant_img = img.crop((x1, y1, x2, y2))

        # Store original cropped dimensions
        cropped_width = quadrant_img.width
        cropped_height = quadrant_img.height

        # Upscale to original page size for better OCR (zoom effect)
        if upscale_to_original:
            quadrant_img = quadrant_img.resize(
                (width, height),
                Image.Resampling.LANCZOS  # High-quality downsampling
            )

        # Generate filename
        quadrant_filename = f"page_{page_num}_{quadrant_name}_{pdf_name}.png"
        quadrant_path = output_dir / quadrant_filename

        # Save quadrant
        quadrant_img.save(quadrant_path)

        # Store metadata
        quadrant_metadata.append({
            'quadrant_name': quadrant_name,
            'page_number': page_num,
            'filename': quadrant_filename,
            'width_px': quadrant_img.width,
            'height_px': quadrant_img.height,
            'cropped_width_px': cropped_width,
            'cropped_height_px': cropped_height,
            'upscaled': upscale_to_original,
            'offset_x': x1,
            'offset_y': y1,
            'crop_box': [x1, y1, x2, y2],
            'full_page_width': width,
            'full_page_height': height
        })

    return {
        'page_number': page_num,
        'source_screenshot': str(image_path.name),
        'full_page_width': width,
        'full_page_height': height,
        'quadrant_width': quad_width,
        'quadrant_height': quad_height,
        'overlap_ratio': overlap_ratio,
        'quadrants': quadrant_metadata
    }


def split_all_screenshots(screenshots_dir, output_dir, overlap_ratio=0.0, upscale_to_original=True):
    """
    Split all screenshots in a directory into quadrants.

    Args:
        screenshots_dir: Path to directory containing screenshots
        output_dir: Path to save quadrants
        overlap_ratio: Overlap ratio (default: 0.0 = no overlap)
        upscale_to_original: Upscale quadrants to original size for better OCR (default: True)

    Returns:
        Dict with processing results
    """
    screenshots_dir = Path(screenshots_dir)
    output_dir = Path(output_dir)

    # Load screenshot metadata
    metadata_path = screenshots_dir / 'screenshot_metadata.json'
    if not metadata_path.exists():
        raise FileNotFoundError(f"Screenshot metadata not found: {metadata_path}")

    with open(metadata_path, 'r', encoding='utf-8') as f:
        screenshot_metadata = json.load(f)

    pdf_name = screenshot_metadata['pdf_name']
    pages = screenshot_metadata['pages']

    print(f"Splitting {len(pages)} screenshots into quadrants...")
    print(f"Overlap ratio: {overlap_ratio * 100:.0f}%")
    print(f"Upscale to original size: {'Yes' if upscale_to_original else 'No'} (for better OCR)")
    print()

    all_page_metadata = []
    total_quadrants = 0

    # Process each screenshot
    for page_info in pages:
        page_num = page_info['page_number']
        screenshot_file = page_info['screenshot_file']
        screenshot_path = screenshots_dir / screenshot_file

        print(f"Processing page {page_num}...", end=" ")

        if not screenshot_path.exists():
            print(f"✗ Screenshot not found: {screenshot_path}")
            continue

        # Split into quadrants
        page_metadata = split_into_quadrants(
            image_path=screenshot_path,
            output_dir=output_dir,
            page_num=page_num,
            pdf_name=pdf_name,
            overlap_ratio=overlap_ratio,
            upscale_to_original=upscale_to_original
        )

        all_page_metadata.append(page_metadata)
        total_quadrants += len(page_metadata['quadrants'])

        print(f"✓ {len(page_metadata['quadrants'])} quadrants created")

    print()
    print(f"✓ Total quadrants created: {total_quadrants}")

    # Save quadrant metadata
    metadata = {
        'pdf_name': pdf_name,
        'total_pages': len(all_page_metadata),
        'total_quadrants': total_quadrants,
        'overlap_ratio': overlap_ratio,
        'upscaled_to_original': upscale_to_original,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': all_page_metadata
    }

    metadata_path = output_dir / 'quadrant_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path}")

    return {
        'total_pages': len(all_page_metadata),
        'total_quadrants': total_quadrants,
        'metadata': metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.

    Usage:
        python stage_2_quadrant_splitter.py <screenshots_dir> [output_dir] [overlap_ratio]
    """
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Usage: python stage_2_quadrant_splitter.py <screenshots_dir> [output_dir] [overlap_ratio] [upscale]")
        print("\nExample:")
        print("  python stage_2_quadrant_splitter.py screenshots/ quadrants/ 0.0 True")
        sys.exit(1)

    screenshots_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "quadrants"
    overlap_ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    upscale = sys.argv[4].lower() in ['true', '1', 'yes'] if len(sys.argv) > 4 else True

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Split screenshots
    results = split_all_screenshots(screenshots_dir, output_dir, overlap_ratio, upscale)

    print(f"\n✓ Success! {results['total_quadrants']} quadrants saved to: {output_dir}")
