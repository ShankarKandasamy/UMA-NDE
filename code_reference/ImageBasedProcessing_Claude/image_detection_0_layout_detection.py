"""
Stage 0: Layout Detection using LayoutParser
Detects figures, tables, and other layout elements in PDF documents.

Usage:
    python image_detection_0_layout_detection.py --pdf docs/DeepWalk.pdf
    python image_detection_0_layout_detection.py --pdf docs/DeepWalk.pdf --dpi 300 --threshold 0.5
"""

import argparse
import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Dependency checking and installation helper
def check_and_install_dependencies():
    """Check if required dependencies are installed and provide installation instructions."""
    missing_deps = []
    installation_instructions = []

    # Check for essential packages
    try:
        import torch
        print(f"[OK] PyTorch installed: {torch.__version__}")
    except ImportError:
        missing_deps.append("torch")
        installation_instructions.append(
            "PyTorch: pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu118"
        )

    try:
        import cv2
        print(f"[OK] OpenCV installed: {cv2.__version__}")
    except ImportError:
        missing_deps.append("opencv-python")
        installation_instructions.append("OpenCV: pip install opencv-python")

    try:
        import numpy as np
        print(f"[OK] NumPy installed: {np.__version__}")
    except ImportError:
        missing_deps.append("numpy")
        installation_instructions.append("NumPy: pip install numpy")

    try:
        from pdf2image import convert_from_path
        print("[OK] pdf2image installed")
    except ImportError:
        missing_deps.append("pdf2image")
        installation_instructions.append("pdf2image: pip install pdf2image")
        installation_instructions.append("NOTE: pdf2image also requires poppler. On Windows, download from: https://github.com/oschwartz10612/poppler-windows/releases/")

    try:
        from PIL import Image
        print(f"[OK] Pillow installed: {Image.__version__}")
    except ImportError:
        missing_deps.append("Pillow")
        installation_instructions.append("Pillow: pip install Pillow")

    # Check for LayoutParser (this is the key one)
    try:
        import layoutparser as lp
        print(f"[OK] LayoutParser installed: {lp.__version__}")
    except ImportError:
        missing_deps.append("layoutparser")
        installation_instructions.append("LayoutParser: pip install layoutparser")

    # Check for detectron2 or paddledetection (backend for LayoutParser)
    has_backend = False
    try:
        import detectron2
        print(f"[OK] Detectron2 installed: {detectron2.__version__}")
        has_backend = True
    except ImportError:
        print("[WARN] Detectron2 not found (this is okay, will try PaddleDetection)")

    try:
        import paddle
        print(f"[OK] PaddlePaddle installed: {paddle.__version__}")
        has_backend = True
    except ImportError:
        print("[WARN] PaddlePaddle not found")

    if not has_backend and 'layoutparser' not in missing_deps:
        missing_deps.append("detectron2 or paddlepaddle")
        installation_instructions.append(
            "\nLayout detection backend (choose ONE):\n"
            "  Option A (easier on Windows): pip install paddlepaddle paddledet\n"
            "  Option B (more accurate): Install detectron2 from https://detectron2.readthedocs.io/en/latest/tutorials/install.html"
        )

    if missing_deps:
        print("\n" + "="*80)
        print("[ERROR] MISSING DEPENDENCIES DETECTED")
        print("="*80)
        print("\nThe following packages need to be installed:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstallation instructions:")
        for instruction in installation_instructions:
            print(f"  {instruction}")
        print("\n" + "="*80)
        return False

    print("\n[OK] All dependencies are installed!")
    return True


