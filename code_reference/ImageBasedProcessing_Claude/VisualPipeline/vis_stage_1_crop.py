"""
Visual Stage 1: Crop Document Elements using YOLOv8

Detects and crops out all document layout elements from PDF documents using
YOLOv8 trained on DocLayNet dataset.

Model: hantian/yolo-doclaynet (YOLOv8 trained on DocLayNet dataset)
Classes: Caption, Footnote, Formula, List-item, Page-footer, Page-header,
         Picture, Section-header, Table, Text, Title

This stage extracts ALL 11 DocLayNet classes and saves them as individual images
in class-specific subdirectories.

Usage as standalone:
    python vis_stage_1_crop.py --pdf docs/DeepWalk.pdf
    python vis_stage_1_crop.py --pdf docs/DeepWalk.pdf --dpi 300 --conf 0.5

Usage as pipeline stage (called by test_vis_pipeline.py):
    from vis_stage_1_crop import crop_figures_tables
    results = crop_figures_tables(pdf_path, output_dir, num_pages=2, dpi=300, conf_threshold=0.5)
"""

import argparse
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
from ultralytics import YOLO

# DocLayNet class labels (11 categories)
DOCLAYNET_CLASSES = {
    0: "Caption",
    1: "Footnote",
    2: "Formula",
    3: "List-item",
    4: "Page-footer",
    5: "Page-header",
    6: "Picture",      # This is "Figure"
    7: "Section-header",
    8: "Table",
    9: "Text",
    10: "Title"
}

# Extract all classes (set to None to extract everything, or list specific classes)
TARGET_CLASSES = ["Picture", "Table"]  # Only extract images and tables

# Color scheme for visualizations (BGR format for OpenCV)
CLASS_COLORS = {
    "Caption": (255, 165, 0),      # Orange
    "Footnote": (128, 128, 128),   # Gray
    "Formula": (255, 0, 255),      # Magenta
    "List-item": (0, 255, 255),    # Cyan
    "Page-footer": (128, 0, 128),  # Purple
    "Page-header": (128, 0, 128),  # Purple
    "Picture": (0, 255, 0),        # Green
    "Section-header": (255, 255, 0), # Yellow
    "Table": (255, 0, 0),          # Blue
    "Text": (200, 200, 200),       # Light gray
    "Title": (0, 128, 255)         # Orange-blue
}


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")

    try:
        from ultralytics import YOLO
        print("[OK] Ultralytics YOLO installed")
    except ImportError:
        print("[ERROR] Ultralytics not found. Install with: pip install ultralytics")
        return False

    try:
        import cv2
        print(f"[OK] OpenCV installed: {cv2.__version__}")
    except ImportError:
        print("[ERROR] OpenCV not found. Install with: pip install opencv-python")
        return False

    try:
        import fitz
        print(f"[OK] PyMuPDF installed: {fitz.__version__}")
    except ImportError:
        print("[ERROR] PyMuPDF not found. Install with: pip install pymupdf")
        return False

    print("[OK] All dependencies installed!\n")
    return True


def normalize_bbox_coordinates(x1, y1, x2, y2, page_width, page_height):
    """
    Normalize bounding box coordinates to 0-100 range relative to page dimensions.

    Uses the same normalization as stage_8_horizontal_buckets.py.

    Args:
        x1, y1: Top-left corner coordinates
        x2, y2: Bottom-right corner coordinates
        page_width: Page width in pixels
        page_height: Page height in pixels

    Returns:
        Dict with normalized coordinates: {left_edge, top_edge, right_edge, bottom_edge}
    """
    # Avoid division by zero
    if page_width == 0:
        page_width = 2550
    if page_height == 0:
        page_height = 3300

    # Normalize to 0-100 range (percentage) as integers
    normalized = {
        'left_edge': int(round((x1 / page_width) * 100)),
        'top_edge': int(round((y1 / page_height) * 100)),
        'right_edge': int(round((x2 / page_width) * 100)),
        'bottom_edge': int(round((y2 / page_height) * 100))
    }

    return normalized


def load_model(model_path=None):
    """
    Load YOLOv8 model trained on DocLayNet.

    Args:
        model_path: Path to .pt model file. If None, looks for yolov8m-doclaynet.pt
                   in ImageBasedProcessing_Claude directory.

    Returns:
        YOLO model instance
    """
    if model_path is None:
        # Default: look for model in parent ImageBasedProcessing_Claude directory
        script_dir = Path(__file__).parent.parent
        model_path = script_dir / "yolov8m-doclaynet.pt"

    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}\n"
            f"Please download the model or provide correct path."
        )

    print(f"Loading model: {model_path}")

    try:
        model = YOLO(str(model_path))
        print(f"[OK] Model loaded successfully")
        print(f"     Classes: {len(model.names)} categories")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        raise


