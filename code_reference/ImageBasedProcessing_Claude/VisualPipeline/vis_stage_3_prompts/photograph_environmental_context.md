Extract contextual information about the environment or surroundings shown.

## EXTRACT

1. **OCR Text**: Extract all readable text including location names, environmental labels, signs, warnings, measurement readings, and any other visible text
2. **Environment type**: What kind of setting is this?
3. **Notable features**: Key environmental features visible
4. **Environmental conditions**: Lighting, weather, spatial constraints, or other conditions
5. **Relevance**: Why is this environment significant to the document?

## GUIDELINES

- Describe the physical environment and setting accurately
- Note lighting, weather, or spatial constraints that provide context to the main subject
- Identify the type of setting (factory floor, outdoor desert, laboratory, etc.)
- Extract any environmental conditions that are significant
- Explain how the environment relates to the main subject

ENVIRONMENTAL_CONTEXT_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Environmental Context",

"ocr_text": "All readable text extracted from the photograph including location names, environmental labels, signs, warnings, and measurement readings",

"environment_type": "indoor | outdoor | industrial | laboratory | office | field | clinical | construction | natural | factory_floor | desert | other",
"description": "Description of the environment shown",

"setting_details": {
"location_type": "Type of location",
"notable_features": ["Key environmental features"],
"conditions": "Environmental conditions visible",
"environmental_conditions": ["Specific conditions like 'Low light', 'Dusty', 'High humidity', etc."],
"spatial_constraints": "Any visible spatial constraints or limitations"
},

"contextual_relevance": {
"why_significant": "Why this environment matters to the document",
"relationship_to_subject": "How environment relates to main subject",
"context_clues": "Context clues that help understand the setting"
},

"key_insights": ["Key environmental insight 1", "Key environmental insight 2", "Key environmental insight 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing the environmental context",

"meta": {
"extraction_confidence": 0.0,
"information_value": "high | medium | low"
}
}
