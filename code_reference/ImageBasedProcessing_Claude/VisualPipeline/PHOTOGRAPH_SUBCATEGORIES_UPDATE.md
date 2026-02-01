# Photograph Subcategories - Implementation Summary

## Overview

Successfully updated Stage 2 categorization and Stage 3 prompt manager to support **11 photograph subcategories** with specialized extraction prompts.

## Files Updated

### 1. **vis_stage_2_categorize.py** ✅
**Changes:**
- Added 11 photograph subcategories to categorization prompt
- Updated response format to require subcategory for photographs
- Format: `"photograph: Evidence"` (or other subcategory)

**Photograph Subcategories:**
```
A. Evidence - Proof or raw data (scientific, legal, measurement-oriented)
B. Demonstration - Shows how to perform actions (procedural instructions)
C. Identification - Shows who or what (people, equipment, products, locations)
D. Documentation - Records state or condition at a particular moment
E. Illustration - Abstract or supportive imagery clarifying concepts
F. Decoration - Stock or aesthetic imagery with low informational value
G. Environmental Context - Shows surroundings rather than the object of study
H. Equipment / Asset Visualization - Focus on machines, devices, components, tools
I. Condition / Anomaly Evidence - Focus on defects, damage, abnormalities
J. Comparative / Before-After - Shows differences across time or conditions
K. Spatial / Locational Reference - Geographic or spatial positioning
```

**Parsing Logic:**
- Extracts main category: `"photograph"` from `"photograph: Evidence"`
- Stores both full category (`photograph: Evidence`) and main category (`photograph`)
- Existing parsing logic handles subcategories correctly (validated)

---

### 2. **vis_stage_3_prompt_manager.py** ✅
**Changes:**
- Renamed from graph/chart-specific to general image analysis
- Added `PHOTOGRAPH_SYSTEM_INSTRUCTION` - specialized system prompt for photographs
- Added `PHOTOGRAPH_PROMPTS` - 11 subcategory-specific user prompts
- Added `PHOTOGRAPH_SCHEMA` - universal extraction schema for all photograph types
- Updated `get_prompt_for_category()` to handle both `graph/chart` and `photograph`
- Updated validation function to handle photograph schemas
- Updated helper functions for multi-category support

**Photograph Schema Structure:**
```json
{
  "image_type": "photograph",
  "subcategory": "Evidence",
  "ocr_text": "",
  "visual_description": {
    "main_subject": "",
    "key_objects": [],
    "setting": "",
    "composition": ""
  },
  "text_elements": {
    "labels": [],
    "annotations": [],
    "captions": [],
    "watermarks": [],
    "measurements": [],
    "identifiers": []
  },
  "subjects": [{
    "type": "",
    "description": "",
    "identifiers": [],
    "condition": "",
    "location_in_image": ""
  }],
  "spatial_info": {
    "layout": "",
    "perspective": "",
    "scale_reference": "",
    "coordinates": null
  },
  "annotations_overlays": [{
    "type": "",
    "purpose": "",
    "location": "",
    "text": null
  }],
  "measurements": [{
    "type": "",
    "value": "",
    "unit": ""
  }],
  "anomalies": [{
    "description": "",
    "location": "",
    "severity": "",
    "highlighted": false
  }],
  "temporal_info": {
    "timestamp": null,
    "sequence_indicator": null,
    "temporal_context": ""
  },
  "key_insights": [],
  "meta": {
    "quality": "",
    "issues": []
  }
}
```

**Subcategory-Specific Prompts:**
Each photograph subcategory has a tailored user prompt focusing on relevant features:
- **Evidence**: Measurements, scales, markers, anomalies
- **Demonstration**: Actions, steps, annotations, sequence
- **Identification**: Identifiers, labels, distinctive features
- **Documentation**: State, condition, neutral documentation
- **Equipment / Asset Visualization**: Equipment details, specifications, condition
- **Condition / Anomaly Evidence**: Defects, damage, anomalies, severity
- **Comparative / Before-After**: Differences, changes, comparison markers
- *(and 4 more...)*

---

### 3. **vis_stage_3_example.py** ✅
**Changes:**
- Added photograph detection examples
- Demonstrates photograph subcategory handling
- Shows expected schema output for photographs

---

### 4. **test_photograph_subcategories.py** ✅
**New File:**
- Validates parsing logic for all 11 photograph subcategories
- Tests main category extraction
- Confirms backward compatibility with graph/chart categories

---

## Usage Examples

### Stage 2 Output → Stage 3 Input

```python
# Stage 2 categorizes an image
detection = {
    "file_path": "page_1/equipment_photo.png",
    "category": "photograph: Equipment / Asset Visualization",
    "main_category": "photograph",
    "confidence": 0.92
}

# Stage 3 retrieves specialized prompt
from vis_stage_3_prompt_manager import get_prompt_for_category

prompt_data = get_prompt_for_category(detection['category'])

# Returns:
{
    "system_prompt": "You are a photograph-analysis AI...",
    "user_prompt": "You are analyzing a photograph of equipment, machinery, or assets...",
    "schema": { ... photograph schema ... },
    "subcategory": "Equipment / Asset Visualization",
    "category_type": "photograph"
}
```

