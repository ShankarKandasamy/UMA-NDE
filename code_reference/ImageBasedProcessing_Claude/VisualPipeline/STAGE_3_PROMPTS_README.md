# Stage 3: Graph/Chart Analysis - Prompt Organization

## Overview

Stage 3 analyzes graphs and charts detected in Stage 2 using **category-specific prompts** to extract structured data. Instead of a one-size-fits-all approach, each chart type gets a specialized prompt and JSON schema optimized for its visual features.

## Architecture

```
Stage 2 Output → Prompt Manager → Category-Specific Prompts → LLM Analysis → Structured JSON
     ↓                                         ↓
"graph/chart: Continuous"              Continuous prompt + schema
```

## File Organization

```
VisualPipeline/
├── vis_stage_3_prompts/
│   └── graphs_charts.md          # Source prompts (reference only)
├── vis_stage_3_prompt_manager.py # Main prompt manager (use this!)
└── vis_stage_3_example.py        # Usage examples
```

## Supported Categories

Based on Stage 2 subcategories:

| Stage 2 Category | Subcategory | Charts Included |
|-----------------|-------------|-----------------|
| `graph/chart: Continuous` | Continuous | Line, Area, Scatter |
| `graph/chart: Categorical` | Categorical | Bar, Stacked Bar, Grouped Bar, Pie, Donut |
| `graph/chart: Distribution` | Distribution | Histogram, Box Plot, Violin Plot |
| `graph/chart: Relationship` | Relationship | Flowchart, Sankey, Network Graph |
| `graph/chart: Matrix` | Matrix | Heatmap, Confusion Matrix |
| `graph/chart: Other` | Other | Radar, Funnel, Waterfall, Gauge |

## Usage

### Basic Usage

```python
from vis_stage_3_prompt_manager import get_prompt_for_category

# Get prompt and schema for a specific category
category = "graph/chart: Continuous"
prompt_data = get_prompt_for_category(category)

# Access components
system_prompt = prompt_data['system_prompt']  # Global instruction
user_prompt = prompt_data['user_prompt']      # Category-specific prompt
schema = prompt_data['schema']                # Expected JSON schema
subcategory = prompt_data['subcategory']      # Normalized subcategory name
```

### Integration with OpenAI API

```python
from openai import OpenAI
import base64
import json

client = OpenAI()

# Load image
with open(image_path, "rb") as img_file:
    base64_image = base64.b64encode(img_file.read()).decode('utf-8')

# Get category-specific prompt
prompt_data = get_prompt_for_category(detection['category'])

# Call OpenAI API
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": prompt_data['system_prompt']
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_data['user_prompt']
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
    response_format={"type": "json_object"},
    temperature=0.0
)

# Parse and validate
result = json.loads(response.choices[0].message.content)
```

### Validation

```python
from vis_stage_3_prompt_manager import validate_response

# Validate that the response matches the expected schema
is_valid = validate_response(category, result)

if is_valid:
    print("[OK] Response validated successfully")
else:
    print("[ERROR] Response validation failed")
```

### Helper Functions

```python
from vis_stage_3_prompt_manager import (
    get_schema_for_category,
    list_supported_categories
)

# Get just the schema
schema = get_schema_for_category("graph/chart: Continuous")

# List all supported subcategories
categories = list_supported_categories()
# Returns: ['Continuous', 'Categorical', 'Distribution', 'Relationship', 'Matrix', 'Other']
```

## Prompt Design

### Global System Instruction

Applied to ALL graph/chart types:
- Extract OCR text
- Interpolate numerical values from visual scales
- Use ranges ("40–60") when precision is uncertain
- Detect turning points and trends
- Output strict JSON only

### Category-Specific Prompts

Each subcategory has a specialized prompt focusing on:

**Continuous Charts**:
- Extract values for every X-axis tick
- Identify turning points (local min/max, direction changes)
- Track multi-series data with color/style differentiation

**Categorical Charts**:
- Interpolate bar heights per category/series
- Extract pie/donut percentages from angular proportions
- Distinguish series by color and legend

**Distribution Charts**:
- Histogram: bin ranges and heights
- Box plot: min, Q1, median, Q3, max
- Violin plot: density shape and spread

**Relationship Diagrams**:
- Extract nodes, labels, locations
- Map edges with flow magnitudes (Sankey)
- Qualitative weights when values unavailable

**Matrix Charts**:
- Extract all cell values
- Approximate via color intensity if needed
- Identify clusters and anomalies

**Other Charts**:
- Radar: axis values
- Funnel: stage values
- Waterfall: sequential changes
- Gauge: current value

## Schema Structure

All schemas include:
- `chart_type`: Main type (e.g., "continuous")
- `chart_subtype`: Specific chart (e.g., "line | area | scatter")
- `ocr_text`: All extracted text
- `key_insights`: High-level observations
- `trends`: Trend descriptions per series
- `meta`: Processing metadata and issues

Type-specific fields:
- Continuous: `axes`, `series`, `turning_points`
- Categorical: `categories`, `series`, `pie_slices`
- Distribution: `histogram_bins`, `box_plots`, `violin_plots`
- Relationship: `nodes`, `edges`
- Matrix: `x_labels`, `y_labels`, `cells`
- Other: `radar_axes`, `funnel_levels`, `waterfall_steps`, `gauge`

## Error Handling

The prompt manager handles edge cases gracefully:

1. **No subcategory specified** (`"graph/chart"`):
   - Defaults to "Other" subcategory

2. **Unknown subcategory**:
   - Warns and defaults to "Other"

3. **Non-graph categories** (`"table"`, `"photograph"`, etc.):
   - Returns `None`

4. **Validation failure**:
   - Checks required top-level keys
   - Verifies `chart_type` matches expected value

## Testing

Run the test suite:

```bash
python vis_stage_3_prompt_manager.py
```

See example integration:

```bash
python vis_stage_3_example.py
```

## Next Steps

1. **Implement Stage 3 script** (`vis_stage_3_extract.py`):
   - Read Stage 2 metadata
   - Loop through detections
   - Call `get_prompt_for_category()` for each graph/chart
   - Make LLM API calls with category-specific prompts
   - Validate and save extracted data

2. **Add prompt variants**:
   - Create prompts for other categories (tables, diagrams)
   - Store in separate markdown files
   - Extend prompt manager to handle all Stage 2 categories

3. **Optimize costs**:
   - Use `gpt-4o-mini` for simple charts
   - Use `gpt-4o` for complex multi-series or dense data
   - Implement confidence-based retry logic

## Design Rationale

**Why category-specific prompts?**
- Better extraction accuracy (optimized for visual features)
- Cleaner schemas (only relevant fields)
- Lower token usage (shorter, focused prompts)
- Easier validation (strict schema per type)

**Why in-code instead of file loading?**
- Faster (no file I/O overhead)
- Type-safe (schemas are Python dicts)
- Easy testing (self-contained module)
- Version control friendly (single source of truth)

**Why keep `graphs_charts.md`?**
- Reference documentation
- Easy to review all prompts at once
- Can be used to regenerate code if needed
- Human-readable format for prompt engineering

---

**Last Updated**: 2025-12-08
**Status**: ✅ Production ready
**Dependencies**: None (standalone module)
