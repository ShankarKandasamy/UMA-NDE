"""
Visual Stage 4: Visual Analysis using Category-Specific Prompts

Takes categorized images from Stage 2 and performs detailed visual analysis
using category-specific prompts and models. Optionally includes surrounding
text context from horizontal buckets to improve extraction accuracy.

Model routing based on category:
- Tables: GPT-4o (high detail)
- Graphs/Charts: GPT-4o-mini (structured extraction)
- Diagrams: GPT-4o-mini (structure and relationships)
- Photographs: GPT-4o-mini (context-dependent)
- Other: Varies by subcategory (Screenshot, Infographic, etc.)

Context Text Feature:
- Extracts 100 tokens of text before and after each image
- Saves up to 400 chars of context text for matching accuracy
- Uses proximity-based selection (closest text first)
- Filters out noise buckets (< 20 chars)
- Requires horizontal bucket metadata from stage_8_horizontal_buckets.py

Usage as standalone:
    # Without context
    python stage_4_visual_analysis.py --stage2 DeepWalk/stage_2_category

    # With context
    python stage_4_visual_analysis.py --stage2 DeepWalk/stage_2_category \\
        --buckets horizontal_bucket_results/horizontal_bucket_metadata.json

Usage as pipeline stage:
    from stage_4_visual_analysis import analyze_images
    results = analyze_images(stage_2_dir, horizontal_buckets_file="path/to/buckets.json")
"""

import argparse
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import base64
from typing import Dict, List, Optional, Tuple
import time

# OpenAI API
try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI library not found. Install with: pip install openai")
    sys.exit(1)

# Tokenizer for context budget
try:
    import tiktoken
    TOKENIZER = tiktoken.encoding_for_model("gpt-4o-mini")
except ImportError:
    print("[WARNING] tiktoken not found. Install with: pip install tiktoken")
    print("[WARNING] Context text will use character-based estimation (less accurate)")
    TOKENIZER = None
except Exception:
    # Fallback for older tiktoken versions
    try:
        TOKENIZER = tiktoken.get_encoding("cl100k_base")
    except:
        TOKENIZER = None

# Import our configuration
try:
    from vis_stage_3_config import (
        get_analysis_config,
        should_skip_image,
        PROMPT_VERSION
    )
except ImportError:
    print("[ERROR] vis_stage_3_config.py not found in the same directory")
    sys.exit(1)

# Context budget settings (tokens)
CONTEXT_TOKEN_BUDGET = {
    'before': 100,  # 100 tokens before image
    'after': 100    # 100 tokens after image
}

# Minimum bucket character count to avoid OCR noise
MIN_BUCKET_CHARS = 20

# General prompt - applies to ALL images
GENERAL_PROMPT = """================================================================================
DOCUMENT CONTEXT
================================================================================

You are analyzing an image extracted from a larger document. The image appears in
context with surrounding text that provides important information about its purpose,
content, and relevance.

{context_section}

USE THIS CONTEXT TO:
  • Identify the image's purpose and relevance within the document
  • Extract accurate titles, captions, or labels mentioned in the surrounding text
  • Identify key concepts, terminology, and domain-specific keywords
  • Understand relationships between the image and surrounding content
  • Improve summary, description, and other text-based content accuracy by aligning with the document's narrative
  • Detect explicit references to this image (e.g., 'Figure 1', 'Table 2', 'as shown above')
  • Incorporate contextual information into your analysis where relevant

================================================================================
"""

# Output format requirements - applies to ALL images
OUTPUT_PROMPT = """
================================================================================
OUTPUT REQUIREMENTS
================================================================================

• Return ONLY valid JSON matching the schema specified in the task instructions above
• Do NOT wrap the JSON in markdown code blocks (no ```json```)
• Do NOT include any explanatory text before or after the JSON
• Ensure all required fields are present and properly formatted
• Use null for optional fields that don't apply
• Validate that your JSON is properly escaped and parseable

Return your response now:
"""


