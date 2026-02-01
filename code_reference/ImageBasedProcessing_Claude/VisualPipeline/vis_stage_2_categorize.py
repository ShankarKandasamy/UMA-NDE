"""
Visual Stage 2: Categorize Figures and Tables using GPT-4o-mini

Takes cropped images from Stage 1 and classifies them into categories:
- table: Structured data in rows and columns
- graph/chart: Visual data representations
- photograph: Real-world photographic images
- diagram: Conceptual illustrations and technical drawings
- other: Content that doesn't fit above categories

Model: GPT-4o-mini with vision capabilities

Usage as standalone:
    python vis_stage_2_categorize.py --stage1 DeepWalk/stage_1_crop
    python vis_stage_2_categorize.py --stage1 DeepWalk/stage_1_crop --model gpt-4o

Usage as pipeline stage (called by test_vis_pipeline.py):
    from vis_stage_2_categorize import categorize_images
    results = categorize_images(stage_1_dir)
"""

import argparse
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import base64
from typing import Dict, List, Optional
import time

# OpenAI API
try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI library not found. Install with: pip install openai")
    sys.exit(1)

# Image categories
CATEGORIES = ["table", "graph/chart", "photograph", "diagram", "other"]

# Categorization prompt
CATEGORIZATION_PROMPT = """Analyze this image and classify it into exactly ONE category from: {categories}.

Consider both visual content and any extracted text to make your classification.

═══════════════════════════════════════════════════════════════════════════════
CATEGORY DEFINITIONS
═══════════════════════════════════════════════════════════════════════════════

1. "table" - Structured data arranged in rows and columns
   • Examples: Spreadsheets, data tables, comparison matrices, tabular listings
   • Key indicators: Grid structure, aligned columns, row/column headers, systematic data layout
   • Response format: "table"

2. "graph/chart" - Visual representations of quantitative data and trends
   • Examples: Bar charts, line graphs, pie charts, scatter plots, histograms, data maps
   • Key indicators: Axes, data points, trend lines, legends, quantitative scales

   Sub-categories (REQUIRED for graph/chart):
   • Continuous: Line charts, area charts, scatter plots
   • Categorical: Bar charts (vertical/horizontal), grouped/stacked bars, pie/donut charts
   • Distribution: Histograms, box plots, violin plots
   • Relationship: Flow charts, Sankey diagrams, network graphs
   • Matrix: Heatmaps, confusion matrices
   • Other: Radar charts, gauge charts, funnel charts, waterfall charts

   Response format: "graph/chart: Continuous" (or other sub-category)

3. "photograph" - Real-world photographic images
   • Examples: Portraits, landscapes, product photos, documentary images
   • Key indicators: Photorealistic content, natural lighting, real-world subjects

   Sub-categories (REQUIRED for photograph):
   • Evidence: Proof or raw data (scientific, legal, measurement-oriented)
   • Demonstration: Shows how to perform actions (procedural instructions)
   • Identification: Shows who or what (people, equipment, products, locations)
   • Documentation: Records state or condition at a particular moment (neutral state)
   • Illustration: Abstract or supportive imagery clarifying a concept from text
   • Decoration: Stock or aesthetic imagery with low informational value
   • Environmental Context: Shows surroundings rather than the object of study
   • Equipment / Asset Visualization: Focus on machines, devices, components, tools
   • Condition / Anomaly Evidence: Focus on defects, damage, abnormalities
   • Comparative / Before-After: Shows differences across time or conditions
   • Spatial / Locational Reference: Geographic or spatial positioning

   Response format: "photograph: Evidence" (or other sub-category)

4. "diagram" - Conceptual illustrations, technical drawings, or explanatory graphics
   • Examples: Flowcharts, schematics, organizational charts, process diagrams, maps
   • Key indicators: Shapes connected by lines, hierarchical structures, technical symbols

   Sub-categories (REQUIRED for diagram):
   • Conceptual: Mind maps, Venn diagrams, concept maps, ER diagrams, theoretical frameworks
   • Technical: Circuit diagrams, blueprints, engineering schematics, wiring diagrams, CAD designs
   • Explanatory: Flowcharts, process diagrams, org charts, decision trees, workflow diagrams
   • Other: Reference maps, timeline diagrams, genealogy trees, seating charts, floor plans

   Response format: "diagram: Technical" (or other sub-category)

5. "other" - Content that doesn't fit above categories or has minimal informational value
   • Examples: Logos, decorative elements, page headers/footers, blank areas, isolated labels,
     fragments separated from main content, ornamental graphics, background images
   • Response format: "other"

      Sub-categories (REQUIRED for other):
   • Logo: Company logos, brand marks, organizational emblems, certification badges
   • Icon: Symbols, feature indicators, UI elements, warning signs, small graphical markers
   • Decorative: Ornamental graphics, artistic flourishes, background patterns, textures
   • Page Furniture: Headers, footers, page numbers, section dividers, navigation elements
   • Watermark: Watermarks, stamps, draft indicators, confidentiality marks
   • Fragment: Cropped or incomplete elements, artifacts, partial images
   • Screenshot: Screen captures of interfaces, applications, or digital content
   • Infographic: Mixed visual/text information displays that don't fit other categories
   • Text Block: Isolated text rendered as image (not fitting table structure)
   • Mixed Content: Complex images combining multiple types that resist single classification
   • Unclassifiable: Cannot determine what the image represents

   Confidence score (REQUIRED for other):
   The confidence score (0.00 to 1.00) indicates how likely this image contains 
   USEFUL INFORMATION worth extracting. This is NOT confidence in your classification —
   it's confidence that the image has ANALYTICAL VALUE.

   Score guidelines:
   • 0.80 - 1.00: HIGH value — Contains extractable data, text, or structured information
                  Examples: Screenshots with data, infographics, text blocks, mixed content 
                  with identifiable information, possibly miscategorized diagrams/charts
   • 0.50 - 0.79: MEDIUM value — May contain useful information, uncertain
                  Examples: Complex logos with text, icons with labels, unclear content
   • 0.20 - 0.49: LOW value — Likely decorative but has some identifiable elements  
                  Examples: Simple logos, basic icons, styled headers
   • 0.00 - 0.19: MINIMAL value — Almost certainly decorative/structural, no extraction needed
                  Examples: Background patterns, ornamental dividers, watermarks, fragments

   Response format example: "other: Screenshot: 0.85" or "other: Decorative: 0.10"

═══════════════════════════════════════════════════════════════════════════════
CLASSIFICATION GUIDELINES
═══════════════════════════════════════════════════════════════════════════════

1. Primary purpose: What is the main function of this image?
2. Information density: Does it convey substantial information or is it supplementary?
3. Completeness: Is this a complete element or a fragment of something larger?
4. Default to "other": When uncertain, use "other" rather than guessing between categories
5. Text-only elements: Small headers, labels, or identifiers → "other"
6. Map distinction: Data visualization maps → "graph/chart"; reference maps → "diagram"

═══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMAT
═══════════════════════════════════════════════════════════════════════════════

Return ONLY the category (and sub-category if applicable):
• For table, other: Return category name only (e.g., "table")
• For graph/chart: Return "graph/chart: [Sub-category]" (e.g., "graph/chart: Continuous")
• For photograph: Return "photograph: [Sub-category]" (e.g., "photograph: Evidence")
• For diagram: Return "diagram: [Sub-category]" (e.g., "diagram: Technical")

Use exact capitalization as shown above."""