def crop_figures_tables(pdf_path, output_dir, num_pages=None, dpi=300,
                       conf_threshold=0.5, model_path=None):
    """
    Crop all document layout elements from a PDF using YOLOv8 layout detection.

    This is the main function called by the visual pipeline orchestrator.
    Extracts all 11 DocLayNet classes by default (TARGET_CLASSES = None).

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for cropped images and metadata
        num_pages: Number of pages to process (None = all pages)
        dpi: DPI for rendering PDF pages
        conf_threshold: Confidence threshold for detections (0.0-1.0)
        model_path: Path to YOLO model weights (None = auto-detect)

    Returns:
        Dict with results:
        {
            'total_pages': int,
            'class_counts': dict,  # Counts for each class
            'total_detections': int,
            'output_dir': str,
            'metadata_file': str
        }
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)

    print(f"Stage 1: Crop Document Elements")
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_dir}")
    print(f"DPI: {dpi}, Confidence threshold: {conf_threshold}")
    if TARGET_CLASSES:
        print(f"Target classes: {', '.join(TARGET_CLASSES)}")
    else:
        print(f"Target classes: ALL (extracting all 11 DocLayNet classes)")

    # Create base output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Create directories for each class (created on-demand)
    class_dirs = {}
    for class_name in DOCLAYNET_CLASSES.values():
        # Convert class names to directory-friendly format
        dir_name = class_name.lower().replace("-", "_")
        class_dirs[class_name] = output_path / dir_name

    # Load model
    model = load_model(model_path)

    # Convert PDF to images using PyMuPDF
    print(f"Converting PDF to images at {dpi} DPI...")
    try:
        pdf_document = fitz.open(str(pdf_path))
        total_pages = len(pdf_document)
        pages_to_process = min(num_pages, total_pages) if num_pages else total_pages

        images = []

        # Calculate zoom factor for desired DPI (default PDF is 72 DPI)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for page_num in range(pages_to_process):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=mat)
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)

        pdf_document.close()

        if num_pages and total_pages > num_pages:
            print(f"[OK] Converted {len(images)} pages (limited from {total_pages} total)")
        else:
            print(f"[OK] Converted {len(images)} pages")
    except Exception as e:
        print(f"[ERROR] PDF conversion failed: {e}")
        raise

    # Process each page
    all_detections = []

    # Initialize counters for all classes
    class_counts = {class_name: 0 for class_name in DOCLAYNET_CLASSES.values()}

    for page_num, pil_image in enumerate(images, start=1):
        print(f"  Processing page {page_num}/{len(images)}...")

        # Convert PIL to OpenCV format
        img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        img_h, img_w = img_cv.shape[:2]

        # Run YOLO detection
        results = model(img_cv, conf=conf_threshold, verbose=False)

        # Process detections
        page_metadata = {
            'page_number': page_num,
            'image_size': {'width': img_w, 'height': img_h},
            'detections': []
        }

        # Initialize per-page counters for all classes
        page_class_counts = {class_name: 0 for class_name in DOCLAYNET_CLASSES.values()}

        # Extract boxes
        boxes = results[0].boxes
        for box in boxes:
            # Get detection info
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            # Get class name
            class_name = model.names[cls_id]

            # Filter by target classes if specified
            if TARGET_CLASSES and class_name not in TARGET_CLASSES:
                continue

            # Crop the detection
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cropped = img_cv[y1:y2, x1:x2]

            # Get class-specific directory and counter
            class_dir = class_dirs[class_name]
            class_index = page_class_counts[class_name]

            # Create directory on first detection of this class
            class_dir.mkdir(parents=True, exist_ok=True)

            # Save cropped image
            dir_name = class_name.lower().replace("-", "_")
            save_path = class_dir / f"page_{page_num}_{dir_name}_{class_index}.png"
            cv2.imwrite(str(save_path), cropped)

            # Update counters
            page_class_counts[class_name] += 1
            class_counts[class_name] += 1

            # Get normalized coordinates (0-100 range)
            normalized_coords = normalize_bbox_coordinates(x1, y1, x2, y2, img_w, img_h)

            # Save metadata
            detection_info = {
                'type': class_name,
                'index': class_index,
                'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                'left_edge': normalized_coords['left_edge'],
                'top_edge': normalized_coords['top_edge'],
                'right_edge': normalized_coords['right_edge'],
                'bottom_edge': normalized_coords['bottom_edge'],
                'confidence': conf,
                'file_path': str(save_path.relative_to(output_path))
            }
            page_metadata['detections'].append(detection_info)

        # Print page summary
        total_page_detections = sum(page_class_counts.values())
        detected_classes = [f"{cls}: {cnt}" for cls, cnt in page_class_counts.items() if cnt > 0]
        if detected_classes:
            print(f"    Page {page_num}: {total_page_detections} total ({', '.join(detected_classes)})")
        else:
            print(f"    Page {page_num}: No detections")

        all_detections.append(page_metadata)

    # Save overall metadata
    metadata_file = output_path / "stage_1_crop_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump({
            'pdf_path': str(pdf_path),
            'model': str(model_path) if model_path else 'yolov8m-doclaynet.pt',
            'dpi': dpi,
            'confidence_threshold': conf_threshold,
            'target_classes': TARGET_CLASSES if TARGET_CLASSES else "ALL",
            'timestamp': datetime.now().isoformat(),
            'total_pages': len(images),
            'class_counts': class_counts,
            'pages': all_detections
        }, f, indent=2)

    # Return results for orchestrator
    return {
        'total_pages': len(images),
        'class_counts': class_counts,
        'total_detections': sum(class_counts.values()),
        'output_dir': str(output_path),
        'metadata_file': str(metadata_file)
    }


def main():
    """Standalone script execution."""
    parser = argparse.ArgumentParser(
        description='Crop all document layout elements from PDFs using YOLOv8',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vis_stage_1_crop.py --pdf docs/DeepWalk.pdf
  python vis_stage_1_crop.py --pdf docs/DeepWalk.pdf --dpi 300 --conf 0.5
  python vis_stage_1_crop.py --pdf docs/DeepWalk.pdf --pages 5
  python vis_stage_1_crop.py --pdf docs/DeepWalk.pdf --check-deps

Note: Extracts all 11 DocLayNet classes (Caption, Footnote, Formula, List-item,
      Page-footer, Page-header, Picture, Section-header, Table, Text, Title).
      Modify TARGET_CLASSES in the code to filter specific classes.
        """
    )

    parser.add_argument('--pdf', type=str, help='Path to PDF file')
    parser.add_argument('--output', type=str, help='Output directory (default: auto-generated)')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF rendering (default: 300)')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold 0.0-1.0 (default: 0.5)')
    parser.add_argument('--pages', type=int, default=None,
                       help='Maximum number of pages to process (default: all)')
    parser.add_argument('--model', type=str, default=None,
                       help='Model weights file path (default: auto-detect yolov8m-doclaynet.pt)')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check if dependencies are installed')

    args = parser.parse_args()

    # Check dependencies
    if args.check_deps or not args.pdf:
        deps_ok = check_dependencies()
        if not deps_ok:
            sys.exit(1)
        if args.check_deps:
            print("All dependencies installed! Ready to process documents.")
            sys.exit(0)

    # Validate PDF path
    if not args.pdf:
        parser.print_help()
        sys.exit(1)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"[ERROR] PDF file not found: {pdf_path}")
        sys.exit(1)

    # Generate output directory
    if args.output:
        output_dir = args.output
    else:
        pdf_name = pdf_path.stem
        script_dir = Path(__file__).parent
        # Create {pdf_name}/stage_1_crop/ structure
        output_dir = script_dir / pdf_name / "stage_1_crop"

    # Run detection
    try:
        results = crop_figures_tables(
            pdf_path=str(pdf_path),
            output_dir=str(output_dir),
            num_pages=args.pages,
            dpi=args.dpi,
            conf_threshold=args.conf,
            model_path=args.model
        )

        # Print summary
        print(f"\n{'='*80}")
        print("STAGE 1 COMPLETE")
        print(f"{'='*80}")
        print(f"Total Pages: {results['total_pages']}")
        print(f"Total Detections: {results['total_detections']}")
        print(f"\nDetections by Class:")
        for class_name, count in results['class_counts'].items():
            if count > 0:
                print(f"  {class_name}: {count}")
        print(f"\nOutput: {results['output_dir']}")
        print(f"Metadata: {results['metadata_file']}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n[ERROR] Stage 1 failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
