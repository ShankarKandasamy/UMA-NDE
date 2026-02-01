"""
Assembly Stage 2: Hierarchy Extraction

Extracts document hierarchy (headings, sections, structure) from merged data
using GPT-4o-mini with visual verification. Uses screenshots and previous page
context to accurately determine heading levels across page boundaries.

Input:
    - Merged JSON: AssemblyPipeline/{doc}/ass_stage_1_merge_data/merged_data.json
    - Screenshots: Pre-generated from stage_1_screenshot_generator.py (from text pipeline)

Output:
    - Hierarchy JSON: AssemblyPipeline/{doc}/ass_stage_2_hierarchy/hierarchy_data.json
    - Corrected Markdown: AssemblyPipeline/{doc}/ass_stage_2_hierarchy/{doc}_corrected.md
    - Text Payload: AssemblyPipeline/{doc}/ass_stage_2_hierarchy/{doc}_hierarchy_payload.json

Output Format (hierarchy_data.json):
    {
      "document_name": "DeepWalk",
      "total_pages": 6,
      "hierarchy": {
        "page_1": {
          "corrected_markdown": "# DeepWalk\n\n## Introduction...",
          "headings": [
            {"level": 1, "text": "DeepWalk", "char_start": 0, "char_end": 9},
            {"level": 2, "text": "Introduction", "char_start": 150, "char_end": 162}
          ],
          "sections": [
            {"title": "Introduction", "heading_level": 2,
             "char_start": 150, "char_end": 500, "subsections": []}
          ],
          "metadata": {
            "structure_type": "academic_paper",
            "has_numbered_sections": true,
            "total_headings": 5
          }
        }
      }
    }

Output Format (hierarchy_payload.json):
    {
      "document_name": "DeepWalk",
      "total_pages": 6,
      "pages": {
        "page_1": {
          "text_content": "# Markdown text...",
          "char_count": 1500,
          "word_count": 250,
          "line_count": 45
        }
      },
      "statistics": {...}
    }

Usage:
    python ass_stage_2_hierarchy.py DeepWalk --screenshots backend/development/ImageBasedProcessing_Claude/DeepWalk/stage_1_screenshots
    python ass_stage_2_hierarchy.py "Nelson Advanced Functions 12 Textbook" --screenshots path/to/screenshots
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from openai import OpenAI
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_vlm_client(provider: str = "openai"):
    """
    Initialize the appropriate VLM client based on provider.

    Args:
        provider: One of "openai", "together", "fireworks", "replicate"

    Returns:
        Initialized client instance
    """
    if provider == "openai":
        return OpenAI()
    elif provider == "together":
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz/v1"
        )
    elif provider == "fireworks":
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError("FIREWORKS_API_KEY not found in environment")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1"
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_model_name(provider: str, model: str = None):
    """
    Get the model identifier for the provider.

    Args:
        provider: One of "openai", "together", "fireworks"
        model: Optional specific model override

    Returns:
        Model identifier string
    """
    if model:
        return model

    # Default models by provider
    defaults = {
        "openai": "gpt-4o-mini",  # Fast, accurate, cost-effective
        "together": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        "fireworks": "accounts/fireworks/models/qwen2-vl-72b-instruct"
    }

    return defaults.get(provider, "gpt-4o-mini")


def load_merged_data(merged_file: Path) -> dict:
    """Load merged data from Stage 1."""
    if not merged_file.exists():
        raise FileNotFoundError(f"Merged data file not found: {merged_file}")

    with open(merged_file, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text_only(doc_data: dict) -> Dict[str, str]:
    """
    Extract only text_content from merged data (strip visual_analysis).

    Args:
        doc_data: Document data from merged_data.json

    Returns:
        Dictionary mapping page keys to text content
        Example: {"page_1": "# DeepWalk...", "page_2": "..."}
    """
    text_only = {}

    for page_key, page_data in doc_data.items():
        if not page_key.startswith("page_"):
            continue

        text_content = page_data.get("text_content", "")
        text_only[page_key] = text_content

    return text_only


def find_screenshot_for_page(screenshots_dir: Path, page_num: int) -> Path:
    """
    Find pre-generated screenshot for a given page number.

    Args:
        screenshots_dir: Directory containing screenshots from stage_1_screenshot_generator.py
        page_num: Page number (1-indexed, e.g., 1, 2, 3...)

    Returns:
        Path to screenshot file (page_{N}_*.png)

    Raises:
        FileNotFoundError: If screenshot not found for page
    """
    # Pattern: page_1_DeepWalk.png, page_2_DeepWalk.png, etc.
    pattern = f"page_{page_num}_*.png"
    matches = list(screenshots_dir.glob(pattern))

    if not matches:
        raise FileNotFoundError(
            f"Screenshot not found for page {page_num} in {screenshots_dir}\n"
            f"Expected pattern: {pattern}"
        )

    if len(matches) > 1:
        print(f"    [WARN] Multiple screenshots found for page {page_num}, using: {matches[0].name}")

    return matches[0]


def extract_hierarchy_with_llm(
    text_content: str,
    page_key: str,
    screenshot_path: Path,
    previous_corrected_markdown: Optional[str],
    client: OpenAI,
    model_name: str = "gpt-4o",
    max_retries: int = 3
) -> dict:
    """
    Use VLM with vision to extract document hierarchy from text and screenshot.

    Args:
        text_content: Text content for a single page
        page_key: Page identifier (e.g., "page_1")
        screenshot_path: Path to pre-generated screenshot from stage_1
        previous_corrected_markdown: Corrected markdown from previous page (None for page 1)
        client: OpenAI-compatible client instance
        model_name: Model identifier (e.g., "gpt-4o", "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo")
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary containing hierarchy structure for the page
    """
    system_prompt = """You are a Markdown structure repair engine with VISUAL VERIFICATION.

