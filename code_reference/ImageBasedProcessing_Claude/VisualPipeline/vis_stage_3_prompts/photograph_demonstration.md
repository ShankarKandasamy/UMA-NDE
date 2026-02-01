Extract procedural information from this photograph showing how to perform an action.

## EXTRACT

1. **OCR Text**: Extract all readable text including step numbers, action names, labels, tool names, safety warnings, annotations, and any other visible text
2. **Action shown**: What action or step is being demonstrated?
3. **Technique/Method**: How is it being done?
4. **Tools/Materials**: What tools or materials are being used?
5. **Hand/Body position**: Positioning relevant to the technique
6. **Sequence context**: What step is this in a larger process?
7. **Safety considerations**: Any visible safety equipment or warnings

## GUIDELINES

- Identify the specific action or procedure being performed
- List the tools/hands involved and the precise state of the operation (e.g., 'tightening', 'inserting')
- Note any visible safety compliance or warnings
- Capture sequence indicators (step numbers, before/after context)
- Describe positioning and technique details clearly

DEMONSTRATION_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Demonstration",

"ocr_text": "All readable text extracted from the photograph including step numbers, action names, labels, tool names, safety warnings, and annotations",

"action_demonstrated": "What action is being shown",
"description": "Full description of the demonstration",

"technique": {
"method": "How the action is being performed",
"key_points": ["Important technique details"],
"positioning": "Relevant hand, body, or tool positioning"
},

"tools_materials": {
"tools_used": [{"tool": "Tool name", "purpose": "How it's being used"}],
"materials": ["Materials involved"]
},

"sequence_context": {
"step_number": "Step X of Y if determinable",
"step_name": "Name of this step",
"preceding_action": "What comes before",
"following_action": "What comes after"
},

"safety_notes": ["Any visible safety considerations or compliance indicators"],

"key_insights": ["Key procedural insight 1 about the demonstration", "Key procedural insight 2", "Key procedural insight 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing what procedure or step is demonstrated",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
