Extract information about the equipment, machine, or asset shown in this photograph.

## EXTRACT

1. **OCR Text**: Extract all readable text including equipment names, model numbers, serial numbers, manufacturer names, data plate information, warning labels, specifications, ratings, capacities, instruction labels, certification marks, and any other visible text
2. **Equipment identification**: Type, make, model, name
3. **Components visible**: Major parts, subassemblies, features, connection points
4. **Specifications**: Any visible specs, ratings, capacities
5. **Configuration**: Current setup, settings, or state (e.g., 'Panels removed for maintenance', 'connected', 'open')
6. **Labels/Plates**: Data plates, serial numbers, warning labels, asset tags
7. **Connections**: Inputs, outputs, interfaces visible
8. **Condition**: Observable condition of the equipment

## GUIDELINES

- Identify the machine or device clearly
- List the visible major components and connection points
- Capture model numbers and serial numbers exactly as they appear
- Identify all visible components
- Note any visible specifications or ratings
- Describe the current configuration or state
- Note the current operational configuration

EQUIPMENT_ASSET_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Equipment / Asset Visualization",

"ocr_text": "All readable text extracted from the photograph including equipment names, model numbers, serial numbers, manufacturer names, data plate information, warning labels, specifications, ratings, and certification marks",

"equipment_type": "machine | instrument | tool | vehicle | device | component | assembly | system | other",
"description": "Overall description of what's shown",

"identification": {
"equipment_name": "Name or type (asset_name)",
"manufacturer": "Make/manufacturer if visible",
"model": "Model number",
"serial_number": "Serial number if visible",
"asset_tag": "Asset ID or tag if visible",
"confidence": 0.0
},

"components_visible": [
{
"component_name": "Component name",
"location": "Where on the equipment",
"description": "Description of the component",
"specifications": "Any specs visible for this component"
}
],

"specifications_visible": {
"ratings": [
{"parameter": "Power/voltage/capacity/etc.", "value": "Value with units"}
],
"dimensions": "Size if determinable",
"capacity": "Capacity or throughput if shown",
"data_plate_info": "Full data plate text if visible"
},

"configuration": {
"current_state": "on | off | standby | operating | maintenance | other",
"settings_visible": ["Any visible settings or configurations"],
"mode": "Operating mode if indicated",
"operational_config": "Current operational configuration (e.g., 'Panels removed for maintenance', 'connected', 'open')"
},

"connections": {
"inputs": ["Input connections visible"],
"outputs": ["Output connections visible"],
"interfaces": ["Control interfaces, ports, or panels"],
"connection_points": ["Major connection points visible"]
},

"labels_warnings": {
"warning_labels": ["Warning or caution labels visible"],
"instruction_labels": ["Operating instructions visible"],
"certification_marks": ["Certification or compliance marks"]
},

"condition_observed": {
"overall_condition": "new | good | fair | worn | damaged",
"observations": ["Specific condition observations"]
},

"key_insights": ["Key equipment detail 1", "Key equipment detail 2", "Key equipment detail 3"],

"summary": "Brief summary of the main information depicted by the photograph, identifying equipment and key specifications",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