You will receive:
1. Markdown text content for the current page
2. A screenshot of the current page
3. (Optional) The corrected markdown from the PREVIOUS page

Your job is to RETURN the same Markdown with corrected heading markup ONLY.

CROSS-PAGE CONTEXT:
- Use the previous page's headings to understand the hierarchical context
- A heading at the start of a new page is often a CONTINUATION of the previous structure
- Example: If previous page ends with "## 2.3 Methods", a new page starting with
  "Experimental Setup" is likely "### 2.3.1 Experimental Setup" (not H1 or H2)
- Section numbering patterns are STRONG indicators (e.g., "2.3.1" is child of "2.3")

VISUAL VERIFICATION:
- Use the screenshot to verify heading levels by visual styling (font size, weight, spacing)
- Larger/bolder text = higher-level heading
- Compare relative font sizes to distinguish H1 from H2, H2 from H3, etc.
- Pay attention to vertical spacing (more space before/after = higher-level heading)

CRITICAL: REMOVE # MARKERS FROM NON-HEADINGS
These are NOT headings and MUST have # markers removed:

1. **Figure/Chart titles** - Titles above figures/charts/graphs
   - Example: "# Frequency of Vertex Occurrence in Random Walks" → Remove #
   - Pattern: Descriptive title followed by figure/chart content, axis labels, or legend

2. **Algorithm labels** - Algorithm pseudocode headers
   - Example: "# Algorithm 1 DEEPWALK(G, d, γ, t)" → Remove #
   - Pattern: "Algorithm [number]" followed by function signature and pseudocode steps
   - Also applies to: Procedure, Function, Method labels

3. **Figure captions** - Text describing figures/images
   - Example: "# Figure 1: Sample visualization" → Remove #
   - Pattern: "Figure [number]:", "Table [number]:", "Chart [number]:"

4. **List item headers** - Enumerated items in numbered/bulleted lists
   - Example: "# Step 1: Initialize" in a numbered list → Remove #

5. **Code block titles** - Titles above code examples
   - Example: "# Example Implementation" above code fence → Remove #

Hard rules:
- Preserve all non-heading text EXACTLY (character-for-character). Do not reword, paraphrase, delete, or reorder body text.
- Do not change punctuation, spacing, or line breaks in non-heading lines.
- You may only edit:
  1) Heading level markers (# count) on existing heading lines
  2) Remove heading markers from non-headings (figure captions, algorithm labels, list items)
  3) (Optional) Add heading markers ONLY when clearly present but untagged
