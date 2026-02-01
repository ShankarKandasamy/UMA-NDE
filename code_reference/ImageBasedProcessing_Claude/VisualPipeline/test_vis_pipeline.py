"""
Test Visual Pipeline - Process visual elements (figures/tables) from PDF documents

Processes PDF files through the visual pipeline:
- Visual Stage 1: Crop Figures and Tables (YOLO layout detection)
- Visual Stage 2: Categorize Images (GPT-4o-mini classification)
- Visual Stage 4: Visual Analysis (Category-specific VLM extraction)
- Visual Stage 5: [Future] Entity/relationship extraction from visuals

Usage:
    python test_vis_pipeline.py <pdf_file1> [pdf_file2] [pdf_file3] ...
    python test_vis_pipeline.py --pdf docs/DeepWalk.pdf --pages 5
    python test_vis_pipeline.py --pdf docs/DeepWalk.pdf --dpi 300 --conf 0.6

Examples:
    python test_vis_pipeline.py docs/DeepWalk.pdf
    python test_vis_pipeline.py docs/DeepWalk.pdf docs/mock_report.pdf
    python test_vis_pipeline.py --pdf "docs/Farm Financial Health.pdf" --pages 10
"""

import sys
import io
import argparse
from pathlib import Path

# Set UTF-8 encoding for console output (Windows compatibility)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import visual pipeline stages
from vis_stage_1_crop import crop_figures_tables
from vis_stage_2_categorize import categorize_images
from vis_stage_4_visual_analysis import analyze_images


