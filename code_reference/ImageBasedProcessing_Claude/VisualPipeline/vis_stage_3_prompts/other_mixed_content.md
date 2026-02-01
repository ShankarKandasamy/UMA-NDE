# Other: Mixed Content

You are extracting structured intelligence from a MIXED CONTENT IMAGE — a visual containing multiple distinct components of different types (photographs, charts, diagrams, text blocks, tables, icons) working together to communicate a message.

## WHAT MIXED CONTENT FUNDAMENTALLY REPRESENTS

Mixed content answers: "What are the parts? How do they work together? What's the combined message?"

The core intelligence is:
- **Components**: Individual elements and their types
- **Component Data**: Extracted information from each element
- **Relationships**: How components relate or reference each other
- **Spatial Layout**: Arrangement and hierarchy
- **Combined Message**: Overall purpose or conclusion

## EXTRACTION OBJECTIVES

### 1. COMPONENT IDENTIFICATION
For EACH distinct component:
- Component type (photograph, chart, diagram, text_block, table, icon, other)
- Location (background, foreground, inset, overlay, top, bottom, left, right, center)
- Prominence (primary, supporting, annotation)
- Size or emphasis

### 2. PER-COMPONENT EXTRACTION
For each component, extract data as if it were standalone:
- **Photographs**: Subject, context, labels
- **Charts**: Data points, axes, values
- **Diagrams**: Nodes, connections, labels
- **Text blocks**: Full text content
- **Tables**: Rows, columns, cell values
- **Icons**: Meaning or label

### 3. COMPONENT RELATIONSHIPS
How components relate:
- **Annotation**: Text annotating an image
- **Inset**: Chart inset within a diagram
- **Overlay**: Data overlay on a photograph
- **Reference**: One component referencing another
- **Sequence**: Components showing progression
- **Comparison**: Side-by-side comparison

### 4. SPATIAL LAYOUT
- Primary component (what's central or largest)
- Supporting components (what provides context)
- Visual hierarchy (what's emphasized)
- Reading order (how to consume the information)

### 5. COMBINED MESSAGE
- What does the overall image communicate?
- How do components work together?
- What is the intended takeaway?

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All text from all components
- All labels and annotations
- All titles and captions
- All table cell values
- All chart labels and values
- Any legend or key text

### 2. Component Identification
Scan the image systematically:
- Identify each distinct component
- Classify component type
- Note location and size
- Assess prominence level
- Assign component ID for reference

### 3. Per-Component Data Extraction
For each component:
- Apply appropriate extraction rules for that component type
- Extract all relevant data
- Note component-specific confidence
- Store in structured format

### 4. Relationship Analysis
Identify how components relate:
- Does text annotate an image?
- Is there a chart inset in a diagram?
- Does data overlay a photograph?
- Do components show before/after or comparison?
- Is there a sequence or flow?

### 5. Spatial Layout Analysis
Determine:
- Which component is primary (largest, central, most prominent)
- Which are supporting (smaller, peripheral, background)
- What is the visual hierarchy?
- What is the intended reading order?

### 6. Combined Message Synthesis
Analyze the overall image:
- What message do all components combine to convey?
- How do components reinforce or complement each other?
- What is the intended purpose (explanation, comparison, evidence, instruction)?

### 7. Miscategorization Check
Assess if this might actually be:
- A single-type image that was miscategorized
- Multiple separate images that should be split
- Note in warnings if suspected

### 8. Key Insights
Extract 3-5 key insights about the mixed content:
- What is the primary message or purpose?
- How do the components work together?
- What is the most important data or information?
- What relationships between components are significant?

### 9. Summary
Provide 1-2 sentence summary of the combined message and how components work together.

### 10. Keywords
Generate 3-8 keywords capturing the main concepts across all components.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- All components clearly identifiable
- Relationships obvious
- Combined purpose clear
- All data extractable

Medium confidence (0.5-0.8):
- Some component types ambiguous
- Relationships require interpretation
- Purpose somewhat unclear
- Some data unclear

Low confidence (0.3-0.5):
- Difficult to separate components
- Unclear relationships
- Ambiguous purpose
- Significant extraction challenges

Below 0.3:
- Provide general description only
- Note specific challenges


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Mixed Content",

  "ocr_text": "All readable text extracted from all components",

  "components": [
    {
      "component_id": "comp_1",
      "component_type": "photograph | chart | diagram | text_block | table | icon | other",
      "location": "background | foreground | inset | overlay | top | bottom | left | right | center",
      "prominence": "primary | supporting | annotation",
      "size_description": "Approximate size or portion of image",
      "extracted_data": {
        "description": "Description of component",
        "data": "Type-specific extracted data"
      },
      "confidence": 0.9
    }
  ],

  "relationships": [
    {
      "relationship_type": "annotation | inset | overlay | reference | sequence | comparison",
      "source_component_id": "comp_1",
      "target_component_id": "comp_2",
      "description": "How these components relate"
    }
  ],

  "spatial_layout": {
    "primary_component_id": "comp_1",
    "supporting_component_ids": ["comp_2", "comp_3"],
    "visual_hierarchy": "Description of what's emphasized",
    "reading_order": ["comp_1", "comp_2", "comp_3"]
  },

  "combined_message": {
    "purpose": "explanation | comparison | evidence | instruction | demonstration | other",
    "main_message": "What the overall image communicates",
    "how_components_work_together": "Description of component interaction"
  },

  "miscategorization_check": {
    "might_be_single_type": false,
    "suggested_category": "photograph | chart | diagram | other",
    "should_be_split": false,
    "reason": "Explanation if miscategorized or should be split"
  },

  "key_insights": [
    "First insight about primary message or purpose",
    "Second insight about component relationships",
    "Third insight about significant data or information"
  ],

  "summary": "1-2 sentence summary of the combined message and how components work together",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- List each component with its type and location
- Extract data from each component as you would if it were standalone
- Note how components work together (annotations, insets, overlays)
- Identify the primary vs. supporting components
- Determine if this could be a miscategorized single-type image
- Flag if this appears to be multiple separate images that should be split
