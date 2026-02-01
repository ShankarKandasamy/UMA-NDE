"""
Assembly Test Pipeline - Run all assembly stages for processed documents

Orchestrates the complete assembly pipeline (stages 1-5):
- Stage 1: Merge Data (text + visual analysis)
- Stage 2: Hierarchy Extraction (document structure with GPT-4o + screenshots)
- Stage 3: LLM Chunks (semantic chunking with GPT-4o)
- Stage 4: FTS Preparation (vector embeddings) - BOILERPLATE ONLY
- Stage 5: Graph Payload (entity/edge extraction prep) - BOILERPLATE ONLY

Prerequisites:
- Text extraction pipeline (stages 1-12) must be completed
- Screenshots (stage_1_screenshot_generator.py) must be generated
- Visual analysis pipeline (stages 1-4) optional but recommended

Usage:
    python ass_test_pipeline.py <document_name1> [document_name2] ...
    python ass_test_pipeline.py DeepWalk
    python ass_test_pipeline.py DeepWalk "Nelson Advanced Functions 12 Textbook"

Example:
    # First run text pipeline
    cd ../
    python test_pipeline.py ../../../docs/DeepWalk.pdf --num_pages 6

    # Generate screenshots (if not already done)
    cd ../ImageBasedProcessing_2
    python stage_1_screenshot_generator.py ../../../docs/DeepWalk.pdf 6 ../ImageBasedProcessing_Claude/DeepWalk/stage_1_screenshots

    # Run visual pipeline (optional)
    cd ../ImageBasedProcessing_Claude/VisualPipeline
    python test_vis_pipeline.py ../../../docs/DeepWalk.pdf --pages 6

    # Then run assembly pipeline
    cd ../AssemblyPipeline
    python ass_test_pipeline.py DeepWalk
"""

import sys
import io
import argparse
from pathlib import Path

# Set UTF-8 encoding for console output (Windows compatibility)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import assembly stages
from ass_stage_1_merge_data import merge_data, save_merged_data
from ass_stage_2_hierarchy import (
    load_merged_data as load_for_stage_2,
    extract_text_only,
    extract_document_hierarchy,
    save_hierarchy_data,
    save_text_payload
)
from ass_stage_3_llm_chunks import (
    load_merged_data as load_for_stage_3,
    assemble_payload_for_pages,
    create_page_batches,
    llm_chunk_payload
)
from ass_stage_4_fts_chunks import load_chunked_data
from ass_stage_5_graph_data import load_chunked_data as load_chunked_for_stage_5, load_merged_data as load_merged_for_stage_5
from openai import OpenAI
from datetime import datetime
import json


def check_prerequisites(document_name: str, base_dir: Path) -> dict:
    """
    Check if required input files exist for the assembly pipeline.

    Args:
        document_name: Name of the document
        base_dir: Base directory (ImageBasedProcessing_Claude)

    Returns:
        Dict with status of prerequisites
    """
    doc_dir = base_dir / document_name

    # Check text pipeline output (Stage 12)
    text_dir = doc_dir / "stage_12_final"
    text_files = list(text_dir.glob("page_*_final.md")) if text_dir.exists() else []

    # Check screenshots from Stage 1
    screenshots_dir = doc_dir / "stage_1_screenshots"
    screenshot_files = list(screenshots_dir.glob("page_*.png")) if screenshots_dir.exists() else []

    # Check visual pipeline output (Stage 3)
    visual_file = base_dir / "VisualPipeline" / document_name / "stage_3_analysis" / "stage_3_analysis_metadata.json"

    status = {
        "text_pipeline": {
            "available": len(text_files) > 0,
            "path": text_dir,
            "files": len(text_files)
        },
        "screenshots": {
            "available": len(screenshot_files) > 0,
            "path": screenshots_dir,
            "files": len(screenshot_files)
        },
        "visual_pipeline": {
            "available": visual_file.exists(),
            "path": visual_file
        },
        "ready": len(text_files) > 0 and len(screenshot_files) > 0  # Both text pipeline and screenshots required
    }

    return status


