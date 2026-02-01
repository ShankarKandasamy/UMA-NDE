Extract state and condition information from this documentary photograph.

## EXTRACT

1. **OCR Text**: Extract all readable text including reference IDs, timestamps, tags, labels, inspector names, checklist items, status indicators, measurements, and any other visible text
2. **What is documented**: Subject and its state at this moment
3. **Condition observed**: Current condition or state
4. **Temporal markers**: Any indicators of when this was captured
5. **Notable observations**: Significant details worth recording
6. **Context**: Why this state is being documented
7. **Checklist status**: Note if tasks are completed (checked boxes) or other status indicators

## GUIDELINES

- Record the state of the items shown accurately
- Note if tasks are completed (checked boxes) or the presence of tags
- Capture the general stage of progress
- Extract any timestamps or tags visible
- Identify the documentation purpose (inspection, inventory, progress tracking, etc.)

DOCUMENTATION_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Documentation",

"ocr_text": "All readable text extracted from the photograph including reference IDs, timestamps, tags, labels, inspector names, checklist items, and status indicators",

"documentation_purpose": "inspection | inventory | progress | record | baseline | handover | compliance | checklist | other",
"description": "What is being documented and why",

"subject": {
"what_is_documented": "Subject of documentation",
"subject_description": "Detailed description"
},

"state_recorded": {
"condition": "Observed condition",
"status": "Operational status if relevant",
"notable_observations": ["Significant details"],
"measurements": ["Any visible measurements or readings"],
"checklist_status": ["Checklist items and their status (e.g., 'Safety Check: Pass')"]
},

"temporal_context": {
"timestamp": "Date/time if visible",
"phase": "Project phase or stage if relevant (e.g., 'Construction Phase 1 Complete')",
"sequence": "Part of a documentation sequence"
},

"documentation_metadata": {
"reference_id": "Document or photo reference",
"inspector": "Inspector or documenter if shown",
"location": "Location identifier",
"tags": "Any visible tags or identifiers"
},

"key_insights": ["Key documented finding 1", "Key documented finding 2", "Key documented finding 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing the documented state",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