def count_tokens(text: str) -> int:
    """
    Count tokens using OpenAI's tokenizer.

    Args:
        text: Text to count tokens for

    Returns:
        Number of tokens
    """
    if TOKENIZER is None:
        # Fallback: estimate ~4 chars per token
        return len(text) // 4

    try:
        return len(TOKENIZER.encode(text))
    except Exception:
        # Emergency fallback
        return len(text) // 4


def extract_text_from_bucket(horizontal_bucket: Dict) -> str:
    """
    Extract all text from a horizontal bucket's vertical buckets.
    Preserves reading order from vertical bucket structure.

    Args:
        horizontal_bucket: Horizontal bucket dict with 'vertical_buckets' list

    Returns:
        Concatenated text from all vertical buckets
    """
    texts = []

    for vbucket in horizontal_bucket.get('vertical_buckets', []):
        # Check if vertical bucket has blocks with text
        if 'blocks' in vbucket:
            block_texts = [block.get('text', '') for block in vbucket['blocks']]
            texts.append(' '.join(block_texts))
        elif 'text' in vbucket:
            texts.append(vbucket['text'])

    # Join with space to preserve word boundaries
    return ' '.join(texts).strip()


def get_context_text(
    image_bbox: Dict,
    page_num: int,
    horizontal_buckets_data: Dict
) -> Dict:
    """
    Select context text based on proximity to image and token budget.

    Strategy:
    1. Filter out noise buckets (< MIN_BUCKET_CHARS threshold)
    2. Separate buckets into before/after based on vertical position
    3. Sort by proximity (closest first)
    4. Accumulate text until token budget exhausted

    Args:
        image_bbox: Dict with left_edge, top_edge, right_edge, bottom_edge (0-100 range)
        page_num: Page number (1-indexed)
        horizontal_buckets_data: Loaded horizontal bucket metadata

    Returns:
        Dict with before_text, after_text, and token counts:
        {
            'before_text': str,
            'after_text': str,
            'before_tokens': int,
            'after_tokens': int,
            'total_tokens': int
        }
    """
    # Find the page in horizontal buckets data
    page_buckets = None
    for page in horizontal_buckets_data.get('pages', []):
        if page['page_number'] == page_num:
            page_buckets = page.get('horizontal_buckets', [])
            break

    if not page_buckets:
        return {
            'before_text': '',
            'after_text': '',
            'before_tokens': 0,
            'after_tokens': 0,
            'total_tokens': 0
        }

    # Get image boundaries
    image_top = image_bbox['top_edge']
    image_bottom = image_bbox['bottom_edge']

    # Separate buckets into before/after
    before_buckets = []
    after_buckets = []

    for bucket in page_buckets:
        # Extract and measure text
        bucket_text = extract_text_from_bucket(bucket)
        char_count = len(bucket_text)

        # Skip noise buckets
        if char_count < MIN_BUCKET_CHARS:
            continue

        # Classify as before or after based on vertical position
        bucket_bottom = bucket.get('bottom_edge', 0)
        bucket_top = bucket.get('top_edge', 0)

        if bucket_bottom < image_top:
            # Bucket is completely above image
            distance = image_top - bucket_bottom
            before_buckets.append({
                'text': bucket_text,
                'distance': distance,
                'char_count': char_count
            })
        elif bucket_top > image_bottom:
            # Bucket is completely below image
            distance = bucket_top - image_bottom
            after_buckets.append({
                'text': bucket_text,
                'distance': distance,
                'char_count': char_count
            })
        # Skip buckets that overlap with image

    # Sort by distance (closest first)
    before_buckets.sort(key=lambda x: x['distance'])
    after_buckets.sort(key=lambda x: x['distance'])

    # Accumulate text up to token budget
    def accumulate_text_by_tokens(buckets, token_limit):
        accumulated = []
        total_tokens = 0

        for item in buckets:
            bucket_text = item['text']
            bucket_tokens = count_tokens(bucket_text)

            if total_tokens + bucket_tokens > token_limit:
                # Stop at bucket boundary (preserve completeness)
                break

            accumulated.append(bucket_text)
            total_tokens += bucket_tokens

        return '\n\n'.join(accumulated), total_tokens

    # Get context text within budget
    before_text, before_tokens = accumulate_text_by_tokens(
        before_buckets,
        CONTEXT_TOKEN_BUDGET['before']
    )
    after_text, after_tokens = accumulate_text_by_tokens(
        after_buckets,
        CONTEXT_TOKEN_BUDGET['after']
    )

    return {
        'before_text': before_text,
        'after_text': after_text,
        'before_tokens': before_tokens,
        'after_tokens': after_tokens,
        'total_tokens': before_tokens + after_tokens
    }