- Keep heading levels within H1–H4 only.
- Output MUST be valid Markdown.

"""

    # Build user prompt with optional previous page context
    user_prompt_parts = []

    if previous_corrected_markdown:
        user_prompt_parts.append(f"""PREVIOUS PAGE CONTEXT:
Below is the corrected markdown from the PREVIOUS page. Use this to understand
the hierarchical context for headings at the start of the current page.

```markdown
{previous_corrected_markdown[-2000:]}
```

""")

    user_prompt_parts.append(f"""CURRENT PAGE ANALYSIS:
Analyze the Markdown below and the provided screenshot to extract hierarchical structure.

TASKS:
1. Correct heading markup:
   - Fix heading levels using BOTH previous page context AND visual cues from screenshot
   - Remove # markers from non-headings (figure captions, algorithm steps, lists)
   - Preserve heading text exactly; only adjust leading # markers

2. Extract headings:
   - Identify all H1-H4 headings with exact character positions
   - Use numbering patterns as strong cues for hierarchy
   - Cross-reference with screenshot to verify font size/weight

3. Identify sections:
   - Section starts at its heading and ends before next same/higher-level heading
   - Include parent-child relationships

4. Classify document type:
   - One of: academic_paper, textbook, technical_report, legal_document, narrative, other

CONSTRAINTS:
- Preserve all non-heading text character-for-character
- For headings: preserve text exactly, only adjust # markers
- Character positions must be exact offsets in the corrected markdown string

OUTPUT FORMAT (strict JSON):
{{
  "corrected_markdown": "Full corrected markdown text...",
  "headings": [...],
  "sections": [...],
  "metadata": {{...}}
}}