def run_visual_pipeline_for_pdf(pdf_path, output_base_dir=None, num_pages=None,
                                dpi=300, conf_threshold=0.5, model_path=None):
    """
    Run the visual pipeline for a single PDF.

    Args:
        pdf_path: Path to PDF file
        output_base_dir: Base directory for outputs (default: current directory)
        num_pages: Number of pages to process (None = all pages)
        dpi: DPI for PDF rendering (default: 300)
        conf_threshold: YOLO confidence threshold (default: 0.5)
        model_path: Path to YOLO model (None = auto-detect)

    Returns:
        Dict with results, or None if processing failed
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"✗ PDF not found: {pdf_path}")
        return None

    if not pdf_path.suffix.lower() == '.pdf':
        print(f"✗ Not a PDF file: {pdf_path}")
        return None

    pdf_name = pdf_path.stem

    # Determine output directory
    if output_base_dir is None:
        # Create folder in VisualPipeline directory with PDF name
        output_base_dir = Path(__file__).parent
    else:
        output_base_dir = Path(output_base_dir)

    pdf_output_dir = output_base_dir / pdf_name

    print("="*80)
    print(f"VISUAL PIPELINE: {pdf_name}")
    print("="*80)
    print(f"PDF Path: {pdf_path}")
    print(f"Output Directory: {pdf_output_dir}")
    print(f"Pages to process: {num_pages if num_pages else 'all'}")
    print(f"DPI: {dpi}, Confidence threshold: {conf_threshold}")
    print()

    # Create output directories for each stage
    stage_1_dir = pdf_output_dir / "stage_1_crop"
    stage_2_dir = pdf_output_dir / "stage_2_category"

    # Note: stage_1_dir will be created by vis_stage_1_crop.py
    # stage_2_dir will be created by vis_stage_2_categorize.py
    # Images/ and Tables/ subdirectories created only if needed

    results = {}

    # Visual Stage 1: Crop Figures and Tables
    print("VISUAL STAGE 1: Crop Figures and Tables")
    print("-" * 80)
    try:
        crop_results = crop_figures_tables(
            pdf_path=str(pdf_path),
            output_dir=stage_1_dir,
            num_pages=num_pages,
            dpi=dpi,
            conf_threshold=conf_threshold,
            model_path=model_path
        )
        results['stage_1'] = crop_results
        class_counts = crop_results['class_counts']
        num_pictures = class_counts.get('Picture', 0)
        num_tables = class_counts.get('Table', 0)
        print(f"✓ Visual Stage 1 complete: {num_pictures} pictures, "
              f"{num_tables} tables ({crop_results['total_detections']} total detections)\n")
    except Exception as e:
        print(f"✗ Visual Stage 1 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # Visual Stage 2: Categorize Figures and Tables
    print("VISUAL STAGE 2: Categorize Figures and Tables")
    print("-" * 80)
    try:
        category_results = categorize_images(
            stage_1_dir=str(stage_1_dir)
        )
        results['stage_2'] = category_results
        print(f"✓ Visual Stage 2 complete: {category_results['total_categorized']} images categorized\n")
    except Exception as e:
        print(f"✗ Visual Stage 2 failed: {e}\n")
        import traceback
        traceback.print_exc()
        # Continue even if Stage 2 fails
        results['stage_2'] = None

    # Visual Stage 4: Visual Analysis
    print("VISUAL STAGE 4: Visual Analysis")
    print("-" * 80)

    # Look for horizontal buckets file for context
    # Path: ../../DeepWalk/stage_8_horizontal_buckets/horizontal_bucket_metadata.json
    # (go up from VisualPipeline/ to ImageBasedProcessing_Claude/, then into pdf_name/)
    horizontal_buckets_file = None
    h_buckets_path = pdf_output_dir.parent.parent / pdf_name / "stage_8_horizontal_buckets" / "horizontal_bucket_metadata.json"
    if h_buckets_path.exists():
        horizontal_buckets_file = str(h_buckets_path)
        print(f"✓ Found horizontal buckets for context: {horizontal_buckets_file}")
    else:
        print(f"⚠ No horizontal buckets found at: {h_buckets_path}")
        print(f"  Context will be disabled for visual analysis")

    try:
        analysis_results = analyze_images(
            stage_2_dir=str(stage_2_dir),
            horizontal_buckets_file=horizontal_buckets_file
        )
        results['stage_4'] = analysis_results
        print(f"✓ Visual Stage 4 complete: {analysis_results['total_analyzed']} images analyzed, "
              f"{analysis_results['total_skipped']} skipped\n")
    except Exception as e:
        print(f"✗ Visual Stage 4 failed: {e}\n")
        import traceback
        traceback.print_exc()
        # Continue even if Stage 4 fails
        results['stage_4'] = None

    # Future stages will be added here
    # Visual Stage 5: Entity/relationship extraction

    print("="*80)
    print(f"✓ VISUAL PIPELINE COMPLETE FOR {pdf_name}")
    print("="*80)
    print(f"Output directory: {pdf_output_dir}")
    print()

    return {
        'pdf_name': pdf_name,
        'output_dir': str(pdf_output_dir),
        'results': results
    }


def main():
    """Run visual pipeline on PDF files provided as command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Run visual pipeline on PDF documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_vis_pipeline.py docs/DeepWalk.pdf
  python test_vis_pipeline.py docs/DeepWalk.pdf docs/mock_report.pdf
  python test_vis_pipeline.py --pdf "docs/Farm Financial Health.pdf" --pages 10
  python test_vis_pipeline.py --pdf docs/DeepWalk.pdf --dpi 300 --conf 0.6
        """
    )

    # Support both positional and --pdf argument
    parser.add_argument(
        'pdf_files',
        nargs='*',
        help='PDF file(s) to process'
    )
    parser.add_argument(
        '--pdf',
        type=str,
        help='PDF file to process (alternative to positional argument)'
    )
    parser.add_argument(
        '--pages',
        type=int,
        default=5,
        help='Number of pages to process (default: 5)'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='DPI for PDF rendering (default: 300)'
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.5,
        help='YOLO confidence threshold 0.0-1.0 (default: 0.5)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Path to YOLO model weights (default: auto-detect)'
    )

    args = parser.parse_args()

    # Combine positional and --pdf arguments
    pdf_paths = []
    if args.pdf_files:
        pdf_paths.extend([Path(arg) for arg in args.pdf_files])
    if args.pdf:
        pdf_paths.append(Path(args.pdf))

    if not pdf_paths:
        parser.print_help()
        sys.exit(1)

    num_pages = args.pages
    dpi = args.dpi
    conf_threshold = args.conf
    model_path = args.model

    print("="*80)
    print("VISUAL PIPELINE PROCESSING")
    print("="*80)
    print(f"Processing {len(pdf_paths)} PDF file(s)")
    print()

    all_results = []

    for pdf_path in pdf_paths:
        result = run_visual_pipeline_for_pdf(
            pdf_path,
            num_pages=num_pages,
            dpi=dpi,
            conf_threshold=conf_threshold,
            model_path=model_path
        )
        if result:
            all_results.append(result)
        print()  # Blank line between PDFs

    # Summary
    print("="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"Successfully processed: {len(all_results)}/{len(pdf_paths)} PDFs")
    print()

    for result in all_results:
        pdf_name = result['pdf_name']
        stage_1_data = result['results']['stage_1']
        stage_1_pages = stage_1_data['total_pages']
        stage_1_class_counts = stage_1_data['class_counts']
        stage_1_pictures = stage_1_class_counts.get('Picture', 0)
        stage_1_tables = stage_1_class_counts.get('Table', 0)
        stage_1_total = stage_1_data['total_detections']

        print(f"{pdf_name}:")
        print(f"  Stage 1 - Crop: {stage_1_pages} pages, {stage_1_pictures} pictures, "
              f"{stage_1_tables} tables ({stage_1_total} total detections)")

        # Stage 2 summary
        if result['results'].get('stage_2'):
            stage_2_data = result['results']['stage_2']
            stage_2_total = stage_2_data['total_categorized']
            category_counts = stage_2_data['category_counts']
            print(f"  Stage 2 - Categorize: {stage_2_total} images categorized")
            # Show non-zero categories
            categories_str = ", ".join([f"{cat}: {count}" for cat, count in category_counts.items() if count > 0])
            if categories_str:
                print(f"            {categories_str}")
        else:
            print(f"  Stage 2 - Categorize: Not run or failed")

        # Stage 4 summary
        if result['results'].get('stage_4'):
            stage_4_data = result['results']['stage_4']
            stage_4_analyzed = stage_4_data['total_analyzed']
            stage_4_skipped = stage_4_data['total_skipped']
            stage_4_tokens = stage_4_data['total_tokens']
            print(f"  Stage 4 - Visual Analysis: {stage_4_analyzed} images analyzed, {stage_4_skipped} skipped")
            print(f"            Tokens used: {stage_4_tokens:,}")
            # Show category distribution
            if stage_4_data.get('category_counts'):
                categories_str = ", ".join([f"{cat}: {count}" for cat, count in stage_4_data['category_counts'].items() if count > 0])
                if categories_str:
                    print(f"            {categories_str}")
        else:
            print(f"  Stage 4 - Visual Analysis: Not run or failed")

        print(f"  Output: {result['output_dir']}")
        print()


if __name__ == "__main__":
    main()