def encode_image(image_path: Path) -> str:
    """Encode image to base64 string for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def categorize_image(client: OpenAI, image_path: Path, model: str = "gpt-4o-mini") -> Dict:
    """
    Categorize a single image using GPT-4o-mini vision.

    Args:
        client: OpenAI client instance
        image_path: Path to image file
        model: Model to use (default: gpt-4o-mini)

    Returns:
        Dict with category and metadata
    """
    try:
        # Encode image
        base64_image = encode_image(image_path)

        # Create prompt with categories
        prompt = CATEGORIZATION_PROMPT.format(categories=', '.join(CATEGORIES))

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50,
            temperature=0.0
        )

        # Extract category from response
        category_response = response.choices[0].message.content.strip().lower()

        # Extract main category (before colon if sub-category exists)
        main_category = category_response.split(':')[0].strip()

        # Validate main category
        if main_category not in CATEGORIES:
            print(f"    [WARNING] Unexpected category '{category_response}' for {image_path.name}, defaulting to 'other'")
            category_response = "other"
            main_category = "other"

        return {
            "category": category_response,  # Full response with sub-category
            "main_category": main_category,  # Base category for filtering
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

    except Exception as e:
        print(f"    [ERROR] Failed to categorize {image_path.name}: {e}")
        return {
            "category": "other",
            "main_category": "other",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def categorize_images(stage_1_dir: str, model: str = "gpt-4o-mini",
                     api_key: Optional[str] = None) -> Dict:
    """
    Categorize all images from Stage 1 output.

    This is the main function called by the visual pipeline orchestrator.

    Args:
        stage_1_dir: Directory containing Stage 1 output (stage_1_crop)
        model: OpenAI model to use (default: gpt-4o-mini)
        api_key: OpenAI API key (if None, reads from environment)

    Returns:
        Dict with results:
        {
            'total_images': int,
            'total_categorized': int,
            'category_counts': dict,
            'output_dir': str,
            'metadata_file': str
        }
    """
    stage_1_path = Path(stage_1_dir)

    print(f"Stage 2: Categorize Figures and Tables")
    print(f"Input: {stage_1_dir}")
    print(f"Model: {model}")
    print(f"Categories: {', '.join(CATEGORIES)}")

    # Load Stage 1 metadata
    metadata_file = stage_1_path / "stage_1_crop_metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Stage 1 metadata not found: {metadata_file}")

    with open(metadata_file, 'r') as f:
        stage_1_metadata = json.load(f)

    print(f"Loaded Stage 1 metadata: {len(stage_1_metadata['pages'])} pages")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Create output directory
    output_dir = stage_1_path.parent / "stage_2_category"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each page
    total_images = 0
    total_categorized = 0
    category_counts = {cat: 0 for cat in CATEGORIES}
    total_tokens = 0

    enhanced_metadata = stage_1_metadata.copy()

    for page_idx, page_data in enumerate(enhanced_metadata['pages']):
        page_num = page_data['page_number']

        if not page_data['detections']:
            continue

        print(f"  Processing page {page_num}: {len(page_data['detections'])} detections...")

        for detection in page_data['detections']:
            total_images += 1

            # Get image path (relative to stage_1_dir)
            image_rel_path = detection['file_path']
            image_path = stage_1_path / image_rel_path

            if not image_path.exists():
                print(f"    [WARNING] Image not found: {image_path}")
                detection['category'] = "other"
                detection['main_category'] = "other"
                detection['category_error'] = "Image file not found"
                continue

            # Categorize image
            print(f"    Categorizing {image_path.name}...", end=" ")
            result = categorize_image(client, image_path, model)

            # Update detection with category info
            detection['category'] = result['category']  # Full category with sub-category
            detection['main_category'] = result.get('main_category')  # Base category
            detection['category_model'] = result.get('model')
            detection['category_timestamp'] = result.get('timestamp')

            if 'error' in result:
                detection['category_error'] = result['error']
            else:
                total_categorized += 1
                # Count by main category for summary statistics
                main_cat = result.get('main_category', result['category'].split(':')[0].strip())
                category_counts[main_cat] += 1
                if 'total_tokens' in result:
                    total_tokens += result['total_tokens']

            print(f"{result['category']}")

            # Small delay to avoid rate limits
            time.sleep(0.1)

        print(f"    Page {page_num}: {len(page_data['detections'])} images categorized")

    # Save enhanced metadata
    metadata_output = output_dir / "stage_2_category_metadata.json"
    enhanced_metadata['stage_2_info'] = {
        'model': model,
        'categories': CATEGORIES,
        'timestamp': datetime.now().isoformat(),
        'total_images': total_images,
        'total_categorized': total_categorized,
        'category_counts': category_counts,
        'total_tokens': total_tokens
    }

    with open(metadata_output, 'w') as f:
        json.dump(enhanced_metadata, f, indent=2)

    print(f"\n[OK] Stage 2 complete")
    print(f"     Total images: {total_images}")
    print(f"     Successfully categorized: {total_categorized}")
    print(f"     Category distribution:")
    for cat, count in category_counts.items():
        if count > 0:
            print(f"       - {cat}: {count}")
    print(f"     Total tokens used: {total_tokens:,}")

    # Return results for orchestrator
    return {
        'total_images': total_images,
        'total_categorized': total_categorized,
        'category_counts': category_counts,
        'total_tokens': total_tokens,
        'output_dir': str(output_dir),
        'metadata_file': str(metadata_output)
    }


def main():
    """Standalone script execution."""
    parser = argparse.ArgumentParser(
        description='Categorize cropped images using GPT-4o-mini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vis_stage_2_categorize.py --stage1 DeepWalk/stage_1_crop
  python vis_stage_2_categorize.py --stage1 DeepWalk/stage_1_crop --model gpt-4o
  python vis_stage_2_categorize.py --stage1 VisualPipeline/DeepWalk/stage_1_crop
        """
    )

    parser.add_argument('--stage1', type=str, required=True,
                       help='Path to Stage 1 output directory (contains stage_1_crop_metadata.json)')
    parser.add_argument('--model', type=str, default='gpt-4o-mini',
                       help='OpenAI model to use (default: gpt-4o-mini)')
    parser.add_argument('--api-key', type=str, default=None,
                       help='OpenAI API key (default: reads from OPENAI_API_KEY env var)')

    args = parser.parse_args()

    # Validate Stage 1 directory
    stage_1_path = Path(args.stage1)
    if not stage_1_path.exists():
        print(f"[ERROR] Stage 1 directory not found: {stage_1_path}")
        sys.exit(1)

    metadata_file = stage_1_path / "stage_1_crop_metadata.json"
    if not metadata_file.exists():
        print(f"[ERROR] Stage 1 metadata not found: {metadata_file}")
        print(f"        Make sure you've run vis_stage_1_crop.py first")
        sys.exit(1)

    # Run categorization
    try:
        results = categorize_images(
            stage_1_dir=str(stage_1_path),
            model=args.model,
            api_key=args.api_key
        )

        # Print summary
        print(f"\n{'='*80}")
        print("STAGE 2 COMPLETE")
        print(f"{'='*80}")
        print(f"Total Images: {results['total_images']}")
        print(f"Successfully Categorized: {results['total_categorized']}")
        print(f"\nCategory Distribution:")
        for cat, count in results['category_counts'].items():
            if count > 0:
                print(f"  {cat}: {count}")
        print(f"\nTotal Tokens: {results['total_tokens']:,}")
        print(f"\nOutput: {results['output_dir']}")
        print(f"Metadata: {results['metadata_file']}")
        print(f"{'='*80}\n")

    except Exception as e:
        print(f"\n[ERROR] Stage 2 failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
