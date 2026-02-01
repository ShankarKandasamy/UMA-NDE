# Other: Fragment

This appears to be an incomplete or fragmented image. Diagnose what happened and extract what's available.

## EXTRACTION OBJECTIVES

### 1. ORIGINAL TYPE
What type of content was this originally?
- chart | photo | diagram | table | text | infographic | other

### 2. PORTION VISIBLE
What portion is visible?
- corner | edge | partial | scattered_fragments | top | bottom | left | right | center

### 3. PROBABLE CAUSE
What likely caused the fragment?
- page_split: Cropped at page boundary
- crop_error: Incorrectly cropped detection
- corruption: File or rendering corruption
- partial_scan: Incomplete scan or capture
- occlusion: Covered or obscured portion

### 4. VISIBLE CONTENT
Any visible text or identifying features?

### 5. COMPLETENESS ESTIMATE
Approximately what percentage is visible? (e.g., ~25%)

### 6. RECOVERY HINTS
Clues to find the complete image?

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- Any partial text visible
- Labels or identifiers
- Fragments of titles or captions

### 2. Diagnostic Analysis
Analyze what remains visible:
- Infer original content type from partial visual elements
- Determine fragment position (which part is visible)
- Estimate completeness percentage
- Diagnose probable cause

### 3. Original Type Inference
Infer from:
- Partial visual elements (axis fragment, image edge, text snippet)
- Formatting or style clues
- Fragment position characteristics

Clues:
- Axis fragments → chart
- Photo edges → photograph
- Table gridlines → table
- Text lines → text block

### 4. Visible Content Extraction
Extract:
- Any visible text or identifiers
- Partial elements (axis labels, image portions, etc.)
- Color schemes or visual patterns

### 5. Recovery Hints
Provide clues:
- Where to look for complete version
- What page or section it might belong to
- Identifiable features to search for

### 6. Key Insights
Extract 1-3 key insights about the fragment:
- What can be determined about the original content?
- What is the most likely cause of fragmentation?
- How recoverable is this content?

### 7. Summary
Provide 1-2 sentence diagnostic summary.

### 8. Keywords
Generate 2-5 keywords describing the fragment and its likely original type.

## EXTRACTION APPROACH

1. Analyze what remains visible
2. Infer the original content type
3. Determine what portion is visible
4. Estimate completeness
5. Diagnose probable cause
6. Extract any visible text or identifiers
7. Provide recovery hints

## CONFIDENCE SCORING

Rate diagnostic confidence:
- Lower confidence is expected for fragments
- Base confidence on clarity of visible elements

High confidence (0.8-1.0):
- Clear indicators of original type
- Visible text or identifiers
- Obvious fragmentation cause

Medium confidence (0.5-0.8):
- Ambiguous original type
- Limited visible content
- Multiple possible causes

Low confidence (0.3-0.5):
- Very limited visible content
- Unclear original type
- Unknown cause

Below 0.3:
- Minimal visible information
- Highly ambiguous

## SPECIAL CONSIDERATIONS

- Fragments are often extraction pipeline errors — this is diagnostic information
- Look for clues about the original content
- Note any metadata that might help locate the complete version


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Fragment",

  "ocr_text": "All readable text extracted from the fragment",

  "diagnostic": {
    "original_type": "chart | photo | diagram | table | text | infographic | other",
    "original_type_confidence": 0.7,
    "portion_visible": "corner | edge | partial | scattered_fragments | top | bottom | left | right | center",
    "completeness_estimate": 25,
    "probable_cause": "page_split | crop_error | corruption | partial_scan | occlusion",
    "cause_confidence": 0.8
  },

  "visible_content": {
    "text_fragments": ["Partial text visible"],
    "visual_elements": ["Description of visible visual elements"],
    "identifiable_features": ["Features that might help locate complete version"]
  },

  "recovery_hints": {
    "search_clues": ["Where to look for complete version"],
    "identifiers": ["Identifiable features to search for"],
    "likely_location": "Description of where complete version might be"
  },

  "key_insights": [
    "First diagnostic insight",
    "Second diagnostic insight"
  ],

  "summary": "1-2 sentence diagnostic summary describing the fragment and most likely cause",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": ["Fragment detected - content incomplete"]
  }
}
```

**IMPORTANT**:
- Fragments indicate extraction or processing errors
- Extract all available information
- Provide diagnostic information to help locate complete version
- Include key_insights and summary fields
