Extract information about the defect, damage, or anomaly shown in this photograph.

## EXTRACT

1. **OCR Text**: Extract all readable text including labels, markers, measurements, photo identifiers, timestamps, inspection markers, and any other visible text
2. **Anomaly identification**: What defect, damage, or abnormality is shown?
3. **Location**: Where on the subject is the anomaly located?
4. **Characteristics**: Size, shape, color, pattern, texture (e.g., 'corroded', 'cracked'), severity of the anomaly
5. **Extent**: How widespread is the damage/defect?
6. **Probable cause**: Any visible indicators of what caused this?
7. **Reference context**: Scale references, surrounding condition for comparison
8. **Classification**: Type and severity assessment

## GUIDELINES

- Be precise about location (use clock positions, quadrants, or measurements)
- Describe anomaly characteristics in detail
- Note any visible progression or patterns
- Capture any visible identifiers or markers

CONDITION*ANOMALY_SCHEMA = """{
"figure_id": "page*{page*num}\_figure*{index}",
"subcategory": "Condition / Anomaly Evidence",

"ocr_text": "All readable text extracted from the photograph including labels, markers, measurements, photo identifiers, timestamps, and inspection markers",

"anomaly_type": "crack | corrosion | wear | deformation | discoloration | contamination | missing_part | leak | burn | impact | biological | other",
"description": "Overall description of what's documented",

"anomaly_details": {
"identification": "What the anomaly/defect is",
"location_on_subject": {
"description": "Where on the subject (e.g., 'lower left quadrant', '3 o'clock position')",
"component": "Specific component or area affected",
"coordinates": "Measurements or grid reference if visible"
},
"characteristics": {
"size": "Dimensions if determinable",
"shape": "Shape description",
"color": "Color or discoloration",
"pattern": "Pattern (linear, branching, circular, etc.)",
"texture": "Surface texture observations"
},
"extent": {
"coverage": "How much area affected",
"depth": "Surface or penetrating",
"progression": "Signs of spreading or progression"
}
},

"severity_assessment": {
"severity": "critical | major | moderate | minor | cosmetic",
"functional_impact": "Impact on function if determinable",
"safety_concern": true
},

"probable_cause": {
"visible_indicators": ["Indicators of what caused this"],
"cause_hypothesis": "Likely cause based on visual evidence",
"confidence": 0.0
},

"reference_context": {
"scale_reference": "Size reference visible",
"surrounding_condition": "Condition of surrounding area",
"comparison_baseline": "What normal should look like if shown"
},

"documentation_details": {
"markers_visible": ["Any inspection markers or labels"],
"photo_identifiers": "Photo ID, timestamp, or reference numbers"
},

"key_insights": ["Key finding 1 about the defect, damage, or anomaly", "Key finding 2", "Key finding 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing the anomaly and its significance",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