Markdown input for CURRENT page:
{text_content}
""")

    user_prompt = "\n".join(user_prompt_parts)

    print(f"    Sending {page_key} to {model_name} for hierarchy extraction...")

    # Read and encode screenshot
    with open(screenshot_path, "rb") as f:
        screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Build messages with screenshot
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{screenshot_b64}",
                        "detail": "low"  # Low-detail mode for faster processing with large images
                    }
                }
            ]
        }
    ]

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Validate required fields
            required_fields = ["corrected_markdown", "headings", "sections", "metadata"]
            missing_fields = [f for f in required_fields if f not in result]

            if missing_fields:
                raise ValueError(f"Response missing required fields: {missing_fields}")

            # Ensure metadata has required subfields
            if "metadata" in result:
                metadata = result["metadata"]
                if "structure_type" not in metadata:
                    metadata["structure_type"] = "unknown"
                if "has_numbered_sections" not in metadata:
                    metadata["has_numbered_sections"] = False
                if "total_headings" not in metadata:
                    metadata["total_headings"] = len(result.get("headings", []))

            # Add processing metadata
            result["_meta"] = {
                "page_key": page_key,
                "model": model_name,
                "timestamp": datetime.now().isoformat(),
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
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


def extract_document_hierarchy(
    document_name: str,
    text_only: Dict[str, str],
    screenshots_dir: Path,
    client: OpenAI,
    model_name: str = "gpt-4o"
) -> dict:
    """
    Extract hierarchy for all pages in the document with screenshot support.

    Args:
        document_name: Name of the document
        text_only: Dictionary mapping page keys to text content
        screenshots_dir: Directory containing pre-generated screenshots from stage_1
        client: OpenAI-compatible client instance
        model_name: Model identifier to use for extraction

    Returns:
        Complete hierarchy structure for the document
    """
    hierarchy_data = {
        "document_name": document_name,
        "total_pages": len(text_only),
        "hierarchy": {},
        "generated_at": datetime.now().isoformat()
    }

    print(f"\nExtracting hierarchy for {len(text_only)} pages...")
    print(f"Screenshots directory: {screenshots_dir}")

    previous_corrected_md = None  # Track previous page's corrected markdown

    for page_key in sorted(text_only.keys(), key=lambda x: int(x.split("_")[1])):
        text_content = text_only[page_key]
        page_num = int(page_key.split("_")[1])  # 1-indexed page number

        if not text_content.strip():
            print(f"  [{page_key}] Empty content, skipping")
            hierarchy_data["hierarchy"][page_key] = {
                "headings": [],
                "sections": [],
                "structure_type": "empty",
                "has_numbered_sections": False,
                "total_headings": 0
            }
            continue

        print(f"\n  [{page_key}] Processing ({len(text_content)} chars)...")

        try:
            # Find screenshot for this page
            screenshot_path = find_screenshot_for_page(screenshots_dir, page_num)
            print(f"    [OK] Using screenshot: {screenshot_path.name}")

            # Extract hierarchy with screenshot and previous page context
            page_hierarchy = extract_hierarchy_with_llm(
                text_content,
                page_key,
                screenshot_path,
                previous_corrected_md,  # Pass previous page's corrected markdown
                client,
                model_name
            )

            # Store this page's corrected markdown for next iteration
            previous_corrected_md = page_hierarchy.get("corrected_markdown")

            num_headings = len(page_hierarchy.get("headings", []))
            num_sections = len(page_hierarchy.get("sections", []))
            tokens_used = page_hierarchy["_meta"]["total_tokens"]

            print(f"    [OK] Extracted {num_headings} headings, {num_sections} sections")
            print(f"    - Tokens used: {tokens_used:,}")

            hierarchy_data["hierarchy"][page_key] = page_hierarchy

        except Exception as e:
            print(f"    [ERROR] Hierarchy extraction failed: {e}")
            import traceback
            traceback.print_exc()

            # Add empty hierarchy for failed pages
            hierarchy_data["hierarchy"][page_key] = {
                "headings": [],
                "sections": [],
                "structure_type": "error",
                "has_numbered_sections": False,
                "total_headings": 0,
                "error": str(e)
            }

    return hierarchy_data


def save_hierarchy_data(hierarchy_data: dict, output_path: Path):
    """
    Save hierarchy data to JSON file and optionally save corrected markdown.

    Args:
        hierarchy_data: Extracted hierarchy data
        output_path: Path to save JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save full hierarchy data
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(hierarchy_data, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Save corrected markdown separately for easy access
    corrected_md_path = output_path.parent / f"{hierarchy_data['document_name']}_corrected.md"

    corrected_pages = []
    for page_key in sorted(hierarchy_data["hierarchy"].keys(), key=lambda x: int(x.split("_")[1]) if "_" in x else 0):
        page_data = hierarchy_data["hierarchy"][page_key]
        if "corrected_markdown" in page_data:
            page_num = page_key.split("_")[1]
            corrected_pages.append(f"<!-- PAGE {page_num} -->\n\n{page_data['corrected_markdown']}\n\n")

    if corrected_pages:
        with open(corrected_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(corrected_pages))

        print(f"[SAVED] {corrected_md_path}")
        print(f"File size: {corrected_md_path.stat().st_size / 1024:.1f} KB")


def save_text_payload(text_only: Dict[str, str], document_name: str, output_path: Path):
    """
    Save text-only payload that was sent to LLM for hierarchy extraction.

    Args:
        text_only: Dictionary mapping page keys to text content
        document_name: Name of the document
        output_path: Path to save JSON file
    """
    # Build payload structure with metadata
    payload_data = {
        "document_name": document_name,
        "total_pages": len(text_only),
        "pages": {},
        "statistics": {
            "total_characters": 0,
            "total_words": 0,
            "total_lines": 0
        },
        "generated_at": datetime.now().isoformat()
    }

    # Add each page with metadata
    for page_key in sorted(text_only.keys(), key=lambda x: int(x.split("_")[1])):
        text_content = text_only[page_key]

        page_stats = {
            "text_content": text_content,
            "char_count": len(text_content),
            "word_count": len(text_content.split()),
            "line_count": text_content.count("\n") + 1
        }

        payload_data["pages"][page_key] = page_stats

        # Update totals
        payload_data["statistics"]["total_characters"] += page_stats["char_count"]
        payload_data["statistics"]["total_words"] += page_stats["word_count"]
        payload_data["statistics"]["total_lines"] += page_stats["line_count"]

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload_data, f, indent=2, ensure_ascii=False)

    print(f"[SAVED] {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")