def encode_image(image_path: Path) -> str:
    """Encode image to base64 string for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def parse_category(category_str: str) -> Tuple[str, Optional[str], Optional[float]]:
    """
    Parse Stage 2 category into (main_category, subcategory, confidence).

    Examples:
        "table" → ("table", None, None)
        "graph/chart: Continuous" → ("graph/chart", "Continuous", None)
        "photograph: Evidence" → ("photograph", "Evidence", None)
        "other: Screenshot: 0.85" → ("other", "Screenshot", 0.85)

    Returns:
        (main_category, subcategory, confidence_value)
    """
    if ':' not in category_str:
        return category_str, None, None

    parts = category_str.split(':', 1)
    main_category = parts[0].strip()
    remainder = parts[1].strip()

    # Handle "other" subcategory with confidence score
    if main_category == "other" and ':' in remainder:
        subcat_parts = remainder.split(':', 1)
        subcategory = subcat_parts[0].strip()
        try:
            confidence = float(subcat_parts[1].strip())
            return main_category, subcategory, confidence
        except ValueError:
            return main_category, subcategory, None

    return main_category, remainder, None


def analyze_image(
    client: OpenAI,
    image_path: Path,
    category_prompt: str,
    model: str,
    max_tokens: int,
    temperature: float,
    detail: str,
    context_text: Optional[Dict] = None
) -> Dict:
    """
    Analyze a single image using OpenAI vision API.

    Constructs final prompt as: GENERAL_PROMPT + category_prompt + OUTPUT_PROMPT

    Args:
        client: OpenAI client instance
        image_path: Path to image file
        category_prompt: Category-specific extraction prompt (from vis_stage_3_config)
        model: Model to use (gpt-4o, gpt-4o-mini)
        max_tokens: Maximum tokens for response
        temperature: Sampling temperature
        detail: Image detail level ("high" or "low")
        context_text: Optional dict with before_text and after_text from surrounding document

    Returns:
        Dict with analysis results or error information
    """
    try:
        # Build context section
        context_section = ""
        if context_text and (context_text.get('before_text') or context_text.get('after_text')):
            if context_text.get('before_text'):
                context_section += "--- TEXT BEFORE IMAGE ---\n"
                context_section += f"{context_text['before_text']}\n\n"

            if context_text.get('after_text'):
                context_section += "--- TEXT AFTER IMAGE ---\n"
                context_section += f"{context_text['after_text']}\n\n"
        else:
            # No context available
            context_section = "No surrounding text context available for this image.\n\n"

        # Construct final prompt: general + category-specific + output
        general_section = GENERAL_PROMPT.format(context_section=context_section)
        final_prompt = general_section + "\n" + category_prompt + "\n" + OUTPUT_PROMPT

        # Encode image
        base64_image = encode_image(image_path)

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": final_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": detail
                            }
                        }
                    ]
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Extract response
        raw_output = response.choices[0].message.content.strip()

        # Try to parse as JSON
        result = None

        # First, try parsing directly
        if raw_output.startswith('{') or raw_output.startswith('['):
            try:
                result = json.loads(raw_output)
            except json.JSONDecodeError:
                pass

        # If direct parsing failed or output has markdown code blocks, try cleaning
        if result is None and "```" in raw_output:
            parts = raw_output.split("```")
            if len(parts) >= 2:
                # Get content between first pair of ```
                cleaned = parts[1]
                # Remove 'json' language identifier if present
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                try:
                    result = json.loads(cleaned.strip())
                except json.JSONDecodeError:
                    pass

        if result is None:
            # Return raw output if not JSON
            result = {"raw_text": raw_output}

        # Add metadata
        result["_stage3_meta"] = {
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return result

    except Exception as e:
        print(f"    [ERROR] Failed to analyze {image_path.name}: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def analyze_images(
    stage_2_dir: str,
    api_key: Optional[str] = None,
    version_override: Optional[str] = None,
    horizontal_buckets_file: Optional[str] = None
) -> Dict:
    """
    Analyze all categorized images from Stage 2 output.

    This is the main function called by the visual pipeline orchestrator.

    Args:
        stage_2_dir: Directory containing Stage 2 output (stage_2_category)
        api_key: OpenAI API key (if None, reads from environment)
        version_override: Override PROMPT_VERSION ("gpt", "claude", "gemini")
        horizontal_buckets_file: Path to horizontal bucket metadata JSON (if None, context disabled)

    Returns:
        Dict with results:
        {
            'total_images': int,
            'total_analyzed': int,
            'total_skipped': int,
            'category_counts': dict,
            'output_dir': str,
            'metadata_file': str
        }
    """
    stage_2_path = Path(stage_2_dir)

    print(f"Stage 4: Visual Analysis")
    print(f"Input: {stage_2_dir}")

    # Override version if specified
    if version_override:
        import vis_stage_3_config
        vis_stage_3_config.PROMPT_VERSION = version_override
        print(f"Prompt version: {version_override} (overridden)")
    else:
        print(f"Prompt version: {PROMPT_VERSION}")

    # Load horizontal buckets for context (optional)
    horizontal_buckets_data = None
    if horizontal_buckets_file:
        h_buckets_path = Path(horizontal_buckets_file)
        if h_buckets_path.exists():
            print(f"Loading horizontal buckets for context: {horizontal_buckets_file}")
            try:
                with open(h_buckets_path, 'r', encoding='utf-8') as f:
                    horizontal_buckets_data = json.load(f)
                print(f"[OK] Context enabled: {CONTEXT_TOKEN_BUDGET['before']} tokens before, {CONTEXT_TOKEN_BUDGET['after']} tokens after")
            except Exception as e:
                print(f"[WARNING] Failed to load horizontal buckets: {e}")
                print(f"[WARNING] Context will be disabled")
        else:
            print(f"[WARNING] Horizontal buckets file not found: {h_buckets_path}")
            print(f"[WARNING] Context will be disabled")
    else:
        print(f"[INFO] No horizontal buckets file provided - context disabled")

    # Load Stage 2 metadata
    metadata_file = stage_2_path / "stage_2_category_metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Stage 2 metadata not found: {metadata_file}")

    with open(metadata_file, 'r') as f:
        stage_2_metadata = json.load(f)

    print(f"Loaded Stage 2 metadata: {len(stage_2_metadata['pages'])} pages")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Create output directory
    output_dir = stage_2_path.parent / "stage_3_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each page
    total_images = 0
    total_analyzed = 0
    total_skipped = 0
    skip_reasons = {}
    category_counts = {}
    total_tokens = 0

    enhanced_metadata = stage_2_metadata.copy()

    for page_idx, page_data in enumerate(enhanced_metadata['pages']):
        page_num = page_data['page_number']

        if not page_data['detections']:
            continue

        print(f"\n  Processing page {page_num}: {len(page_data['detections'])} detections...")

        for detection in page_data['detections']:
            total_images += 1

            # Get category information
            category = detection.get('category', 'other')
            main_category = detection.get('main_category', 'other')

            # Parse category
            main_cat, subcategory, other_confidence = parse_category(category)

            # Update main_category if parsing gave us better info
            if main_cat:
                main_category = main_cat

            # Get image path
            image_rel_path = detection['file_path']
            image_path = stage_2_path.parent / "stage_1_crop" / image_rel_path

            if not image_path.exists():
                print(f"    [WARNING] Image not found: {image_path}")
                detection['stage3_error'] = "Image file not found"
                total_skipped += 1
                continue

            # Check skip rules
            stage2_confidence = detection.get('category_confidence', 1.0)
            should_skip, skip_reason = should_skip_image(main_category, subcategory or "", stage2_confidence)

            if should_skip:
                print(f"    [SKIP] {image_path.name}: {skip_reason}")
                detection['stage3_skipped'] = True
                detection['stage3_skip_reason'] = skip_reason
                total_skipped += 1
                skip_reasons[skip_reason] = skip_reasons.get(skip_reason, 0) + 1
                continue

            # Get analysis config
            config = get_analysis_config(main_category, subcategory or "", stage2_confidence)

            if config is None:
                print(f"    [SKIP] {image_path.name}: No config found for {main_category}/{subcategory}")
                detection['stage3_skipped'] = True
                detection['stage3_skip_reason'] = "No configuration available"
                total_skipped += 1
                skip_reasons["No configuration"] = skip_reasons.get("No configuration", 0) + 1
                continue

            # Get context text if horizontal buckets available
            context = None
            if horizontal_buckets_data:
                try:
                    context = get_context_text(
                        image_bbox={
                            'left_edge': detection.get('left_edge', 0),
                            'top_edge': detection.get('top_edge', 0),
                            'right_edge': detection.get('right_edge', 100),
                            'bottom_edge': detection.get('bottom_edge', 100)
                        },
                        page_num=page_num,
                        horizontal_buckets_data=horizontal_buckets_data
                    )
                except Exception as e:
                    print(f"    [WARNING] Failed to get context for {image_path.name}: {e}")
                    context = None

            # Analyze image
            context_info = f" +{context['total_tokens']}ctx" if context and context['total_tokens'] > 0 else ""
            print(f"    Analyzing {image_path.name} [{main_category}/{subcategory}]{context_info}...", end=" ")

            result = analyze_image(
                client,
                image_path,
                config['prompt'],
                config['model'],
                config['max_tokens'],
                config['temperature'],
                config['detail'],
                context_text=context
            )

            # Update detection with analysis
            detection['visual_analysis'] = result
            detection['analysis_model'] = config['model']
            detection['analysis_timestamp'] = datetime.now().isoformat()
            detection['prompt_file'] = config.get('prompt_file', 'unknown')

            # Save context metadata if context was used
            if context:
                # Extract full context text (up to 400 chars for better matching accuracy)
                before_text = context.get('before_text', '')
                after_text = context.get('after_text', '')

                detection['context_metadata'] = {
                    'before_tokens': context.get('before_tokens', 0),
                    'after_tokens': context.get('after_tokens', 0),
                    'total_tokens': context.get('total_tokens', 0),
                    'before_text_preview': before_text[:400] + ('...' if len(before_text) > 400 else ''),
                    'after_text_preview': after_text[:400] + ('...' if len(after_text) > 400 else '')
                }

            if 'error' in result:
                print(f"ERROR: {result['error']}")
            else:
                total_analyzed += 1
                category_counts[main_category] = category_counts.get(main_category, 0) + 1
                if '_stage3_meta' in result:
                    total_tokens += result['_stage3_meta'].get('total_tokens', 0)
                print(f"OK ({config['model']})")

            # Small delay to avoid rate limits
            time.sleep(0.1)

        print(f"    Page {page_num} complete")

    # Save enhanced metadata
    metadata_output = output_dir / "stage_3_analysis_metadata.json"
    enhanced_metadata['stage_3_info'] = {
        'prompt_version': version_override or PROMPT_VERSION,
        'timestamp': datetime.now().isoformat(),
        'total_images': total_images,
        'total_analyzed': total_analyzed,
        'total_skipped': total_skipped,
        'skip_reasons': skip_reasons,
        'category_counts': category_counts,
        'total_tokens': total_tokens
    }

    with open(metadata_output, 'w') as f:
        json.dump(enhanced_metadata, f, indent=2)

    print(f"\n[OK] Stage 4 complete")
    print(f"     Total images: {total_images}")
    print(f"     Analyzed: {total_analyzed}")
    print(f"     Skipped: {total_skipped}")
    if skip_reasons:
        print(f"     Skip reasons:")
        for reason, count in skip_reasons.items():
            print(f"       - {reason}: {count}")
    print(f"     Category distribution:")
    for cat, count in category_counts.items():
        if count > 0:
            print(f"       - {cat}: {count}")
    print(f"     Total tokens used: {total_tokens:,}")

    # Return results for orchestrator
    return {
        'total_images': total_images,
        'total_analyzed': total_analyzed,
        'total_skipped': total_skipped,
        'skip_reasons': skip_reasons,
        'category_counts': category_counts,
        'total_tokens': total_tokens,
        'output_dir': str(output_dir),
        'metadata_file': str(metadata_output)
    }


def main():
    """Standalone script execution."""
    parser = argparse.ArgumentParser(
        description='Perform visual analysis on categorized images using category-specific prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (no context)
  python stage_4_visual_analysis.py --stage2 DeepWalk/stage_2_category

  # With context from horizontal buckets
  python stage_4_visual_analysis.py --stage2 DeepWalk/stage_2_category --buckets horizontal_bucket_results/horizontal_bucket_metadata.json

  # With different prompt version
  python stage_4_visual_analysis.py --stage2 DeepWalk/stage_2_category --version claude --buckets horizontal_bucket_results/horizontal_bucket_metadata.json
        """
    )

    parser.add_argument('--stage2', type=str, required=True,
                       help='Path to Stage 2 output directory (contains stage_2_category_metadata.json)')
    parser.add_argument('--version', type=str, default=None, choices=['gpt', 'claude', 'gemini'],
                       help='Override prompt version (gpt, claude, or gemini)')
    parser.add_argument('--buckets', type=str, default=None,
                       help='Path to horizontal bucket metadata JSON for context (optional)')
    parser.add_argument('--api-key', type=str, default=None,
                       help='OpenAI API key (default: reads from OPENAI_API_KEY env var)')

    args = parser.parse_args()

    # Validate Stage 2 directory
    stage_2_path = Path(args.stage2)
    if not stage_2_path.exists():
        print(f"[ERROR] Stage 2 directory not found: {stage_2_path}")
        sys.exit(1)

    metadata_file = stage_2_path / "stage_2_category_metadata.json"
    if not metadata_file.exists():
        print(f"[ERROR] Stage 2 metadata not found: {metadata_file}")
        print(f"        Make sure you've run vis_stage_2_categorize.py first")
        sys.exit(1)

    # Run analysis
    try:
        results = analyze_images(
            stage_2_dir=str(stage_2_path),
            api_key=args.api_key,
            version_override=args.version,
            horizontal_buckets_file=args.buckets
        )

        # Print summary
        print(f"\n{'='*80}")
        print("STAGE 4 COMPLETE")
        print(f"{'='*80}")
        print(f"Total Images: {results['total_images']}")
        print(f"Analyzed: {results['total_analyzed']}")
        print(f"Skipped: {results['total_skipped']}")

        if results['skip_reasons']:
            print(f"\nSkip Reasons:")
            for reason, count in results['skip_reasons'].items():
                print(f"  {reason}: {count}")

        print(f"\nCategory Distribution:")
        for cat, count in results['category_counts'].items():
            if count > 0:
                print(f"  {cat}: {count}")

        print(f"\nTotal Tokens: {results['total_tokens']:,}")
        print(f"\nOutput: {results['output_dir']}")
        print(f"Metadata: {results['metadata_file']}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n[ERROR] Stage 4 failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

