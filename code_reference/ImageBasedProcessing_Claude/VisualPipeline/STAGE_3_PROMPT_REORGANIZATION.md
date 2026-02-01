# Stage 3 Prompt Reorganization Guide

**Date**: December 2024
**Author**: Claude Code
**Purpose**: Document the reorganization of Stage 3 prompts from model-specific to category-specific structure

---

## Summary

Reorganized 62 prompt files from a model-centric structure to a category/subcategory structure with optional version variants. This enables:
- Easy switching between GPT, Claude, and Gemini prompts for testing
- Consistent organization by category
- Clear separation of concerns

---

## File Structure

### Before (Old Structure)
```
vis_stage_3_prompts/
  tables.md
  graphs_charts_gpt.md
  graphs_charts_claude.md
  graphs_charts_gemini.md
  diagrams_gpt.md
  diagrams_claude.md
  diagrams_gemini.md
  photographs_gpt.md
  other_gpt.md
  other_claude.md
  other_gemini.md
```

### After (New Structure)
```
vis_stage_3_prompts/
  # Table (1 file)
  table.md

  # Graphs/Charts (18 files: 6 subcategories × 3 versions)
  graph_chart_continuous_gpt.md
  graph_chart_continuous_claude.md
  graph_chart_continuous_gemini.md
  graph_chart_categorical_gpt.md
  graph_chart_categorical_claude.md
  graph_chart_categorical_gemini.md
  graph_chart_distribution_gpt.md
  graph_chart_distribution_claude.md
  graph_chart_distribution_gemini.md
  graph_chart_relationship_gpt.md
  graph_chart_relationship_claude.md
  graph_chart_relationship_gemini.md
  graph_chart_matrix_gpt.md
  graph_chart_matrix_claude.md
  graph_chart_matrix_gemini.md
  graph_chart_other_gpt.md
  graph_chart_other_claude.md
  graph_chart_other_gemini.md

  # Diagrams (12 files: 4 subcategories × 3 versions)
  diagram_conceptual_gpt.md
  diagram_conceptual_claude.md
  diagram_conceptual_gemini.md
  diagram_technical_gpt.md
  diagram_technical_claude.md
  diagram_technical_gemini.md
  diagram_explanatory_gpt.md
  diagram_explanatory_claude.md
  diagram_explanatory_gemini.md
  diagram_other_gpt.md
  diagram_other_claude.md
  diagram_other_gemini.md

  # Photographs (10 files: 10 subcategories × 1 version)
  photograph_evidence.md
  photograph_demonstration.md
  photograph_identification.md
  photograph_documentation.md
  photograph_illustration.md
  photograph_environmental_context.md
  photograph_equipment_asset.md
  photograph_condition_anomaly.md
  photograph_comparative_before_after.md
  photograph_spatial_locational.md

  # Other (21 files: 7 subcategories × 3 versions)
  other_screenshot_gpt.md
  other_screenshot_claude.md
  other_screenshot_gemini.md
  other_infographic_gpt.md
  other_infographic_claude.md
  other_infographic_gemini.md
  other_mixed_content_gpt.md
  other_mixed_content_claude.md
  other_mixed_content_gemini.md
  other_text_block_gpt.md
  other_text_block_claude.md
  other_text_block_gemini.md
  other_unclassifiable_gpt.md
  other_unclassifiable_claude.md
  other_unclassifiable_gemini.md
  other_watermark_gpt.md
  other_watermark_claude.md
  other_watermark_gemini.md
  other_fragment_gpt.md
  other_fragment_claude.md
  other_fragment_gemini.md
```

**Total**: 62 prompt files (1 table + 18 graphs + 12 diagrams + 10 photographs + 21 other)

---

## Configuration File

### `vis_stage_3_config.py`

Central configuration file providing:

**1. Skip Rules**
```python
SKIP_RULES = {
    "other": {
        "confidence_threshold": 0.5,
        "subcategories_always_skip": ["Logo", "Icon", "Decorative", "Page Furniture"]
    },
    "photograph": {
        "subcategories_always_skip": ["Decoration"]
    }
}
```

**2. Version Selection**
```python
PROMPT_VERSION = "claude"  # Change to "gpt", "claude", or "gemini"
```

**3. Model Configuration**
```python
MODEL_CONFIG = {
    "table": {"model": "gpt-4o", "max_tokens": 2000, "detail": "high"},
    "graph_chart": {"model": "gpt-4o-mini", "max_tokens": 1500, "detail": "high"},
    "diagram": {"model": "gpt-4o-mini", "max_tokens": 1500, "detail": "high"},
    "photograph": {"model": "gpt-4o-mini", "max_tokens": 1000, "detail": "high"},
    "other": {...}  # Per-subcategory configuration
}
```

**4. Utility Functions**
- `should_skip_image(main_category, subcategory, confidence)` - Determine if image should be skipped
- `get_prompt_file(main_category, subcategory)` - Get appropriate prompt filename
- `get_model_config(main_category, subcategory)` - Get model parameters
- `load_prompt(prompt_file)` - Load prompt from file
- `get_analysis_config(main_category, subcategory, confidence)` - Get complete config

---

## Usage in Stage 3

### Basic Usage

```python
from vis_stage_3_config import get_analysis_config, should_skip_image

# From Stage 2 output
main_category = "graph/chart"  # From Stage 2 categorization
subcategory = "Continuous"     # Parsed from full category
confidence = 0.85              # From Stage 2 confidence

# Get analysis configuration
config = get_analysis_config(main_category, subcategory, confidence)

if config is None:
    # Image should be skipped
    print("Skipping image based on rules")
else:
    # Proceed with analysis
    prompt = config["prompt"]
    model = config["model"]
    max_tokens = config["max_tokens"]
    detail = config["detail"]

    # Call OpenAI API with these parameters
    result = analyze_image(image_base64, prompt, model, max_tokens, detail)
```

