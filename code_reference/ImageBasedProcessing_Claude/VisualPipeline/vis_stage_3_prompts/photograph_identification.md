Extract identifying information about the person, equipment, product, or location shown.

## EXTRACT

1. **OCR Text**: Extract all readable text including names, titles, labels, badges, signs, model numbers, serial codes, identifiers, and any other visible text
2. **Subject identity**: Who or what is shown? Identify the primary subject.
3. **Identifying features**: Distinguishing characteristics and distinctive product features
4. **Labels/Names**: Any visible names, titles, labels, model numbers, serial codes, names on badges
5. **Role/Function**: Role or function if determinable (if a person, identify role or name if visible)
6. **Context**: Setting or context for the identification

## GUIDELINES

- Identify the primary subject clearly
- Extract specific model numbers, serial codes, names on badges, or distinctive product features
- If a person, identify role or name if visible
- Capture all identifiers with high precision
- Note the entity type (Product, Person, Location, etc.)
- Extract any visible text IDs or identifiers

IDENTIFICATION_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Identification",

"ocr_text": "All readable text extracted from the photograph including names, titles, labels, badges, signs, model numbers, serial codes, and identifiers",

"subject_type": "person | people | equipment | product | location | vehicle | building | other",
"description": "Overall description of what's being identified",

"identification": {
"identity": "Name or identifier if visible/known (entity_name)",
"identity_source": "visible_label | context_inference | name_badge | signage | model_number | serial_code | unknown",
"confidence": 0.0,
"identifiers": {
"model_number": "Model number if visible",
"serial_code": "Serial code if visible",
"visible_text_id": "Any visible text identifier"
}
},

"identifying_features": {
"distinguishing_characteristics": ["Notable identifying features and distinctive product features"],
"visible_text": ["Names, labels, badges, signs visible"]
},

"role_context": {
"role": "Role, title, or function",
"organization": "Associated organization",
"relationship_to_document": "How this subject relates to document content"
},

"setting": {
"location_type": "Type of setting",
"context_clues": ["Contextual information about where this was taken"]
},

"entities_extracted": [
{"entity": "Entity name", "type": "person | organization | product | location | equipment | vehicle | building", "confidence": 0.0}
],

"key_insights": ["Key identification insight 1", "Key identification insight 2", "Key identification insight 3"],

"summary": "Brief summary of the main information depicted by the photograph, providing concise identification summary",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