def main():
    parser = argparse.ArgumentParser(
        description="Extract document hierarchy using VLM with visual context"
    )
    parser.add_argument(
        "document",
        help="Document name (e.g., 'DeepWalk', 'Nelson Advanced Functions 12 Textbook')"
    )
    parser.add_argument(
        "--screenshots",
        required=True,
        help="Path to screenshots directory (from stage_1_screenshot_generator.py)"
    )
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "together", "fireworks"],
        help="VLM provider (default: openai)"
    )
    parser.add_argument(
        "--model",
        help="Specific model override (uses provider default if not specified)"
    )
    parser.add_argument(
        "--input",
        help="Input merged JSON file (default: AssemblyPipeline/{doc}/ass_stage_1_merge_data/merged_data.json)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output hierarchy JSON file (default: AssemblyPipeline/{doc}/ass_stage_2_hierarchy/hierarchy_data.json)"
    )
    parser.add_argument(
        "--base-dir",
        help="Base directory (default: auto-detect)"
    )

    args = parser.parse_args()

    # Assembly pipeline directory
    assembly_pipeline_dir = Path(__file__).parent

    # Parse screenshots directory
    screenshots_dir = Path(args.screenshots)
    if not screenshots_dir.exists():
        print(f"\n[ERROR] Screenshots directory not found: {screenshots_dir}")
        sys.exit(1)

    # Determine input path
    if args.input:
        input_path = Path(args.input)
    else:
        input_path = assembly_pipeline_dir / args.document / "ass_stage_1_merge_data" / "merged_data.json"

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = assembly_pipeline_dir / args.document / "ass_stage_2_hierarchy" / "hierarchy_data.json"

    print(f"\n{'='*80}")
    print(f"ASSEMBLY STAGE 2: HIERARCHY EXTRACTION")
    print(f"{'='*80}\n")
    print(f"Document: {args.document}")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Screenshots: {screenshots_dir}\n")

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

    # Extract text-only content
    print(f"\nExtracting text content (stripping visual analysis)...")
    text_only = extract_text_only(doc_data)
    total_chars = sum(len(text) for text in text_only.values())
    print(f"[OK] Extracted {total_chars:,} characters across {len(text_only)} pages")

    # Initialize VLM client
    print(f"\nInitializing {args.provider} client...")
    client = get_vlm_client(args.provider)
    model_name = get_model_name(args.provider, args.model)
    print(f"[OK] Client initialized")
    print(f"[OK] Using model: {model_name}")

    # Extract hierarchy
    try:
        hierarchy_data = extract_document_hierarchy(
            args.document,
            text_only,
            screenshots_dir,
            client,
            model_name
        )

        # Calculate summary statistics
        total_headings = sum(
            len(page.get("headings", []))
            for page in hierarchy_data["hierarchy"].values()
        )
        total_sections = sum(
            len(page.get("sections", []))
            for page in hierarchy_data["hierarchy"].values()
        )

        print(f"\n[SUCCESS] Hierarchy extraction complete!")
        print(f"  - Total headings: {total_headings}")
        print(f"  - Total sections: {total_sections}")

    except Exception as e:
        print(f"\n[ERROR] Hierarchy extraction failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Save hierarchy data
    save_hierarchy_data(hierarchy_data, output_path)

    # Save text payload
    payload_output = output_path.parent / f"{args.document}_hierarchy_payload.json"
    save_text_payload(text_only, args.document, payload_output)

    print(f"\n{'='*80}")
    print(f"Assembly Stage 2 - Hierarchy Extraction Complete!")
    print(f"{'='*80}\n")
    print(f"Results:")
    print(f"  - Hierarchy data: {output_path}")

    # Check if corrected markdown was saved
    corrected_md_path = output_path.parent / f"{args.document}_corrected.md"
    if corrected_md_path.exists():
        print(f"  - Corrected markdown: {corrected_md_path}")

    print(f"  - Text payload: {payload_output}")
    print(f"\nNext: Run Stage 3 (LLM Chunking) with hierarchy context\n")


if __name__ == "__main__":
    main()
