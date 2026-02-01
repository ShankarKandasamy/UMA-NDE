"""
Assembly Stage 1: Merge Text and Visual Analysis

Merges extracted text content from Stage 12 (text extraction pipeline) with
visual analysis from Stage 3 (visual pipeline) to create a unified document
representation.

Input:
    - Stage 12 MD files: {doc}/stage_12_final/page_N_final.md
    - Visual Stage 3 JSON: VisualPipeline/{doc}/stage_3_analysis/stage_3_analysis_metadata.json

Output:
    - Merged JSON: AssemblyPipeline/{doc}/ass_stage_1_merge_data/merged_data.json

Output Format:
    {
      "document_name": {
        "page_1": {
          "text_content": "...",
          "visual_analysis": {
            "image_1": {...},
            "table_1": {...},
            ...
          }
        }
      }
    }

Usage:
    python ass_stage_1_merge_data.py DeepWalk
    python ass_stage_1_merge_data.py "Nelson Advanced Functions 12 Textbook"
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def load_stage_12_text(stage_12_dir: Path) -> Dict[str, str]:
    """
    Load text content from Stage 12 MD files.

    Args:
        stage_12_dir: Path to stage_12_final directory

    Returns:
        Dictionary mapping page numbers to text content
        Example: {"1": "# Page 1 content...", "2": "# Page 2 content..."}
    """
    text_content = {}

    if not stage_12_dir.exists():
        print(f"[WARNING] Stage 12 directory not found: {stage_12_dir}")
        return text_content

    # Find all MD files
    md_files = sorted(stage_12_dir.glob("page_*_final.md"))

    if not md_files:
        print(f"[WARNING] No MD files found in {stage_12_dir}")
        return text_content

    for md_file in md_files:
        # Extract page number from filename (page_1_final.md -> "1")
        page_num = md_file.stem.split("_")[1]

        try:
            with open(md_file, "r", encoding="utf-8") as f:
                text_content[page_num] = f.read()
            print(f"[INFO] Loaded text for page {page_num}: {len(text_content[page_num])} chars")
        except Exception as e:
            print(f"[ERROR] Failed to read {md_file}: {e}")

    return text_content


def load_stage_3_visual(stage_3_file: Path) -> Dict[str, List[Dict]]:
    """
    Load visual analysis from Stage 3 JSON.

    Args:
        stage_3_file: Path to stage_3_analysis_metadata.json

    Returns:
        Dictionary mapping page numbers to list of detections
        Example: {"1": [detection1, detection2, ...], "2": [...]}
    """
    visual_data = {}

    if not stage_3_file.exists():
        print(f"[WARNING] Stage 3 file not found: {stage_3_file}")
        return visual_data

    try:
        with open(stage_3_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract detections per page
        for page_data in data.get("pages", []):
            page_num = str(page_data["page_number"])
            detections = page_data.get("detections", [])
            visual_data[page_num] = detections
            print(f"[INFO] Loaded {len(detections)} visual elements for page {page_num}")

    except Exception as e:
        print(f"[ERROR] Failed to read {stage_3_file}: {e}")

    return visual_data


def format_visual_analysis(detections: List[Dict]) -> Dict[str, Dict]:
    """
    Format detections into visual_analysis dictionary with image_N/table_N keys.

    Args:
        detections: List of detection objects from Stage 3

    Returns:
        Dictionary with keys like "image_1", "table_1", etc.
    """
    visual_analysis = {}

    # Track counters for each type
    image_counter = 1
    table_counter = 1

    for detection in detections:
        detection_type = detection.get("type", "").lower()

        # Determine the key name
        if detection_type == "table":
            key = f"table_{table_counter}"
            table_counter += 1
        else:  # Picture or other visual elements
            key = f"image_{image_counter}"
            image_counter += 1

        # Store the complete detection data
        visual_analysis[key] = detection

    return visual_analysis


def merge_document_data(
    document_name: str,
    text_content: Dict[str, str],
    visual_data: Dict[str, List[Dict]]
) -> Dict:
    """
    Merge text and visual data into unified document structure.

    Args:
        document_name: Name of the document (e.g., "DeepWalk")
        text_content: Page number -> text content mapping
        visual_data: Page number -> detections mapping

    Returns:
        Merged document structure
    """
    # Get all unique page numbers
    all_pages = sorted(
        set(text_content.keys()) | set(visual_data.keys()),
        key=int
    )

    document_data = {}

    for page_num in all_pages:
        page_key = f"page_{page_num}"

        # Get text content (default to empty string)
        text = text_content.get(page_num, "")

        # Get visual analysis (default to empty dict)
        detections = visual_data.get(page_num, [])
        visual_analysis = format_visual_analysis(detections)

        document_data[page_key] = {
            "text_content": text,
            "visual_analysis": visual_analysis
        }

        print(f"[INFO] Merged page {page_num}: {len(text)} chars text, {len(visual_analysis)} visual elements")

    return {document_name: document_data}


def merge_data(document_name: str, base_dir: Optional[Path] = None) -> Dict:
    """
    Main merge function.

    Args:
        document_name: Name of the document to merge
        base_dir: Base directory (defaults to ImageBasedProcessing_Claude)

    Returns:
        Merged document data
    """
    # Set up paths
    if base_dir is None:
        base_dir = Path(__file__).parent.parent

    text_pipeline_dir = base_dir / document_name / "stage_12_final"
    visual_pipeline_file = base_dir / "VisualPipeline" / document_name / "stage_3_analysis" / "stage_3_analysis_metadata.json"

    print(f"\n{'='*80}")
    print(f"ASSEMBLY STAGE 1: MERGE TEXT AND VISUAL DATA")
    print(f"{'='*80}\n")
    print(f"Document: {document_name}")
    print(f"Text pipeline: {text_pipeline_dir}")
    print(f"Visual pipeline: {visual_pipeline_file}\n")

    # Load data
    print("[STEP 1] Loading Stage 12 text content...")
    text_content = load_stage_12_text(text_pipeline_dir)

    print(f"\n[STEP 2] Loading Stage 3 visual analysis...")
    visual_data = load_stage_3_visual(visual_pipeline_file)

    # Merge
    print(f"\n[STEP 3] Merging data...")
    merged_data = merge_document_data(document_name, text_content, visual_data)

    print(f"\n[SUCCESS] Merge complete!")
    print(f"Total pages: {len(merged_data[document_name])}")

    return merged_data


def save_merged_data(merged_data: Dict, output_path: Path):
    """
    Save merged data to JSON file.

    Args:
        merged_data: Merged document data
        output_path: Path to save JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="Merge text and visual analysis data"
    )
    parser.add_argument(
        "document",
        help="Document name (e.g., 'DeepWalk', 'Nelson Advanced Functions 12 Textbook')"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output JSON file path (default: AssemblyPipeline/{document}/ass_stage_1_merge_data/merged_data.json)"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory containing document folders (default: auto-detect)"
    )

    args = parser.parse_args()

    # Set base directory
    base_dir = Path(args.base_dir) if args.base_dir else Path(__file__).parent.parent

    # Merge data
    try:
        merged_data = merge_data(args.document, base_dir)
    except Exception as e:
        print(f"\n[ERROR] Merge failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Save to AssemblyPipeline/{document}/ass_stage_1_merge_data/merged_data.json
        assembly_pipeline_dir = Path(__file__).parent
        output_path = assembly_pipeline_dir / args.document / "ass_stage_1_merge_data" / "merged_data.json"

    # Save
    save_merged_data(merged_data, output_path)

    print(f"\n{'='*80}")
    print(f"Assembly Stage 1 Complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
