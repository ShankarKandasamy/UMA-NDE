"""
Assembly Stage 4: Graph Database Preparation

Takes chunked data from Stage 2 and prepares it for graph database ingestion.
Creates extraction payload for entity/edge extraction and claims extraction.

Input:
    - Chunked JSON: {doc}/assembly/chunked_data.json
    - Merged JSON: {doc}/assembly/merged_data.json (for images)

Output:
    - Graph payload JSON: {doc}/assembly/graph_payload.json

Usage:
    python ass_stage_4_graph_data.py DeepWalk
"""

import argparse
import json
import sys
from pathlib import Path


def load_chunked_data(chunked_file: Path) -> dict:
    """Load chunked data from Stage 2."""
    if not chunked_file.exists():
        raise FileNotFoundError(f"Chunked data file not found: {chunked_file}")

    with open(chunked_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_merged_data(merged_file: Path) -> dict:
    """Load merged data from Stage 1."""
    if not merged_file.exists():
        raise FileNotFoundError(f"Merged data file not found: {merged_file}")

    with open(merged_file, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Prepare graph database payload from chunked data"
    )
    parser.add_argument(
        "document",
        help="Document name"
    )
    parser.add_argument(
        "--chunked-input",
        help="Input chunked JSON file (default: {doc}/assembly/chunked_data.json)"
    )
    parser.add_argument(
        "--merged-input",
        help="Input merged JSON file (default: {doc}/assembly/merged_data.json)"
    )
    parser.add_argument(
        "--output",
        help="Output graph payload JSON file (default: {doc}/assembly/graph_payload.json)"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory (default: auto-detect)"
    )

    args = parser.parse_args()

    # Set base directory
    base_dir = Path(args.base_dir) if args.base_dir else Path(__file__).parent.parent

    # Determine input paths
    if args.chunked_input:
        chunked_path = Path(args.chunked_input)
    else:
        chunked_path = base_dir / args.document / "assembly" / "chunked_data.json"

    if args.merged_input:
        merged_path = Path(args.merged_input)
    else:
        merged_path = base_dir / args.document / "assembly" / "merged_data.json"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = base_dir / args.document / "assembly" / "graph_payload.json"

    print(f"\n{'='*80}")
    print(f"ASSEMBLY STAGE 4: GRAPH DATABASE PREPARATION")
    print(f"{'='*80}\n")
    print(f"Document: {args.document}")
    print(f"Chunked input: {chunked_path}")
    print(f"Merged input: {merged_path}")
    print(f"Output: {output_path}\n")

    # Load data
    try:
        print("Loading chunked data from Stage 2...")
        chunked_data = load_chunked_data(chunked_path)
        print("[OK] Loaded chunked data")

        # Display chunk info if available
        chunks = chunked_data.get("chunks", [])
        if chunks:
            print(f"[OK] Found {len(chunks)} chunks")

        print("\nLoading merged data from Stage 1...")
        merged_data = load_merged_data(merged_path)
        print(f"[OK] Loaded merged data: {len(merged_data)} document(s)")

    except Exception as e:
        print(f"\n[ERROR] Failed to load input data: {e}")
        sys.exit(1)

    print("\n[TODO] Graph payload creation logic not yet implemented")
    print(f"\n{'='*80}")
    print("Assembly Stage 4 - Ready for Implementation")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
