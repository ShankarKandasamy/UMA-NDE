"""
Assembly Stage 3: LLM-based Intelligent Chunking

Takes merged data from Stage 1 and hierarchy from Stage 2, then creates
semantic chunks using GPT-4o. Chunks are optimized for RAG retrieval
with 200-400 token target sizes.

Input:
    - Merged JSON: AssemblyPipeline/{doc}/ass_stage_1_merge_data/merged_data.json
    - Hierarchy JSON (optional): AssemblyPipeline/{doc}/ass_stage_2_hierarchy/hierarchy_data.json

Output:
    - Chunked JSON: AssemblyPipeline/{doc}/ass_stage_3_llm_chunks/chunked_data.json
    - Payloads JSON: AssemblyPipeline/{doc}/ass_stage_3_llm_chunks/{doc}_payloads.json

Usage:
    python ass_stage_3_llm_chunks.py DeepWalk
    python ass_stage_3_llm_chunks.py DeepWalk --hierarchy-file path/to/hierarchy_data.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from openai import OpenAI
from datetime import datetime


def load_merged_data(merged_file: Path) -> dict:
    """Load merged data from Stage 1."""
    if not merged_file.exists():
        raise FileNotFoundError(f"Merged data file not found: {merged_file}")

    with open(merged_file, "r", encoding="utf-8") as f:
        return json.load(f)


def assemble_payload_for_pages(doc_data: dict, page_numbers: list[int]) -> str:
    """
    Assemble payload for a batch of pages.

    Args:
        doc_data: Document data from merged_data.json
        page_numbers: List of page numbers to include in this batch

    Returns:
        Formatted payload string combining text content and figures
    """
    payload_parts = []

    for page_num in page_numbers:
        page_key = f"page_{page_num}"

        if page_key not in doc_data:
            continue

        page_data = doc_data[page_key]

        # Add text content
        text_content = page_data.get("text_content", "")
        if text_content:
            payload_parts.append(f"<text_content>\n{text_content}\n</text_content>\n")

        # Add figures from visual_analysis
        visual_analysis = page_data.get("visual_analysis", {})

        for item_key, item_data in visual_analysis.items():
            # Extract visual analysis data
            visual_data = item_data.get("visual_analysis", {})

            if not visual_data:
                continue

            # Extract fields
            subcategory = visual_data.get("subcategory", "")
            description = visual_data.get("description", "")
            summary = visual_data.get("summary", "")
            key_insights = visual_data.get("key_insights", [])

            # Format key_insights as string
            if isinstance(key_insights, list):
                key_insights_str = "\n".join(f"- {insight}" for insight in key_insights)
            else:
                key_insights_str = str(key_insights)

            # Build figure section
            figure_section = f"""<figure>
<subcategory>{subcategory}</subcategory>

description: {description}
summary: {summary}
key_insights:
{key_insights_str}

</figure>
"""
            payload_parts.append(figure_section)

    return "\n".join(payload_parts)


def create_page_batches(page_count: int, max_batch_size: int = 2) -> list[list[int]]:
    """
    Split pages into batches of max_batch_size.

    Args:
        page_count: Total number of pages
        max_batch_size: Maximum pages per batch (default 2)
                        Note: Reduced from 10 to 2 to avoid API timeouts.
                        Large batches cause the model to hang due to complexity overload.
                        Testing shows: 15k chars works, 19k+ hangs.
                        2 pages ≈ 12k chars (safe), 3 pages ≈ 18k chars (risky).

    Returns:
        List of page number lists (each list is a batch)
    """
    batches = []
    for i in range(1, page_count + 1, max_batch_size):
        batch = list(range(i, min(i + max_batch_size, page_count + 1)))
        batches.append(batch)
    return batches


def llm_chunk_payload(payload: str, min_chunks: int, max_chunks: int, client: OpenAI, max_retries: int = 3) -> dict:
    """
    Use GPT-4o-mini to intelligently chunk the payload into semantic segments.

    Args:
        payload: The assembled text content with figures
        min_chunks: Minimum number of chunks to create
        max_chunks: Maximum number of chunks to create
        client: OpenAI client instance
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary containing chunks list and metadata
    """
    system_prompt = """You are an expert at semantic text chunking for RAG systems.
