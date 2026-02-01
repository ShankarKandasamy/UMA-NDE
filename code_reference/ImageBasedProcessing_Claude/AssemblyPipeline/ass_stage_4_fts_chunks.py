"""
Assembly Stage 3: Full-Text Search (FTS) Preparation

Takes chunked data from Stage 2 and creates embeddings for vector search.
Prepares data in ChromaDB-ready format.

Input:
    - Chunked JSON: {doc}/assembly/chunked_data.json

Output:
    - FTS-ready JSON: {doc}/assembly/fts_ready.json

Usage:
    python ass_stage_3_fts_chunks.py DeepWalk
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


def main():
    parser = argparse.ArgumentParser(
        description="Prepare chunks for full-text search with embeddings"
    )
    parser.add_argument(
        "document",
        help="Document name"
    )
    parser.add_argument(
        "--input",
        help="Input chunked JSON file (default: {doc}/assembly/chunked_data.json)"
    )
    parser.add_argument(
        "--output",
        help="Output FTS JSON file (default: {doc}/assembly/fts_ready.json)"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory (default: auto-detect)"
    )

    args = parser.parse_args()

    # Set base directory
    base_dir = Path(args.base_dir) if args.base_dir else Path(__file__).parent.parent

    # Determine input path
    if args.input:
        input_path = Path(args.input)
    else:
        input_path = base_dir / args.document / "assembly" / "chunked_data.json"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = base_dir / args.document / "assembly" / "fts_ready.json"

    print(f"\n{'='*80}")
    print(f"ASSEMBLY STAGE 3: FTS PREPARATION")
    print(f"{'='*80}\n")
    print(f"Document: {args.document}")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}\n")

    # Load chunked data
    try:
        print("Loading chunked data from Stage 2...")
        chunked_data = load_chunked_data(input_path)
        print("[OK] Loaded chunked data")

        # Display chunk info if available
        chunks = chunked_data.get("chunks", [])
        if chunks:
            print(f"[OK] Found {len(chunks)} chunks")

    except Exception as e:
        print(f"\n[ERROR] Failed to load chunked data: {e}")
        sys.exit(1)

    print("\n[TODO] FTS preparation logic not yet implemented")
    print(f"\n{'='*80}")
    print("Assembly Stage 3 - Ready for Implementation")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