### Switching Prompt Versions

To test different prompt versions (GPT vs Claude vs Gemini):

**Option 1: Edit config file**
```python
# In vis_stage_3_config.py, change:
PROMPT_VERSION = "claude"  # to "gpt" or "gemini"
```

**Option 2: Runtime override** (future enhancement)
```python
import vis_stage_3_config
vis_stage_3_config.PROMPT_VERSION = "gemini"
config = get_analysis_config(main_category, subcategory, confidence)
```

### Parsing Category/Subcategory

Stage 2 returns categories like:
- `"table"` - No subcategory
- `"graph/chart: Continuous"` - Parse out "Continuous"
- `"photograph: Evidence"` - Parse out "Evidence"
- `"diagram: Technical"` - Parse out "Technical"
- `"other: Screenshot: 0.85"` - Parse out "Screenshot" (confidence value separate)

```python
def parse_category(category_str: str) -> tuple:
    """Parse Stage 2 category into (main_category, subcategory)."""
    if ':' not in category_str:
        return category_str, None

    parts = category_str.split(':', 1)
    main_category = parts[0].strip()
    subcategory = parts[1].strip()

    # Handle "other" confidence scores
    if main_category == "other" and ':' in subcategory:
        subcat_parts = subcategory.split(':', 1)
        subcategory = subcat_parts[0].strip()

    return main_category, subcategory
```

---

## Category/Subcategory Reference

### Tables
- **Main**: `table`
- **Subcategories**: None
- **Versions**: 1 (no variants)

### Graphs/Charts
- **Main**: `graph/chart`
- **Subcategories**:
  - Continuous
  - Categorical
  - Distribution
  - Relationship
  - Matrix
  - Other
- **Versions**: 3 (gpt, claude, gemini)

### Diagrams
- **Main**: `diagram`
- **Subcategories**:
  - Conceptual
  - Technical
  - Explanatory
  - Other
- **Versions**: 3 (gpt, claude, gemini)

### Photographs
- **Main**: `photograph`
- **Subcategories**:
  - Evidence
  - Demonstration
  - Identification
  - Documentation
  - Illustration
  - Environmental Context
  - Equipment / Asset Visualization
  - Condition / Anomaly Evidence
  - Comparative / Before-After
  - Spatial / Locational Reference
- **Versions**: 1 (no variants)

### Other
- **Main**: `other`
- **Subcategories**:
  - Screenshot
  - Infographic
  - Mixed Content
  - Text Block
  - Unclassifiable
  - Watermark
  - Fragment
  - *Skip*: Logo, Icon, Decorative, Page Furniture
- **Versions**: 3 (gpt, claude, gemini)

---

## Prompt File Format

All prompts follow this structure:

```markdown
# [Category: Subcategory] ([Version])

[Brief description]

## EXTRACTION OBJECTIVES

[Numbered list of what to extract]

## EXTRACTION APPROACH

[Step-by-step approach]

## CONFIDENCE SCORING

[Guidelines for assigning confidence scores]

## SPECIAL CONSIDERATIONS

[Category-specific notes and edge cases]
```

Prompts contain **ONLY** the prompt text. JSON schemas are documented separately (future: may be in schema files).

---

## Migration Checklist

- [x] Create 62 prompt files organized by category/subcategory
- [x] Create `vis_stage_3_config.py` with routing logic
- [x] Define skip rules for low-value images
- [x] Define model configurations per category
- [x] Implement version selection mechanism
- [ ] Update `vis_stage_3_visual_analysis.py` to use new config (next step)
- [ ] Test with sample Stage 2 output
- [ ] Archive old model-specific prompt files

---

## Next Steps

1. **Update Stage 3 script** (`vis_stage_3_visual_analysis.py`)
   - Import from `vis_stage_3_config`
   - Use `get_analysis_config()` for routing
   - Implement category parsing
   - Handle skip logic

2. **Testing**
   - Test all 62 prompt files load correctly
   - Test version switching (gpt/claude/gemini)
   - Test skip rules work as expected
   - Validate JSON output schemas

3. **Archive Old Files**
   - Move old model-specific files to `_archive/` directory
   - Keep for reference during testing

---

## Benefits

### Before
- Prompts mixed by model, hard to compare subcategory approaches
- Had to duplicate schemas across files
- No central configuration
- Version switching required editing multiple files

### After
- ✅ Prompts organized by category/subcategory
- ✅ Easy A/B testing between GPT/Claude/Gemini versions
- ✅ Central configuration with skip rules
- ✅ Version switching via single variable
- ✅ Clean separation: prompts in .md files, logic in .py config
- ✅ Scalable structure for adding new categories
- ✅ Consistent file naming convention

---

## File Naming Convention

```
{category}_{subcategory}_{version}.md

Examples:
  graph_chart_continuous_claude.md
  diagram_technical_gpt.md
  photograph_evidence.md  (no version suffix)
  other_screenshot_gemini.md
```

**Rules**:
- Category and subcategory separated by `_`
- Spaces replaced with `_`
- Forward slashes (`/`) replaced with `_`
- Version suffix only for categories with variants
- Lowercase filenames

---

## Questions?

See `vis_stage_3_config.py` for implementation details and inline documentation.