Your task is to divide document content into semantically coherent chunks optimized for retrieval.

Guidelines:
- Each chunk should represent a complete semantic unit (e.g., a section, subsection, or coherent topic)
- Target chunk size: 700-900 characters
- Preserve context and coherence within each chunk
- Include relevant figures with their associated text content
- Maintain markdown formatting and structure
- Ensure chunks are self-contained and meaningful when read independently
"""

    user_prompt = f"""Please divide the following document content into {min_chunks} to {max_chunks} semantic chunks.

Target: Create chunks in the 700-900 character range that maintain semantic coherence.

Return your response as a JSON object with this structure:
{{
  "chunks": [
    {{
      "chunk_id": 1,
      "content": "chunk text here...",
      "char_count": 850,
      "semantic_type": "section/subsection/figure/mixed"
    }},
    ...
  ]
}}

Document content:
{payload}
"""

    print(f"    Sending to GPT-4o-mini for chunking...")

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Add metadata
            result["_meta"] = {
                "model": "gpt-4o-mini",
                "timestamp": datetime.now().isoformat(),
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "target_range": {"min_chunks": min_chunks, "max_chunks": max_chunks}
            }

            return result

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"    [WARN] Attempt {attempt + 1} failed: {e}")
                print(f"    Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Failed after {max_retries} attempts: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Create semantic chunks from merged document data"
    )
    parser.add_argument(
        "document",
        help="Document name"
    )
    parser.add_argument(
        "--input",
        help="Input merged JSON file (default: AssemblyPipeline/{doc}/ass_stage_1_merge_data/merged_data.json)"
    )
    parser.add_argument(
        "--hierarchy-file",
        help="Input hierarchy JSON file (default: AssemblyPipeline/{doc}/ass_stage_2_hierarchy/hierarchy_data.json)"
    )
    parser.add_argument(
        "--output",
        help="Output chunked JSON file (default: AssemblyPipeline/{doc}/ass_stage_3_llm_chunks/chunked_data.json)"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory (default: auto-detect)"
    )

    args = parser.parse_args()

    # Set base directory (for reading text/visual pipelines if needed)
    base_dir = Path(args.base_dir) if args.base_dir else Path(__file__).parent.parent

    # Assembly pipeline directory
    assembly_pipeline_dir = Path(__file__).parent

    # Determine input path
    if args.input:
        input_path = Path(args.input)
    else:
        input_path = assembly_pipeline_dir / args.document / "ass_stage_1_merge_data" / "merged_data.json"

    # Determine hierarchy file path (optional)
    if args.hierarchy_file:
        hierarchy_path = Path(args.hierarchy_file)
    else:
        hierarchy_path = assembly_pipeline_dir / args.document / "ass_stage_2_hierarchy" / "hierarchy_data.json"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = assembly_pipeline_dir / args.document / "ass_stage_3_llm_chunks" / "chunked_data.json"

    print(f"\n{'='*80}")
    print(f"ASSEMBLY STAGE 3: LLM CHUNKING")
    print(f"{'='*80}\n")
    print(f"Document: {args.document}")
    print(f"Input: {input_path}")
    print(f"Hierarchy: {hierarchy_path} {'(exists)' if hierarchy_path.exists() else '(not found)'}")
    print(f"Output: {output_path}\n")

    # Load merged data
    try:
        print("Loading merged data from Stage 1...")
        merged_data = load_merged_data(input_path)
        print(f"[OK] Loaded merged data: {len(merged_data)} document(s)")

        # Get document data
        doc_data = merged_data.get(args.document, {})
        if not doc_data:
            print(f"\n[ERROR] Document '{args.document}' not found in merged data")
            sys.exit(1)

        page_count = len([k for k in doc_data.keys() if k.startswith("page_")])
        print(f"[OK] Document has {page_count} pages")

    except Exception as e:
        print(f"\n[ERROR] Failed to load merged data: {e}")
        sys.exit(1)

    # Create page batches
    print(f"\nCreating page batches (max 2 pages per batch)...")
    batches = create_page_batches(page_count, max_batch_size=2)
    print(f"[OK] Created {len(batches)} batch(es)")

    # Initialize OpenAI client
    print(f"\nInitializing OpenAI client...")
    client = OpenAI()
    print(f"[OK] Client initialized")

    # Assemble payloads and chunk each batch
    print(f"\nAssembling payloads for {len(batches)} batch(es)...")
    all_payloads = []
    all_chunked_data = []

    for i, batch_pages in enumerate(batches, start=1):
        print(f"\n  Batch {i}: Pages {batch_pages[0]}-{batch_pages[-1]}")
        payload = assemble_payload_for_pages(doc_data, batch_pages)

        # Print payload stats
        line_count = payload.count("\n")
        char_count = len(payload)
        figure_count = payload.count("<figure>")
        min_chunks = int(char_count / 900)
        max_chunks = int(char_count / 700)

        print(f"    - Characters: {char_count:,}")
        print(f"    - Lines: {line_count:,}")
        print(f"    - Figures: {figure_count}")
        print(f"    - Chunk range: {min_chunks}-{max_chunks}")

        # Save payload data
        all_payloads.append({
            "batch_id": i,
            "pages": batch_pages,
            "payload": payload,
            "stats": {
                "char_count": char_count,
                "line_count": line_count,
                "figure_count": figure_count,
                "min_chunks": min_chunks,
                "max_chunks": max_chunks
            }
        })

        # Chunk with LLM
        try:
            chunked_result = llm_chunk_payload(payload, min_chunks, max_chunks, client)

            num_chunks = len(chunked_result.get("chunks", []))
            avg_chunk_size = sum(c.get("char_count", 0) for c in chunked_result["chunks"]) / num_chunks if num_chunks > 0 else 0

            print(f"    [OK] Created {num_chunks} chunks (avg: {avg_chunk_size:.0f} chars)")
            print(f"    - Tokens used: {chunked_result['_meta']['total_tokens']:,}")

            # Store chunked data
            all_chunked_data.append({
                "batch_id": i,
                "pages": batch_pages,
                "chunks": chunked_result["chunks"],
                "metadata": chunked_result["_meta"]
            })

        except Exception as e:
            print(f"    [ERROR] Chunking failed: {e}")
            sys.exit(1)

    # Save payloads for inspection
    payload_output = output_path.parent / f"{args.document}_payloads.json"
    print(f"\nSaving payloads to: {payload_output}")

    with open(payload_output, "w", encoding="utf-8") as f:
        json.dump(all_payloads, f, indent=2, ensure_ascii=False)

    print(f"[OK] Saved {len(all_payloads)} payload(s)")

    # Save chunked data
    print(f"\nSaving chunked data to: {output_path}")

    chunked_output = {
        "document": args.document,
        "total_pages": page_count,
        "total_batches": len(batches),
        "total_chunks": sum(len(batch["chunks"]) for batch in all_chunked_data),
        "batches": all_chunked_data,
        "generated_at": datetime.now().isoformat()
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunked_output, f, indent=2, ensure_ascii=False)

    print(f"[OK] Saved {chunked_output['total_chunks']} chunks across {len(batches)} batch(es)")

    print(f"\n{'='*80}")
    print("Assembly Stage 3 - LLM Chunking Complete")
    print(f"{'='*80}")
    print(f"\nResults:")
    print(f"  - Payloads saved: {payload_output}")
    print(f"  - Chunks saved: {output_path}")
    print(f"  - Total chunks: {chunked_output['total_chunks']}")
    print(f"\nNext: Run Stage 4 for embedding generation\n")


if __name__ == "__main__":
    main()