def detect_layout(pdf_path, output_dir, dpi=300, threshold=0.5, use_paddle=False):
    """
    Detect layout elements (figures, tables, text) in a PDF.

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for cropped images and metadata
        dpi: DPI for rendering PDF pages
        threshold: Confidence threshold for detections
        use_paddle: If True, use PaddleDetection backend; else use Detectron2
    """
    import layoutparser as lp
    import cv2
    import numpy as np
    from pdf2image import convert_from_path
    from PIL import Image

    print(f"\n{'='*80}")
    print(f"Processing: {pdf_path}")
    print(f"Output directory: {output_dir}")
    print(f"DPI: {dpi}, Threshold: {threshold}")
    print(f"Backend: {'PaddleDetection' if use_paddle else 'Detectron2'}")
    print(f"{'='*80}\n")

    # Create output directories
    output_path = Path(output_dir)
    figures_dir = output_path / "figures"
    tables_dir = output_path / "tables"
    text_dir = output_path / "text_regions"
    metadata_dir = output_path / "metadata"

    for dir_path in [figures_dir, tables_dir, text_dir, metadata_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # Load the layout detection model
    print("Loading layout detection model...")
    try:
        if use_paddle:
            # PaddleDetection backend (Windows-friendly)
            model = lp.PaddleDetectionLayoutModel(
                "lp://PubLayNet/ppyolov2_r50vd_dcn_365e_publaynet/config",
                threshold=threshold,
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
            print("[OK] PaddleDetection model loaded")
        else:
            # Detectron2 backend (more accurate)
            model = lp.Detectron2LayoutModel(
                'lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", threshold],
                label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
            )
            print("[OK] Detectron2 model loaded")
    except Exception as e:
        print(f"[ERROR] Error loading model: {e}")
        print("\nTrying to determine which backend is available...")

        try:
            import detectron2
            print("Detectron2 is installed, but model loading failed.")
            print("Try using --use-paddle flag to use PaddleDetection instead.")
        except ImportError:
            pass

        try:
            import paddle
            print("PaddlePaddle is installed, but model loading failed.")
            print("Try using --use-detectron2 flag (default) to use Detectron2 instead.")
        except ImportError:
            pass

        raise

    # Convert PDF to images
    print(f"\nConverting PDF to images at {dpi} DPI...")
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        print(f"[OK] Converted {len(images)} pages")
    except Exception as e:
        print(f"[ERROR] Error converting PDF: {e}")
        print("\nIf you see 'poppler' errors, you need to install poppler:")
        print("  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/")
        print("  Extract and add the 'bin' folder to your PATH")
        raise

    # Process each page
    all_detections = []

    for page_num, pil_image in enumerate(images, start=1):
        print(f"\n--- Processing Page {page_num}/{len(images)} ---")

        # Convert PIL Image to OpenCV format
        img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Detect layout
        print("  Detecting layout elements...")
        layout = model.detect(img_cv)

        # Organize detections by type
        figures = lp.Layout([b for b in layout if b.type == 'Figure'])
        tables = lp.Layout([b for b in layout if b.type == 'Table'])
        text_blocks = lp.Layout([b for b in layout if b.type == 'Text'])

        print(f"  Found: {len(figures)} figures, {len(tables)} tables, {len(text_blocks)} text blocks")

        page_metadata = {
            'page_number': page_num,
            'image_size': {'width': img_cv.shape[1], 'height': img_cv.shape[0]},
            'detections': []
        }

        # Save figures
        for i, block in enumerate(figures):
            cropped = block.crop_image(img_cv)
            figure_path = figures_dir / f"page_{page_num}_figure_{i}.png"
            cv2.imwrite(str(figure_path), cropped)

            detection_info = {
                'type': 'Figure',
                'index': i,
                'bbox': {
                    'x1': int(block.coordinates[0]),
                    'y1': int(block.coordinates[1]),
                    'x2': int(block.coordinates[2]),
                    'y2': int(block.coordinates[3])
                },
                'confidence': float(block.score) if hasattr(block, 'score') else 1.0,
                'file_path': str(figure_path.relative_to(output_path))
            }
            page_metadata['detections'].append(detection_info)
            print(f"    Saved figure {i}: {figure_path.name}")

        # Save tables
        for i, block in enumerate(tables):
            cropped = block.crop_image(img_cv)
            table_path = tables_dir / f"page_{page_num}_table_{i}.png"
            cv2.imwrite(str(table_path), cropped)

            detection_info = {
                'type': 'Table',
                'index': i,
                'bbox': {
                    'x1': int(block.coordinates[0]),
                    'y1': int(block.coordinates[1]),
                    'x2': int(block.coordinates[2]),
                    'y2': int(block.coordinates[3])
                },
                'confidence': float(block.score) if hasattr(block, 'score') else 1.0,
                'file_path': str(table_path.relative_to(output_path))
            }
            page_metadata['detections'].append(detection_info)
            print(f"    Saved table {i}: {table_path.name}")

        # Save page metadata
        all_detections.append(page_metadata)

    # Save overall metadata
    metadata_file = metadata_dir / "layout_detections.json"
    with open(metadata_file, 'w') as f:
        json.dump({
            'pdf_path': str(pdf_path),
            'dpi': dpi,
            'threshold': threshold,
            'backend': 'PaddleDetection' if use_paddle else 'Detectron2',
            'timestamp': datetime.now().isoformat(),
            'total_pages': len(images),
            'pages': all_detections
        }, f, indent=2)

    print(f"\n{'='*80}")
    print("[OK] Layout detection complete!")
    print(f"Metadata saved to: {metadata_file}")
    print(f"{'='*80}\n")

    # Summary
    total_figures = sum(len([d for d in p['detections'] if d['type'] == 'Figure']) for p in all_detections)
    total_tables = sum(len([d for d in p['detections'] if d['type'] == 'Table']) for p in all_detections)

    print("Summary:")
    print(f"  Total pages: {len(images)}")
    print(f"  Total figures detected: {total_figures}")
    print(f"  Total tables detected: {total_tables}")
    print(f"  Figures saved to: {figures_dir}")
    print(f"  Tables saved to: {tables_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Detect layout elements (figures, tables) in PDF documents using LayoutParser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_detection_0_layout_detection.py --pdf docs/DeepWalk.pdf
  python image_detection_0_layout_detection.py --pdf docs/DeepWalk.pdf --dpi 300 --threshold 0.5
  python image_detection_0_layout_detection.py --pdf docs/DeepWalk.pdf --use-paddle
  python image_detection_0_layout_detection.py --check-deps
        """
    )

    parser.add_argument('--pdf', type=str, help='Path to PDF file')
    parser.add_argument('--output', type=str, help='Output directory (default: auto-generated)')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF rendering (default: 300)')
    parser.add_argument('--threshold', type=float, default=0.5, help='Detection confidence threshold (default: 0.5)')
    parser.add_argument('--use-paddle', action='store_true', help='Use PaddleDetection backend instead of Detectron2')
    parser.add_argument('--check-deps', action='store_true', help='Check if all dependencies are installed')

    args = parser.parse_args()

    # Check dependencies
    if args.check_deps or not args.pdf:
        deps_ok = check_and_install_dependencies()
        if not deps_ok:
            sys.exit(1)
        if args.check_deps:
            print("\n✓ All dependencies are properly installed!")
            print("You can now run layout detection on PDFs.")
            sys.exit(0)

    # Validate PDF path
    if not args.pdf:
        parser.print_help()
        sys.exit(1)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    # Generate output directory name
    if args.output:
        output_dir = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_name = pdf_path.stem
        output_dir = f"layout_detection_{pdf_name}_{timestamp}"

    # Run layout detection
    try:
        detect_layout(
            pdf_path=str(pdf_path),
            output_dir=output_dir,
            dpi=args.dpi,
            threshold=args.threshold,
            use_paddle=args.use_paddle
        )
    except Exception as e:
        print(f"\n❌ Error during layout detection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
