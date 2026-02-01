# Other: Unclassifiable

You are attempting to extract information from an image that cannot be confidently classified into standard categories (photograph, diagram, chart, infographic, text block, screenshot, etc.). This may be due to poor quality, unusual content, abstract visuals, or genuinely ambiguous imagery.

## WHAT UNCLASSIFIABLE IMAGES REPRESENT

Unclassifiable images present: "What can we determine? What's unclear? Why is classification difficult?"

The focus is:
- **Best Guess**: What might this be?
- **Visible Elements**: What can be discerned?
- **Classification Barriers**: Why is it unclassifiable?
- **Potential Value**: Is there useful information despite ambiguity?
- **Recommendations**: What would help classification?

## EXTRACTION OBJECTIVES

### 1. VISUAL DESCRIPTION
- General appearance
- Colors and shapes visible
- Any recognizable elements
- Spatial arrangement

### 2. POSSIBLE TYPE ASSESSMENT
Best guess at what this might be:
- **photograph**: But subject unclear
- **diagram**: But structure unclear
- **chart**: But data unclear
- **infographic**: But sections unclear
- **text_block**: But text unreadable
- **screenshot**: But application unclear
- **abstract**: No clear representation
- **decorative**: Purely aesthetic
- **corrupted**: File or rendering issue
- **other**: None of the above

### 3. VISIBLE ELEMENTS
Any discernible features:
- Text fragments (even if partial)
- Shapes or geometric elements
- Colors or color patterns
- Edges or boundaries
- Possible objects or subjects

### 4. CLASSIFICATION BARRIERS
Why this cannot be classified:
- **poor_quality**: Low resolution, blur, noise
- **partial_view**: Fragment or truncated
- **corruption**: File damage or rendering error
- **abstract**: Non-representational content
- **ambiguous**: Multiple interpretations possible
- **complex**: Too many mixed elements
- **unusual**: Doesn't fit standard categories

### 5. VALUE ASSESSMENT
- Is there useful extractable information?
- Could higher quality help?
- Should this be flagged for review?
- Is it likely decorative or non-essential?

### 6. RECOMMENDATIONS
What would help classification or extraction:
- Higher resolution version
- Context from surrounding content
- Original file instead of screenshot
- Human review
- Alternative format

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- Any partial or fragmentary text
- Individual characters or words even if incomplete
- Numbers or symbols
- Labels if discernible
- Note if OCR is failing due to image quality

### 2. Visual Description
Provide detailed description:
- Overall appearance
- Predominant colors
- Visible shapes or patterns
- Approximate layout or composition
- Any recognizable features

### 3. Possible Type Guess
Make best-effort classification:
- What category might this fit?
- What clues support this guess?
- What clues contradict this guess?
- Assign confidence to guess (usually low)

### 4. Element Identification
List any discernible elements:
- Text fragments, even partial
- Geometric shapes (rectangles, circles, lines)
- Possible objects or subjects
- Icons or symbols
- Boundaries or regions

### 5. Barrier Identification
Explain classification difficulty:
- Image quality issues (resolution, blur, noise, contrast)
- Completeness issues (truncated, partial, fragmented)
- Content issues (abstract, ambiguous, unusual)
- Technical issues (corruption, encoding, rendering)

### 6. Value Assessment
Evaluate potential usefulness:
- Is there any extractable data or information?
- Could this be important despite ambiguity?
- Is it likely decorative or non-essential?
- Should it be flagged for manual review?

### 7. Recommendations
Suggest next steps:
- Request higher quality version
- Check surrounding document context
- Attempt alternative extraction methods
- Flag for human review
- Skip as non-essential

### 8. Key Insights
Extract 2-3 key insights about the unclassifiable image:
- What is the most likely type or purpose?
- What are the main barriers to classification?
- What would be most helpful to resolve ambiguity?

### 9. Summary
Provide 1-2 sentence summary describing what can be determined and why classification is difficult.

### 10. Keywords
Generate 2-5 keywords capturing any identifiable elements or characteristics.

## CONFIDENCE SCORING

High confidence (0.5-0.8):
- Clear barriers to classification identified
- Some elements discernible
- Reasonable type guess possible
- Note: High confidence in an "unclassifiable" image means high confidence that it IS unclassifiable

Medium confidence (0.3-0.5):
- Uncertain why it's difficult to classify
- Very few elements discernible
- Type guess highly uncertain

Low confidence (0.1-0.3):
- Completely ambiguous
- No elements clearly visible
- No reasonable type guess possible

Below 0.1:
- Essentially no useful information extractable


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Unclassifiable",

  "ocr_text": "Any readable text, even if fragmentary",

  "visual_description": {
    "overall_appearance": "General description of what's visible",
    "colors": "Predominant colors or color patterns",
    "shapes": "Visible shapes or geometric elements",
    "layout": "Spatial arrangement or composition",
    "recognizable_features": ["Feature 1", "Feature 2"]
  },

  "possible_type": {
    "best_guess": "photograph | diagram | chart | infographic | text_block | screenshot | abstract | decorative | corrupted | other",
    "confidence": 0.3,
    "supporting_clues": ["Clue 1", "Clue 2"],
    "contradicting_clues": ["Clue 1", "Clue 2"]
  },

  "visible_elements": [
    {
      "element_type": "text | shape | object | symbol | pattern",
      "description": "Description of element",
      "location": "Approximate location in image"
    }
  ],

  "classification_barriers": {
    "primary_barrier": "poor_quality | partial_view | corruption | abstract | ambiguous | complex | unusual",
    "quality_issues": ["Low resolution", "Blur", "Noise"],
    "completeness_issues": ["Truncated", "Partial", "Fragment"],
    "content_issues": ["Abstract", "Ambiguous", "Unusual"],
    "technical_issues": ["Corruption", "Encoding", "Rendering"]
  },

  "value_assessment": {
    "has_extractable_information": false,
    "likely_important": false,
    "likely_decorative": true,
    "should_flag_for_review": false,
    "notes": "Assessment notes"
  },

  "recommendations": {
    "request_higher_quality": false,
    "check_surrounding_context": true,
    "attempt_alternative_extraction": false,
    "flag_for_human_review": false,
    "skip_as_nonessential": true,
    "notes": "Specific recommendations"
  },

  "key_insights": [
    "First insight about most likely type or purpose",
    "Second insight about main classification barriers"
  ],

  "summary": "1-2 sentence summary describing what can be determined and why classification is difficult",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": ["Unclassifiable - insufficient information for standard categorization"]
  }
}
```

**IMPORTANT**:
- This category is a last resort for truly ambiguous images
- Make best-effort extraction of any visible information
- Clearly document why classification is not possible
- Provide actionable recommendations for resolution
- Flag for review if potentially important but unclear
- Be honest about low confidence