def run_assembly_pipeline(document_name: str, base_dir: Path = None) -> dict:
    """
    Run the complete assembly pipeline (stages 1-4) for a single document.

    Args:
        document_name: Name of the document (e.g., 'DeepWalk')
        base_dir: Base directory (default: auto-detect)

    Returns:
        Dict with results, or None if processing failed
    """
    # Set base directory
    if base_dir is None:
        base_dir = Path(__file__).parent.parent
    else:
        base_dir = Path(base_dir)

    print("="*80)
    print(f"ASSEMBLY PIPELINE: {document_name}")
    print("="*80)
    print(f"Base directory: {base_dir}")
    print()

    # Check prerequisites
    print("Checking prerequisites...")
    prereqs = check_prerequisites(document_name, base_dir)

    if prereqs["text_pipeline"]["available"]:
        print(f"[OK] Text pipeline: {prereqs['text_pipeline']['files']} MD files found")
    else:
        print(f"[ERROR] Text pipeline not found at: {prereqs['text_pipeline']['path']}")
        print("        Run text extraction pipeline first (stages 1-12)")
        return None

    if prereqs["screenshots"]["available"]:
        print(f"[OK] Screenshots: {prereqs['screenshots']['files']} PNG files found")
    else:
        print(f"[ERROR] Screenshots not found at: {prereqs['screenshots']['path']}")
        print("        Run stage_1_screenshot_generator.py first")
        return None

    if prereqs["visual_pipeline"]["available"]:
        print(f"[OK] Visual pipeline: Found at {prereqs['visual_pipeline']['path']}")
    else:
        print(f"[WARNING] Visual pipeline not found at: {prereqs['visual_pipeline']['path']}")
        print("          Visual analysis will be empty (text only)")

    if not prereqs["ready"]:
        print("\n[ERROR] Prerequisites not met - cannot continue")
        return None

    print()

    # Assembly pipeline directory (where we save outputs)
    assembly_pipeline_dir = Path(__file__).parent
    assembly_base = assembly_pipeline_dir / document_name

    results = {}

    # =========================================================================
    # STAGE 1: Merge Data (FULLY OPERATIONAL)
    # =========================================================================
    print("STAGE 1: Merge Data")
    print("-" * 80)
    try:
        merged_data = merge_data(document_name, base_dir)
        stage_1_dir = assembly_base / "ass_stage_1_merge_data"
        output_path = stage_1_dir / "merged_data.json"
        save_merged_data(merged_data, output_path)

        # Get statistics
        doc_data = merged_data.get(document_name, {})
        page_count = len([k for k in doc_data.keys() if k.startswith("page_")])
        visual_count = sum(
            len(page.get("visual_analysis", {}))
            for page in doc_data.values()
        )

        results['stage_1'] = {
            'status': 'complete',
            'pages': page_count,
            'visual_elements': visual_count,
            'output_file': str(output_path),
            'file_size_kb': output_path.stat().st_size / 1024
        }

        print(f"[OK] Stage 1 complete: {page_count} pages, {visual_count} visual elements")
        print(f"     Output: {output_path} ({results['stage_1']['file_size_kb']:.1f} KB)\n")

    except Exception as e:
        print(f"[ERROR] Stage 1 failed: {e}\n")
        import traceback
        traceback.print_exc()
        return None

    # =========================================================================
    # STAGE 2: Hierarchy Extraction (FULLY OPERATIONAL)
    # =========================================================================
    print("STAGE 2: Hierarchy Extraction")
    print("-" * 80)
    try:
        # Load merged data from Stage 1
        merged_path = stage_1_dir / "merged_data.json"
        merged_data_for_hierarchy = load_for_stage_2(merged_path)

        doc_data = merged_data_for_hierarchy.get(document_name, {})
        page_count = len([k for k in doc_data.keys() if k.startswith("page_")])

        print(f"[OK] Loaded merged data: {page_count} pages")

        # Extract text-only content
        text_only = extract_text_only(doc_data)
        total_chars = sum(len(text) for text in text_only.values())
        print(f"[OK] Extracted text content: {total_chars:,} characters")

        # Get screenshots directory
        screenshots_dir = base_dir / document_name / "stage_1_screenshots"
        print(f"[OK] Using screenshots from: {screenshots_dir}")

        # Initialize OpenAI client
        client = OpenAI()

        # Extract hierarchy with screenshots
        hierarchy_data = extract_document_hierarchy(document_name, text_only, screenshots_dir, client)

        # Calculate statistics
        total_headings = sum(
            len(page.get("headings", []))
            for page in hierarchy_data["hierarchy"].values()
        )
        total_sections = sum(
            len(page.get("sections", []))
            for page in hierarchy_data["hierarchy"].values()
        )

        # Save hierarchy data
        stage_2_dir = assembly_base / "ass_stage_2_hierarchy"
        hierarchy_output_path = stage_2_dir / "hierarchy_data.json"
        save_hierarchy_data(hierarchy_data, hierarchy_output_path)

        # Save text payload
        payload_output = stage_2_dir / f"{document_name}_hierarchy_payload.json"
        save_text_payload(text_only, document_name, payload_output)

        results['stage_2'] = {
            'status': 'complete',
            'pages': page_count,
            'headings': total_headings,
            'sections': total_sections,
            'output_file': str(hierarchy_output_path),
            'payload_file': str(payload_output),
            'file_size_kb': hierarchy_output_path.stat().st_size / 1024
        }

        print(f"[OK] Stage 2 complete: {total_headings} headings, {total_sections} sections")
        print(f"     Output: {hierarchy_output_path} ({results['stage_2']['file_size_kb']:.1f} KB)")
        print(f"     Payload: {payload_output}\n")

    except Exception as e:
        print(f"[ERROR] Stage 2 failed: {e}\n")
        import traceback
        traceback.print_exc()
        results['stage_2'] = {'status': 'failed', 'error': str(e)}
        return None

    # =========================================================================
    # STAGE 3: LLM Chunks (FULLY OPERATIONAL)
    # =========================================================================
    print("STAGE 3: LLM Chunks")
    print("-" * 80)
    try:
        # Load merged data from Stage 1
        merged_path = stage_1_dir / "merged_data.json"
        merged_data = load_for_stage_3(merged_path)

        doc_data = merged_data.get(document_name, {})
        page_count = len([k for k in doc_data.keys() if k.startswith("page_")])

        print(f"[OK] Loaded merged data: {page_count} pages")

        # Create page batches (2 pages per batch)
        batches = create_page_batches(page_count, max_batch_size=2)
        print(f"[OK] Created {len(batches)} batch(es) (2 pages per batch)")

        # Initialize OpenAI client (reuse if already created)
        if 'client' not in locals():
            client = OpenAI()

        # Process each batch
        all_payloads = []
        all_chunked_data = []
        total_tokens = 0

        for i, batch_pages in enumerate(batches, start=1):
            print(f"\n  Batch {i}/{len(batches)}: Pages {batch_pages[0]}-{batch_pages[-1]}")

            # Assemble payload
            payload = assemble_payload_for_pages(doc_data, batch_pages)

            char_count = len(payload)
            figure_count = payload.count("<figure>")
            min_chunks = int(char_count / 900)
            max_chunks = int(char_count / 700)

            print(f"    - Characters: {char_count:,}")
            print(f"    - Figures: {figure_count}")
            print(f"    - Chunk range: {min_chunks}-{max_chunks}")

            # Save payload metadata
            all_payloads.append({
                "batch_id": i,
                "pages": batch_pages,
                "payload": payload,
                "stats": {
                    "char_count": char_count,
                    "figure_count": figure_count,
                    "min_chunks": min_chunks,
                    "max_chunks": max_chunks
                }
            })

            # Chunk with LLM
            chunked_result = llm_chunk_payload(payload, min_chunks, max_chunks, client)

            num_chunks = len(chunked_result.get("chunks", []))
            avg_chunk_size = sum(c.get("char_count", 0) for c in chunked_result["chunks"]) / num_chunks if num_chunks > 0 else 0
            batch_tokens = chunked_result['_meta']['total_tokens']
            total_tokens += batch_tokens

            print(f"    [OK] Created {num_chunks} chunks (avg: {avg_chunk_size:.0f} chars)")
            print(f"    - Tokens: {batch_tokens:,}")

            # Store chunked data
            all_chunked_data.append({
                "batch_id": i,
                "pages": batch_pages,
                "chunks": chunked_result["chunks"],
                "metadata": chunked_result["_meta"]
            })

        # Create Stage 3 output directory
        stage_3_dir = assembly_base / "ass_stage_3_llm_chunks"
        stage_3_dir.mkdir(parents=True, exist_ok=True)

        # Save payloads
        payload_output = stage_3_dir / f"{document_name}_payloads.json"
        with open(payload_output, "w", encoding="utf-8") as f:
            json.dump(all_payloads, f, indent=2, ensure_ascii=False)

        # Save chunked data
        chunked_output_path = stage_3_dir / "chunked_data.json"
        chunked_output = {
            "document": document_name,
            "total_pages": page_count,
            "total_batches": len(batches),
            "total_chunks": sum(len(batch["chunks"]) for batch in all_chunked_data),
            "batches": all_chunked_data,
            "generated_at": datetime.now().isoformat()
        }

        with open(chunked_output_path, "w", encoding="utf-8") as f:
            json.dump(chunked_output, f, indent=2, ensure_ascii=False)

        results['stage_3'] = {
            'status': 'complete',
            'pages': page_count,
            'batches': len(batches),
            'chunks': chunked_output['total_chunks'],
            'total_tokens': total_tokens,
            'output_file': str(chunked_output_path),
            'payloads_file': str(payload_output),
            'file_size_kb': chunked_output_path.stat().st_size / 1024
        }

        print(f"\n[OK] Stage 3 complete: {chunked_output['total_chunks']} chunks across {len(batches)} batches")
        print(f"     Output: {chunked_output_path} ({results['stage_3']['file_size_kb']:.1f} KB)")
        print(f"     Payloads: {payload_output}")
        print(f"     Total tokens: {total_tokens:,}\n")

    except Exception as e:
        print(f"[ERROR] Stage 3 failed: {e}\n")
        import traceback
        traceback.print_exc()
        results['stage_3'] = {'status': 'failed', 'error': str(e)}
        return None

    # =========================================================================
    # STAGE 4: FTS Preparation (BOILERPLATE ONLY)
    # =========================================================================
    print("STAGE 4: FTS Preparation")
    print("-" * 80)
    print("[SKIP] Stage 4 requires Stage 3 output (chunked_data.json)")
    print("[TODO] FTS preparation logic not yet implemented\n")

    results['stage_4'] = {
        'status': 'skipped',
        'reason': 'requires_stage_3_output'
    }

    # =========================================================================
    # STAGE 5: Graph Payload (BOILERPLATE ONLY)
    # =========================================================================
    print("STAGE 5: Graph Database Preparation")
    print("-" * 80)
    print("[SKIP] Stage 5 requires Stage 3 output (chunked_data.json)")
    print("[TODO] Graph payload creation logic not yet implemented\n")

    results['stage_5'] = {
        'status': 'skipped',
        'reason': 'requires_stage_3_output'
    }

    # =========================================================================
    # Pipeline Complete
    # =========================================================================
    print("="*80)
    print(f"ASSEMBLY PIPELINE COMPLETE: {document_name}")
    print("="*80)
    print(f"Assembly directory: {assembly_base}")
    print()
    print("Current Status:")
    print("  [OK] Stage 1: Merge Data - OPERATIONAL")
    print("  [OK] Stage 2: Hierarchy Extraction - OPERATIONAL")
    print("  [OK] Stage 3: LLM Chunks - OPERATIONAL")
    print("  [TODO] Stage 4: FTS Preparation - BOILERPLATE ONLY")
    print("  [TODO] Stage 5: Graph Payload - BOILERPLATE ONLY")
    print()

    return {
        'document_name': document_name,
        'assembly_dir': str(assembly_base),
        'results': results
    }


