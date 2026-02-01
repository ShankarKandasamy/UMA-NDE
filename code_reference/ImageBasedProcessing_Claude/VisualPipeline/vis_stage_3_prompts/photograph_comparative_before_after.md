Extract comparison information from this before/after or comparative, old/new, or two different conditions in a photograph.

## EXTRACT

1. **OCR Text**: Extract all readable text including labels, timestamps, condition markers, annotations, measurements, and any other visible text
2. **States shown**: What two (or more) states are being compared?
3. **What changed**: Specific differences between states
4. **Timeframe**: Time between states if indicated
5. **Baseline state**: Description of the "before" or reference state
6. **Changed state**: Description of the "after" or modified state
7. **Quantifiable differences**: Any measurable changes
8. **Cause of change**: What intervention or process caused the change

## EXTRACTION APPROACH

1. Identify the subject being compared
2. Determine the comparison structure:
   - Side-by-side split (left/right or top/bottom)
   - Overlaid comparison
   - Separate images in same frame
3. Label each state:
   - Before/After
   - Old/New
   - Condition A/Condition B
4. Extract differences:
   - Visual changes
   - State changes
   - Improvements or deterioration
5. Look for labels, timestamps, or indicators of which is which
6. Quantify the change if possible (measurements, extent)

## CONFIDENCE SCORING GUIDELINES

High confidence (0.8-1.0):

- Clear comparative structure
- Both states clearly visible
- Differences are obvious
- Before/after labels present

Medium confidence (0.5-0.8):

- Comparative intent clear but structure ambiguous
- Some differences require interpretation
- Before/after order requires inference

Low confidence (0.3-0.5):

- Unclear if image is comparative
- Difficult to identify differences
- Ambiguous which state is which

Below 0.3:

- Describe visible content only

## GUIDELINES

- Clearly distinguish which is before/after or control/test
- Clearly identify the layout (side-by-side, top-bottom, overlaid)
- Be specific about what changed vs. what remained the same
- Capture any timeline indicators
- Note the significance of the changes
- Look for visual indicators like arrows connecting corresponding features
- Describe differences systematically (appearance, condition, configuration)
- Note the type of change (improvement, deterioration, transformation, repair)

COMPARATIVE*SCHEMA = """{
"figure_id": "page*{page*num}\_figure*{index}",
"subcategory": "Comparative / Before-After",

"ocr_text": "All readable text extracted from the photograph including labels, timestamps, condition markers, annotations, and measurements",

"comparison_type": "before_after | side_by_side | time_series | control_test | version_comparison | other",
"description": "What is being compared",

"states_compared": [
{
"state_id": "state_0",
"label": "Before | After | Control | Test | Version X | Time 1",
"timestamp": "When this state was captured if known",
"description": "Detailed description of this state",
"key_characteristics": ["Observable characteristics"]
},
{
"state_id": "state_1",
"label": "Label for second state",
"timestamp": "Timestamp if known",
"description": "Description of second state",
"key_characteristics": ["Observable characteristics"]
}
],

"changes_identified": [
{
"change_description": "What specifically changed",
"location": "Where the change is visible",
"magnitude": "How significant the change is",
"direction": "increase | decrease | transformation | appearance | disappearance",
"quantified": "Measurement if possible"
}
],

"unchanged_elements": ["Elements that remained constant"],

"timeframe": {
"interval": "Time between states",
"start_date": "Start date if shown",
"end_date": "End date if shown"
},

"cause_of_change": {
"intervention": "What action or process caused the change",
"natural_process": "Natural process if applicable",
"confidence": 0.0
},

"outcome_assessment": {
"result": "positive | negative | neutral | mixed",
"significance": "Why this change matters",
"success_indicators": ["Indicators of success/failure if relevant"]
},

"key_insights": ["Key comparative finding 1 summarizing the change or difference", "Key comparative finding 2", "Key comparative finding 3"],

"summary": "Brief summary of the main information depicted by the photograph, focusing on what changed and why it matters",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
