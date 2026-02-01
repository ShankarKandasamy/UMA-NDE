# Stage 4 Visual Analysis - Prompt Structure

## Modular Prompt Architecture

The VLM receives a structured prompt composed of three components:

```
FINAL_PROMPT = GENERAL_PROMPT + CATEGORY_PROMPT + OUTPUT_PROMPT
```

---

## 1. GENERAL_PROMPT (Universal)

**Purpose**: Applies to ALL images, provides context usage instructions

**Location**: `stage_4_visual_analysis.py` (lines 86-107)

**Content**:
```
================================================================================
DOCUMENT CONTEXT
================================================================================

You are analyzing an image extracted from a larger document. The image appears in
context with surrounding text that provides important information about its purpose,
content, and relevance.

{context_section}  <-- Injected dynamically with before/after text

USE THIS CONTEXT TO:
  • Identify the image's purpose and relevance within the document
  • Extract accurate titles, captions, or labels mentioned in the surrounding text
  • Identify key concepts, terminology, and domain-specific keywords
  • Understand relationships between the image and surrounding content
  • Improve summary accuracy by aligning with the document's narrative
  • Detect explicit references to this image (e.g., 'Figure 1', 'Table 2', 'as shown above')
  • Incorporate contextual information into your analysis where relevant

================================================================================
```

**Dynamic Context Section** (injected via `{context_section}`):
```
--- TEXT BEFORE IMAGE ---
[100 tokens of closest text before image]

--- TEXT AFTER IMAGE ---
[100 tokens of closest text after image]
```

If no context available:
```
No surrounding text context available for this image.
```

---

## 2. CATEGORY_PROMPT (Category-Specific)

**Purpose**: Task-specific extraction instructions for each image type

**Location**: `vis_stage_3_prompts/` directory (loaded via `vis_stage_3_config.py`)

**Examples**:
- `table_gpt.md` - Table extraction with row/column structure
- `graph_chart_gpt.md` - Chart data extraction with axis/legend details
- `diagram_gpt.md` - Diagram structure and relationship extraction
- `photograph_evidence_gpt.md` - Photograph analysis for specific subcategories

**Content**: Category-specific JSON schemas, extraction rules, and examples

---

## 3. OUTPUT_PROMPT (Universal)

**Purpose**: Standardizes JSON output format across ALL images

**Location**: `stage_4_visual_analysis.py` (lines 110-123)

**Content**:
```
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
```

---

## Prompt Assembly Flow

1. **Context Extraction** (`get_context_text()`)
   - Finds 100 tokens before/after image based on proximity
   - Filters noise buckets (< 20 chars)
   - Builds context section string

2. **General Section** (`analyze_image()`)
   - Injects context into `GENERAL_PROMPT.format(context_section=...)`
   - Results in universal context usage instructions

3. **Category Section** (`analyze_images()`)
   - Loads category-specific prompt via `get_analysis_config()`
   - Contains extraction schema and task-specific rules

4. **Output Section** (`analyze_image()`)
   - Appends `OUTPUT_PROMPT` to ensure consistent JSON formatting

5. **Final Assembly**
   ```python
   final_prompt = general_section + "\n" + category_prompt + "\n" + OUTPUT_PROMPT
   ```

---

## Benefits of Modular Structure

✅ **Maintainability**: Context instructions in one place, easy to update  
✅ **Consistency**: All images get same general + output instructions  
✅ **Flexibility**: Category-specific prompts can be edited independently  
✅ **Clarity**: Clear separation of concerns (context → task → output)  
✅ **Testability**: Each component can be tested in isolation  
✅ **Extensibility**: Easy to add new universal instructions to GENERAL_PROMPT

---

## Example Final Prompt (Table)

```
================================================================================
DOCUMENT CONTEXT
================================================================================
[...general instructions...]

--- TEXT BEFORE IMAGE ---
The quarterly financial results are shown below. Revenue increased by 15%...

--- TEXT AFTER IMAGE ---
These results demonstrate strong growth across all product categories...

================================================================================

[CATEGORY-SPECIFIC TABLE EXTRACTION PROMPT FROM vis_stage_3_prompts/table_gpt.md]

================================================================================
OUTPUT REQUIREMENTS
================================================================================
• Return ONLY valid JSON matching the schema...
================================================================================
```

