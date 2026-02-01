"""
Stage 1: Screenshot Generator

Generates high-resolution screenshots from PDF pages.

Input:  PDF file
Output: PNG screenshots at 300 DPI (one per page)
        Format: page_1_<filename>.png, page_2_<filename>.png, ...
"""

import fitz  # PyMuPDF
from PIL import Image
from pathlib import Path
from datetime import datetime
import json


def generate_screenshots(pdf_path, output_dir, num_pages=None, dpi=300):
    """
    Generate high-resolution screenshots from PDF pages.

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save screenshots
        num_pages: Number of pages to process (None = all pages)
        dpi: Resolution for rendering (default: 300)

    Returns:
        Dict with processing results:
        {
            'total_pages': int,
            'screenshot_files': [str],
            'metadata': {...}
        }
    """
    print(f"Opening PDF: {pdf_path}")

    # Open PDF
    doc = fitz.open(pdf_path)
    total_pages_in_pdf = len(doc)
    pages_to_process = num_pages if num_pages else total_pages_in_pdf
    pages_to_process = min(pages_to_process, total_pages_in_pdf)

    print(f"Total pages in PDF: {total_pages_in_pdf}")
    print(f"Pages to process: {pages_to_process}")
    print(f"Resolution: {dpi} DPI")
    print()

    # Calculate zoom for desired DPI (72 DPI is default)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    # Get base filename for naming screenshots
    pdf_name = Path(pdf_path).stem

    # Track screenshot files
    screenshot_files = []
    page_metadata = []

    # Generate screenshots
    for page_num in range(pages_to_process):
        print(f"Processing page {page_num + 1}/{pages_to_process}...", end=" ")

        # Get page
        page = doc[page_num]

        # Render page to pixmap
        pix = page.get_pixmap(matrix=matrix)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Save screenshot
        screenshot_filename = f"page_{page_num + 1}_{pdf_name}.png"
        screenshot_path = Path(output_dir) / screenshot_filename
        img.save(screenshot_path)

        screenshot_files.append(str(screenshot_path))

        # Store page metadata
        page_metadata.append({
            'page_number': page_num + 1,
            'screenshot_file': screenshot_filename,
            'width_px': img.width,
            'height_px': img.height,
            'dpi': dpi
        })

        print(f"✓ {img.width}x{img.height}px → {screenshot_filename}")

    doc.close()

    print()
    print(f"✓ Generated {len(screenshot_files)} screenshots")

    # Save screenshot metadata
    metadata = {
        'pdf_path': str(pdf_path),
        'pdf_name': pdf_name,
        'total_pages_in_pdf': total_pages_in_pdf,
        'pages_processed': pages_to_process,
        'dpi': dpi,
        'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'pages': page_metadata
    }

    metadata_path = Path(output_dir) / 'screenshot_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path}")

    return {
        'total_pages': pages_to_process,
        'screenshot_files': screenshot_files,
        'metadata': metadata
    }


if __name__ == "__main__":
    """
    Standalone testing mode.

    Usage:
        python stage_1_screenshot_generator.py <pdf_path> [num_pages] [output_dir]
    """
    import sys
    import io

    # Set UTF-8 encoding for console output (Windows compatibility)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Usage: python stage_1_screenshot_generator.py <pdf_path> [num_pages] [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    num_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "screenshots_test"

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate screenshots
    results = generate_screenshots(pdf_path, output_dir, num_pages)

    print(f"\n✓ Success! {results['total_pages']} screenshots saved to: {output_dir}")