def main():
    """Run assembly pipeline on documents provided as command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Run assembly pipeline on processed documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Prerequisites:
  Both text extraction and visual analysis pipelines must be completed first.

Examples:
  python ass_test_pipeline.py DeepWalk
  python ass_test_pipeline.py DeepWalk "Nelson Advanced Functions 12 Textbook"
  python ass_test_pipeline.py --base-dir /path/to/base DeepWalk
        """
    )

    parser.add_argument(
        'documents',
        nargs='+',
        help='Document name(s) to process (must match folder names)'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default=None,
        help='Base directory containing document folders (default: auto-detect)'
    )

    args = parser.parse_args()

    # Set base directory
    if args.base_dir:
        base_dir = Path(args.base_dir)
    else:
        # Auto-detect: go up from AssemblyPipeline to ImageBasedProcessing_Claude
        base_dir = Path(__file__).parent.parent

    document_names = args.documents

    print("="*80)
    print("ASSEMBLY PIPELINE PROCESSING")
    print("="*80)
    print(f"Base directory: {base_dir}")
    print(f"Processing {len(document_names)} document(s)")
    print()

    all_results = []

    for doc_name in document_names:
        result = run_assembly_pipeline(doc_name, base_dir)
        if result:
            all_results.append(result)
        print()  # Blank line between documents

    # =========================================================================
    # Summary
    # =========================================================================
    print("="*80)
    print("PROCESSING SUMMARY")
    print("="*80)
    print(f"Successfully processed: {len(all_results)}/{len(document_names)} documents")
    print()

    for result in all_results:
        doc_name = result['document_name']
        stage_1 = result['results'].get('stage_1', {})
        stage_2 = result['results'].get('stage_2', {})
        stage_3 = result['results'].get('stage_3', {})
        stage_4 = result['results'].get('stage_4', {})
        stage_5 = result['results'].get('stage_5', {})

        print(f"{doc_name}:")

        # Stage 1
        if stage_1.get('status') == 'complete':
            print(f"  Stage 1 - Merge: {stage_1['pages']} pages, "
                  f"{stage_1['visual_elements']} visual elements "
                  f"({stage_1['file_size_kb']:.1f} KB)")
        else:
            print(f"  Stage 1 - Merge: Failed")

        # Stage 2
        if stage_2.get('status') == 'complete':
            print(f"  Stage 2 - Hierarchy: {stage_2['headings']} headings, "
                  f"{stage_2['sections']} sections "
                  f"({stage_2['file_size_kb']:.1f} KB)")
        elif stage_2.get('status') == 'failed':
            print(f"  Stage 2 - Hierarchy: Failed - {stage_2.get('error', 'Unknown error')}")
        else:
            print(f"  Stage 2 - Hierarchy: {stage_2.get('status', 'unknown')}")

        # Stage 3
        if stage_3.get('status') == 'complete':
            print(f"  Stage 3 - LLM Chunks: {stage_3['chunks']} chunks, "
                  f"{stage_3['batches']} batches, "
                  f"{stage_3['total_tokens']:,} tokens "
                  f"({stage_3['file_size_kb']:.1f} KB)")
        elif stage_3.get('status') == 'failed':
            print(f"  Stage 3 - LLM Chunks: Failed - {stage_3.get('error', 'Unknown error')}")
        else:
            print(f"  Stage 3 - LLM Chunks: {stage_3.get('status', 'unknown')}")

        # Stage 4
        print(f"  Stage 4 - FTS: {stage_4.get('status', 'unknown')}")

        # Stage 5
        print(f"  Stage 5 - Graph: {stage_5.get('status', 'unknown')}")

        print(f"  Output: {result['assembly_dir']}")
        print()

    # Final notes
    if all_results:
        print("Next Steps:")
        print("  1. [DONE] Stage 1: Merge Data")
        print("  2. [DONE] Stage 2: Hierarchy Extraction")
        print("  3. [DONE] Stage 3: LLM Chunking")
        print("  4. [TODO] Stage 4: FTS Preparation (embedding generation)")
        print("  5. [TODO] Stage 5: Graph Payload Creation")
        print()


if __name__ == "__main__":
    main()
