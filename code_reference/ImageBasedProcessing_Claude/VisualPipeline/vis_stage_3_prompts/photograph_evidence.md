Extract evidential information from this photograph serving as proof or raw data.

## EXTRACT

1. **OCR Text**: Extract all readable text including measurements, readings, values, scales, markers, timestamps, labels, identifiers, case numbers, units, calibration indicators, and any other visible text
2. **What is being evidenced**: What claim, measurement, or finding does this support?
3. **Observable data**: All visible measurements, readings, values, scales, markers (e.g., 'Thermometer reads 45C', 'Scale reads 10g')
4. **Subject details**: What specifically is shown as evidence
5. **Measurement context**: Units, scales, reference points, calibration indicators
6. **Conditions**: Environmental or experimental conditions visible
7. **Metadata**: Timestamps, labels, identifiers, case numbers visible
8. **Chain of evidence**: Any indicators of authenticity, source, or documentation trail

## GUIDELINES

- This image IS the data — extract everything observable
- Analyze this image as objective evidence
- Identify the subject being measured or recorded
- Extract any visible readings, values, or specific physical attributes that constitute proof
- Capture exact values and readings
- Note measurement units and scales
- Preserve any visible identifiers exactly
- Document any evidential conclusions supported by the image

## JSON SCHEMA

```json
{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Evidence",

"ocr_text": "All readable text extracted from the photograph including measurements, readings, values, scales, markers, timestamps, labels, identifiers, case numbers, and units",

"evidence_type": "scientific | legal | medical | inspection | measurement | experimental | forensic | other",
"description": "What this photograph documents as evidence",

"what_is_evidenced": {
"claim_supported": "The claim or finding this evidence supports",
"subject_of_evidence": "What specifically is being shown",
"evidence_significance": "Why this is significant",
"evidential_conclusion": "Conclusion supported by the evidence (e.g., 'Confirming presence of bacteria')"
},

"observable_data": {
"measurements": [
{
"parameter": "What is measured",
"value": "Numeric value",
"unit": "Unit of measurement",
"source": "Instrument or scale visible",
"confidence": 0.0
}
],
"readings": [
{"instrument": "Device name", "reading": "Value shown (e.g., 'Thermometer reads 45C', 'Scale reads 10g')", "timestamp": "If visible"}
],
"scale_references": ["Reference objects or scales visible for size context"],
"markers_labels": ["Any markers, labels, or identifiers visible"]
},

"subject_details": {
"primary_subject": "Main subject of the evidence",
"subject_description": "Detailed description",
"observable_features": ["Specific features relevant to evidence"],
"condition_observed": "State or condition documented",
"physical_attributes": ["Specific physical attributes that constitute proof"]
},

"documentation_metadata": {
"timestamp": "Date/time if visible",
"case_reference": "Case number, ID, or reference",
"source_indicator": "Lab, facility, or source if shown",
"chain_of_custody": "Any authenticity indicators"
},

"environmental_conditions": {
"visible_conditions": ["Lighting, temperature display, environmental factors"],
"controlled_environment": true
},

"key_insights": ["Key evidential finding 1", "Key evidential finding 2", "Key evidential finding 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing what this evidence shows",

"meta": {
"extraction_confidence": 0.0,
"data_quality": "high | medium | low",
"warnings": []
}
}
