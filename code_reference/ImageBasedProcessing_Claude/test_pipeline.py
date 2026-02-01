"""
Test Pipeline - Run all steps for PDF documents

Processes PDF files through the complete pipeline (steps 1-12):
- Step 1: Screenshot Generation
- Step 2: Quadrant Splitting
- Step 3: OCR Extraction
- Step 4: Merge Quadrants
- Step 5: Calculate Spatial Metrics
- Step 6: Horizontal Merge (merge text blocks on same line)
- Step 7: Vertical Bucket Sort (group text blocks by vertical position)
- Step 8: Horizontal Bucket Sort (group text blocks by horizontal position)
- Step 9: Vertical Column Stacking (reorder buckets for column reading flow)
- Step 10: LLM Context Chunks (convert buckets to simplified LLM-ready format)
- Step 11: LLM Reorder (GPT-4o-mini reconstructs document with proper reading order)
- Step 12: Bucket Recovery (detect and recover missing buckets from Stage 11)

Usage:
    python test_pipeline.py <pdf_file1> [pdf_file2] [pdf_file3] ...

Example:
    python test_pipeline.py ../docs/DeepWalk.pdf ../docs/mock_report.pdf
"""

import sys
import io
import argparse
import shutil
from pathlib import Path

# Set UTF-8 encoding for console output (Windows compatibility)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import pipeline stages
from stage_1_screenshot_generator import generate_screenshots
from stage_2_quadrant_splitter import split_all_screenshots
from stage_3_easyocr_extraction import extract_all_quadrants
from stage_4_merge_quadrants import merge_all_pages
from stage_5_metrics import calculate_metrics_for_all_pages
from stage_6_horizontal_merge import merge_horizontal_for_all_pages
from stage_7_vertical_buckets import process_all_pages as process_vertical_buckets
from stage_8_horizontal_buckets import process_all_pages as process_horizontal_buckets
from stage_9_vertical_stacking import process_all_pages as process_vertical_stacking
from stage_10_llm_context_chunks import process_all_pages as process_llm_chunks
from stage_11_llm_reorder import process_all_pages as process_llm_reorder
from stage_12_bucket_recovery import process_all_pages as process_bucket_recovery