### OpenAI API Integration

```python
from openai import OpenAI
import base64

client = OpenAI()

# Get category-specific prompt
prompt_data = get_prompt_for_category("photograph: Evidence")

# Load and encode image
with open(image_path, "rb") as img_file:
    base64_image = base64.b64encode(img_file.read()).decode('utf-8')

# Call API with specialized prompt
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
                {"type": "text", "text": prompt_data['user_prompt']},
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

---

## Testing Results

### Prompt Manager Test
```bash
$ python vis_stage_3_prompt_manager.py
```

**Output:**
```
Testing Prompt Manager
================================================================================

Category: photograph: Evidence
  Category Type: photograph
  Subcategory: Evidence
  User Prompt Length: 387 chars
  Schema Keys: ['image_type', 'subcategory', 'ocr_text', 'visual_description', ...]

Category: photograph: Equipment / Asset Visualization
  Category Type: photograph
  Subcategory: Equipment / Asset Visualization
  User Prompt Length: 364 chars
  Schema Keys: ['image_type', 'subcategory', 'ocr_text', 'visual_description', ...]

[... 9 more photograph subcategories ...]

Supported Categories:

  graph/chart:
    - Continuous
    - Categorical
    - Distribution
    - Relationship
    - Matrix
    - Other

  photograph:
    - Evidence
    - Demonstration
    - Identification
    - Documentation
    - Illustration
    - Decoration
    - Environmental Context
    - Equipment / Asset Visualization
    - Condition / Anomaly Evidence
    - Comparative / Before-After
    - Spatial / Locational Reference
```

### Subcategory Parsing Test
```bash
$ python test_photograph_subcategories.py
```

**Output:**
```
All tests passed! Photograph subcategories will parse correctly.
```

---

## Complete Category Support Matrix

| Main Category | Subcategories | Stage 2 Support | Stage 3 Prompts | Schema |
|--------------|---------------|-----------------|-----------------|--------|
| **graph/chart** | 6 subcategories | ✅ | ✅ | ✅ Unique per type |
| **photograph** | 11 subcategories | ✅ | ✅ | ✅ Universal |
| **diagram** | 4 subcategories | ✅ | ⏳ Pending | ⏳ Pending |
| **table** | No subcategories | ✅ | ⏳ Pending | ⏳ Pending |
| **other** | No subcategories | ✅ | N/A | N/A |

---

## Architecture

```
Stage 2: Image Categorization
     ↓
"photograph: Evidence"
     ↓
Stage 3: Prompt Manager
     ↓
get_prompt_for_category()
     ↓
Returns:
  - PHOTOGRAPH_SYSTEM_INSTRUCTION (global)
  - Evidence-specific user prompt (subcategory)
  - PHOTOGRAPH_SCHEMA (universal)
     ↓
LLM API Call (GPT-4o-mini / GPT-4o)
     ↓
Structured JSON Extraction
```

---

## Key Design Decisions

### 1. **Universal Schema for Photographs**
Unlike graphs/charts (which have type-specific schemas), all photograph subcategories use the **same schema**.

**Rationale:**
- Photographs share common extraction needs (OCR, subjects, spatial info, annotations)
- Subcategory affects **focus** of analysis, not **structure** of output
- Simpler validation and processing logic
- Easier to extend with new subcategories

### 2. **Subcategory-Specific Prompts**
Each subcategory has a **tailored user prompt** emphasizing relevant features.

**Example:**
- **Evidence** prompt: "Extract all visible measurements, scales, labels..."
- **Demonstration** prompt: "Identify the action being demonstrated..."
- **Equipment** prompt: "Identify the equipment type, manufacturer..."

**Benefit:** Guides the LLM to focus on category-relevant information

### 3. **Title Case Normalization**
Photograph subcategories use `title()` instead of `capitalize()` to handle multi-word subcategories.

**Examples:**
- `"equipment / asset visualization"` → `"Equipment / Asset Visualization"`
- `"condition / anomaly evidence"` → `"Condition / Anomaly Evidence"`

---

## Next Steps

### Immediate
- ✅ Stage 2 categorization updated
- ✅ Stage 3 prompt manager updated
- ✅ Testing completed

### Future Enhancements
1. **Add diagram subcategory prompts** (4 subcategories defined in Stage 2)
2. **Add table extraction prompts** (no subcategories, but needs Stage 3 support)
3. **Implement actual Stage 3 extraction script** (vis_stage_3_extract.py)
4. **Add confidence-based model selection** (gpt-4o for complex, gpt-4o-mini for simple)
5. **Implement retry logic** for failed extractions

---

## Files Created/Updated

**Updated:**
- `vis_stage_2_categorize.py` - Added photograph subcategories
- `vis_stage_3_prompt_manager.py` - Added photograph support
- `vis_stage_3_example.py` - Added photograph examples

**Created:**
- `test_photograph_subcategories.py` - Validation tests
- `PHOTOGRAPH_SUBCATEGORIES_UPDATE.md` - This summary

---

**Last Updated**: 2025-12-08
**Status**: ✅ Production ready
**Testing**: ✅ All tests passing
**Documentation**: ✅ Complete