def filter_directory_by_pages(directory, max_page_num, pattern):
    """
    Temporarily move files for pages > max_page_num to a temp directory.
    
    Args:
        directory: Directory to filter
        max_page_num: Maximum page number to keep (1-indexed)
        pattern: Glob pattern to match (e.g., 'page_*.json')
    
    Returns:
        List of moved files (to restore later)
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    moved_files = []
    temp_dir = directory / f"_temp_filtered_{max_page_num}"
    temp_dir.mkdir(exist_ok=True)
    
    # Find all files matching the pattern
    all_files = list(directory.glob(pattern))
    
    for file in all_files:
        # Extract page number from filename
        name = file.stem if hasattr(file, 'stem') else file.name
        parts = name.split('_')
        if len(parts) >= 2 and parts[0] == 'page':
            try:
                page_num = int(parts[1])
                if page_num > max_page_num:
                    # Move file to temp directory
                    temp_path = temp_dir / file.name
                    if file.exists():
                        shutil.move(str(file), str(temp_path))
                        moved_files.append((file, temp_path))
            except ValueError:
                continue
    
    return moved_files


def restore_moved_files(moved_files):
    """Restore files that were temporarily moved."""
    for original_path, temp_path in moved_files:
        if temp_path.exists():
            shutil.move(str(temp_path), str(original_path))
    
    # Clean up temp directory if empty
    if moved_files:
        temp_dir = moved_files[0][1].parent
        try:
            temp_dir.rmdir()
        except OSError:
            pass  # Directory not empty or doesn't exist


def run_pipeline_for_pdf(pdf_path, output_base_dir=None, num_pages=None):
    """
    Run the complete pipeline (steps 1-9) for a single PDF.
    
    Args:
        pdf_path: Path to PDF file
        output_base_dir: Base directory for outputs (default: current directory)
        num_pages: Number of pages to process (None = all pages)
    
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
    
    # Default to processing only first 2 pages
    if num_pages is None:
        num_pages = 2
    
    # Determine output directory
    if output_base_dir is None:
        # Create folder in ImageBasedProcessing_Cursor directory with PDF name
        output_base_dir = Path(__file__).parent
    else:
        output_base_dir = Path(output_base_dir)
    
    pdf_output_dir = output_base_dir / pdf_name
    
    print("="*80)
    print(f"PROCESSING: {pdf_name}")
    print("="*80)
    print(f"PDF Path: {pdf_path}")
    print(f"Output Directory: {pdf_output_dir}")
    print()
    
    # Create output directories for each stage (named to match stage scripts)
    step_1_dir = pdf_output_dir / "stage_1_screenshots"
    step_2_dir = pdf_output_dir / "stage_2_quadrants"
    step_3_dir = pdf_output_dir / "stage_3_ocr"
    step_4_dir = pdf_output_dir / "stage_4_merge_quadrants"
    step_5_dir = pdf_output_dir / "stage_5_metrics"
    step_6_dir = pdf_output_dir / "stage_6_horizontal_merge"
    step_7_dir = pdf_output_dir / "stage_7_vertical_buckets"
    step_8_dir = pdf_output_dir / "stage_8_horizontal_buckets"
    step_9_dir = pdf_output_dir / "stage_9_vertical_stacked"
    step_10_dir = pdf_output_dir / "stage_10_llm_chunks"
    step_11_dir = pdf_output_dir / "stage_11_llm_reordered"
    step_12_dir = pdf_output_dir / "stage_12_final"

    # Create directories
    step_1_dir.mkdir(parents=True, exist_ok=True)
    step_2_dir.mkdir(parents=True, exist_ok=True)
    step_3_dir.mkdir(parents=True, exist_ok=True)
    step_4_dir.mkdir(parents=True, exist_ok=True)
    step_5_dir.mkdir(parents=True, exist_ok=True)
    step_6_dir.mkdir(parents=True, exist_ok=True)
    step_7_dir.mkdir(parents=True, exist_ok=True)
    step_8_dir.mkdir(parents=True, exist_ok=True)
    step_9_dir.mkdir(parents=True, exist_ok=True)
    step_10_dir.mkdir(parents=True, exist_ok=True)
    step_11_dir.mkdir(parents=True, exist_ok=True)
    step_12_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # Step 1: Screenshots
    print("STEP 1: Screenshot Generation")
    print("-" * 80)
    try:
        screenshot_results = generate_screenshots(
            pdf_path=str(pdf_path),
            output_dir=step_1_dir,
            num_pages=num_pages,  # Process all pages if None
            dpi=300
        )
        results['step_1'] = screenshot_results
        print(f"✓ Step 1 complete: {screenshot_results['total_pages']} screenshots\n")
    except Exception as e:
        print(f"✗ Step 1 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 2: Quadrant Splitting
    print("STEP 2: Quadrant Splitting")
    print("-" * 80)
    try:
        quadrant_results = split_all_screenshots(
            screenshots_dir=step_1_dir,
            output_dir=step_2_dir,
            overlap_ratio=0.0,
            upscale_to_original=True
        )
        results['step_2'] = quadrant_results
        print(f"✓ Step 2 complete: {quadrant_results['total_quadrants']} quadrants\n")
    except Exception as e:
        print(f"✗ Step 2 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 3: OCR Extraction
    print("STEP 3: OCR Extraction")
    print("-" * 80)
    try:
        ocr_results = extract_all_quadrants(
            quadrants_dir=step_2_dir,
            output_dir=step_3_dir,
            gpu=False
        )
        results['step_3'] = ocr_results
        print(f"✓ Step 3 complete: {ocr_results['total_blocks']} text blocks\n")
    except Exception as e:
        print(f"✗ Step 3 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 4: Merge Quadrants
    print("STEP 4: Merge Quadrants")
    print("-" * 80)
    try:
        merge_results = merge_all_pages(
            ocr_dir=step_3_dir,
            output_dir=step_4_dir,
            min_confidence=0.3  # Filter out low-confidence OCR detections
        )
        results['step_4'] = merge_results
        filtered_msg = f" (filtered {merge_results['total_blocks_filtered']})" if merge_results.get('total_blocks_filtered', 0) > 0 else ""
        print(f"✓ Step 4 complete: {merge_results['total_blocks']} blocks merged{filtered_msg}\n")
    except Exception as e:
        print(f"✗ Step 4 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 5: Calculate Metrics
    print("STEP 5: Calculate Spatial Metrics")
    print("-" * 80)
    try:
        # Filter files to only process pages 1 to num_pages
        moved_files_step4 = filter_directory_by_pages(step_4_dir, num_pages, 'page_*_merged.json')
        try:
            metrics_results = calculate_metrics_for_all_pages(
                merged_dir=step_4_dir,
                output_dir=step_5_dir
            )
            results['step_5'] = metrics_results
            print(f"✓ Step 5 complete: {metrics_results['total_blocks']} blocks with metrics\n")
        finally:
            restore_moved_files(moved_files_step4)
    except Exception as e:
        print(f"✗ Step 5 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 6: Horizontal Merge
    print("STEP 6: Horizontal Merge")
    print("-" * 80)
    try:
        # Filter files to only process pages 1 to num_pages
        moved_files_step5 = filter_directory_by_pages(step_5_dir, num_pages, 'page_*_metrics.json')
        try:
            horizontal_merge_results = merge_horizontal_for_all_pages(
                metrics_dir=step_5_dir,
                output_dir=step_6_dir
            )
            results['step_6'] = horizontal_merge_results
            print(f"✓ Step 6 complete: {horizontal_merge_results['total_blocks_after']} blocks (reduced from {horizontal_merge_results['total_blocks_before']})\n")
        finally:
            restore_moved_files(moved_files_step5)
    except Exception as e:
        print(f"✗ Step 6 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None
    
    # Step 7: Vertical Bucket Sort
    print("STEP 7: Vertical Bucket Sort")
    print("-" * 80)
    try:
        # Filter files to only process pages 1 to num_pages
        moved_files_step6 = filter_directory_by_pages(step_6_dir, num_pages, 'page_*_horizontal_merged.json')
        try:
            vertical_bucket_results = process_vertical_buckets(
                input_dir=step_6_dir,
                output_dir=step_7_dir
            )
            results['step_7'] = {
                'total_buckets': vertical_bucket_results['total_buckets'],
                'total_blocks': vertical_bucket_results['total_blocks'],
                'average_blocks_per_bucket': vertical_bucket_results['average_blocks_per_bucket']
            }
            print(f"✓ Step 7 complete: {vertical_bucket_results['total_buckets']} buckets, {vertical_bucket_results['total_blocks']} blocks")
            print(f"  Average blocks per bucket: {vertical_bucket_results['average_blocks_per_bucket']:.2f}\n")
        finally:
            restore_moved_files(moved_files_step6)
    except Exception as e:
        print(f"✗ Step 7 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # Step 8: Horizontal Bucket Sort
    print("STEP 8: Horizontal Bucket Sort")
    print("-" * 80)
    try:
        # Filter files to only process pages 1 to num_pages
        moved_files_step7 = filter_directory_by_pages(step_7_dir, num_pages, 'page_*_buckets.json')
        try:
            horizontal_bucket_results = process_horizontal_buckets(
                input_dir=step_7_dir,
                output_dir=step_8_dir
            )
            results['step_8'] = {
                'total_horizontal_buckets': horizontal_bucket_results['total_horizontal_buckets'],
                'total_vertical_buckets': horizontal_bucket_results['total_vertical_buckets'],
                'average_vertical_buckets_per_horizontal_bucket': horizontal_bucket_results['average_vertical_buckets_per_horizontal_bucket']
            }
            print(f"✓ Step 8 complete: {horizontal_bucket_results['total_horizontal_buckets']} horizontal buckets from {horizontal_bucket_results['total_vertical_buckets']} vertical buckets")
            print(f"  Average: {horizontal_bucket_results['average_vertical_buckets_per_horizontal_bucket']:.2f} vertical buckets per horizontal bucket\n")
        finally:
            restore_moved_files(moved_files_step7)
    except Exception as e:
        print(f"✗ Step 8 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # Step 9: Vertical Column Stacking
    print("STEP 9: Vertical Column Stacking")
    print("-" * 80)
    try:
        # Filter files to only process pages 1 to num_pages
        moved_files_step8 = filter_directory_by_pages(step_8_dir, num_pages, 'page_*_horizontal_buckets.json')
        try:
            vertical_stacking_results = process_vertical_stacking(
                input_dir=step_8_dir,
                output_dir=step_9_dir
            )
            results['step_9'] = {
                'total_pages': vertical_stacking_results['total_pages']
            }
            print(f"✓ Step 9 complete: {vertical_stacking_results['total_pages']} page(s) re-ordered for column reading\n")
        finally:
            restore_moved_files(moved_files_step8)
    except Exception as e:
        print(f"✗ Step 9 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # Step 10: LLM Context Chunks
    print("STEP 10: LLM Context Chunks")
    print("-" * 80)
    try:
        # Filter files to only process pages 1 to num_pages
        moved_files_step9 = filter_directory_by_pages(step_9_dir, num_pages, 'page_*_vertical_stacked.json')
        try:
            llm_chunks_results = process_llm_chunks(
                input_dir=step_9_dir,
                output_dir=step_10_dir
            )
            results['step_10'] = {
                'total_pages': llm_chunks_results['total_pages'],
                'total_buckets': llm_chunks_results['total_buckets'],
                'total_texts': llm_chunks_results['total_texts']
            }
            print(f"✓ Step 10 complete: {llm_chunks_results['total_pages']} page(s), {llm_chunks_results['total_buckets']} buckets, {llm_chunks_results['total_texts']} texts\n")
        finally:
            restore_moved_files(moved_files_step9)
    except Exception as e:
        print(f"✗ Step 10 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # Step 11: LLM Reorder
    print("STEP 11: LLM Reorder (GPT-4o-mini)")
    print("-" * 80)
    try:
        llm_reorder_results = process_llm_reorder(
            input_dir=step_10_dir,
            screenshots_dir=step_1_dir,
            output_dir=step_11_dir
        )
        results['step_11'] = {
            'total_pages': llm_reorder_results['total_pages'],
            'total_missing_buckets': llm_reorder_results.get('total_missing_buckets', 0)
        }
        if llm_reorder_results.get('total_missing_buckets', 0) > 0:
            print(f"✓ Step 11 complete: {llm_reorder_results['total_pages']} page(s) reordered (⚠ {llm_reorder_results['total_missing_buckets']} missing buckets)\n")
        else:
            print(f"✓ Step 11 complete: {llm_reorder_results['total_pages']} page(s) reordered to Markdown\n")
    except Exception as e:
        print(f"✗ Step 11 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # Step 12: Bucket Recovery
    print("STEP 12: Bucket Recovery")
    print("-" * 80)
    try:
        bucket_recovery_results = process_bucket_recovery(
            stage10_dir=step_10_dir,
            stage11_dir=step_11_dir,
            screenshots_dir=step_1_dir,
            output_dir=step_12_dir
        )
        results['step_12'] = {
            'total_pages': bucket_recovery_results['total_pages'],
            'total_missing': bucket_recovery_results['total_missing'],
            'total_recovered': bucket_recovery_results['total_recovered'],
            'total_gibberish': bucket_recovery_results['total_gibberish']
        }
        if bucket_recovery_results['total_missing'] > 0:
            print(f"✓ Step 12 complete: {bucket_recovery_results['total_pages']} page(s), recovered {bucket_recovery_results['total_recovered']}/{bucket_recovery_results['total_missing']} missing buckets ({bucket_recovery_results['total_gibberish']} gibberish)\n")
        else:
            print(f"✓ Step 12 complete: {bucket_recovery_results['total_pages']} page(s), no missing buckets\n")
    except Exception as e:
        print(f"✗ Step 12 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    print("="*80)
    print(f"✓ PIPELINE COMPLETE FOR {pdf_name}")
    print("="*80)
    print(f"Output directory: {pdf_output_dir}")
    print()
    
    return {
        'pdf_name': pdf_name,
        'output_dir': str(pdf_output_dir),
        'results': results
    }


def main():
    """Run pipeline on PDF files provided as command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Run PDF processing pipeline'
    )
    parser.add_argument(
        'pdf_files',
        nargs='+',
        help='PDF file(s) to process'
    )
    parser.add_argument(
        '--num_pages',
        type=int,
        default=None,
        help='Number of pages to process (default: all pages)'
    )
    
    args = parser.parse_args()
    
    # Get PDF files from command-line arguments
    pdf_paths = [Path(arg) for arg in args.pdf_files]
    num_pages = args.num_pages
    
    print("="*80)
    print("PIPELINE PROCESSING")
    print("="*80)
    print(f"Processing {len(pdf_paths)} PDF file(s)")
    print()
    
    all_results = []
    
    for pdf_path in pdf_paths:
        result = run_pipeline_for_pdf(pdf_path, num_pages=num_pages)
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
        step_1_pages = result['results']['step_1']['total_pages']
        step_2_quadrants = result['results']['step_2']['total_quadrants']
        step_3_blocks = result['results']['step_3']['total_blocks']
        step_4_merged = result['results']['step_4']['total_blocks']
        step_5_metrics = result['results']['step_5']['total_blocks']
        step_6_before = result['results']['step_6']['total_blocks_before']
        step_6_after = result['results']['step_6']['total_blocks_after']
        step_6_reduced = result['results']['step_6']['total_blocks_reduced']
        step_7_buckets = result['results']['step_7']['total_buckets']
        step_7_blocks = result['results']['step_7']['total_blocks']
        step_7_avg = result['results']['step_7']['average_blocks_per_bucket']
        step_8_h_buckets = result['results']['step_8']['total_horizontal_buckets']
        step_8_v_buckets = result['results']['step_8']['total_vertical_buckets']
        step_8_avg = result['results']['step_8']['average_vertical_buckets_per_horizontal_bucket']
        step_9_pages = result['results']['step_9']['total_pages']
        step_10_pages = result['results']['step_10']['total_pages']
        step_10_buckets = result['results']['step_10']['total_buckets']
        step_10_texts = result['results']['step_10']['total_texts']
        step_11_pages = result['results']['step_11']['total_pages']
        step_11_missing = result['results']['step_11']['total_missing_buckets']
        step_12_pages = result['results']['step_12']['total_pages']
        step_12_missing = result['results']['step_12']['total_missing']
        step_12_recovered = result['results']['step_12']['total_recovered']
        step_12_gibberish = result['results']['step_12']['total_gibberish']

        print(f"{pdf_name}:")
        print(f"  Step 1 - Screenshots: {step_1_pages} pages")
        print(f"  Step 2 - Quadrants: {step_2_quadrants} quadrants")
        print(f"  Step 3 - OCR Blocks: {step_3_blocks} blocks")
        print(f"  Step 4 - Merged Blocks: {step_4_merged} blocks")
        print(f"  Step 5 - Metrics: {step_5_metrics} blocks")
        print(f"  Step 6 - Horizontal Merge: {step_6_after} blocks (reduced by {step_6_reduced})")
        print(f"  Step 7 - Vertical Bucket Sort: {step_7_buckets} buckets, {step_7_blocks} blocks (avg: {step_7_avg:.2f})")
        print(f"  Step 8 - Horizontal Bucket Sort: {step_8_h_buckets} h-buckets from {step_8_v_buckets} v-buckets (avg: {step_8_avg:.2f})")
        print(f"  Step 9 - Vertical Column Stacking: {step_9_pages} page(s) re-ordered")
        print(f"  Step 10 - LLM Chunks: {step_10_pages} page(s), {step_10_buckets} buckets, {step_10_texts} texts")
        if step_11_missing > 0:
            print(f"  Step 11 - LLM Reorder: {step_11_pages} Markdown file(s) (⚠ {step_11_missing} missing buckets)")
        else:
            print(f"  Step 11 - LLM Reorder: {step_11_pages} Markdown file(s)")
        if step_12_missing > 0:
            print(f"  Step 12 - Bucket Recovery: {step_12_pages} final file(s), recovered {step_12_recovered}/{step_12_missing} ({step_12_gibberish} gibberish)")
        else:
            print(f"  Step 12 - Bucket Recovery: {step_12_pages} final file(s), no missing buckets")
        print(f"  Output: {result['output_dir']}")
        print()


if __name__ == "__main__":
    main()

