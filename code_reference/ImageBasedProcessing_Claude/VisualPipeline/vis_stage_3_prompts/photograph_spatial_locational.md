Extract geographic or spatial positioning information from this photograph.

## EXTRACT

1. **OCR Text**: Extract all readable text including location names, landmarks, street signs, address markers, coordinates, map references, distance markers, and any other visible text
2. **Location identity**: What place or position is shown? Identify the location or spatial layout.
3. **Geographic indicators**: Landmarks, signs, coordinates, street signs
4. **Spatial relationships**: How elements are positioned relative to each other (e.g., 'North of the river', 'Building A is adjacent to the parking lot')
5. **Orientation**: Direction, viewpoint, perspective
6. **Scale indicators**: Reference for distances or sizes

## GUIDELINES

- Identify the location or spatial layout clearly
- Extract specific landmarks, street signs, or relative positioning of objects
- Note compass directions or relative orientation
- Capture any GPS or grid coordinates visible
- Describe spatial relationships accurately
- Extract any distance or dimension indicators

SPATIAL_LOCATIONAL_SCHEMA = """{
"figure_id": "page_{page_num}_figure_{index}",
"subcategory": "Spatial / Locational Reference",

"ocr_text": "All readable text extracted from the photograph including location names, landmarks, street signs, address markers, coordinates, and distance markers",

"location_type": "geographic | indoor | site | facility | room | position | route | boundary | other",
"description": "What location or spatial information is shown",

"location_identity": {
"place_name": "Name of location if identifiable (location_name)",
"location_type": "Type of location",
"address_indicators": "Any address or location markers visible"
},

"geographic_indicators": {
"landmarks": ["Visible landmarks"],
"signage": ["Location signs and street signs visible"],
"coordinates": "GPS or grid coordinates if shown",
"map_references": "Map references if visible"
},

"spatial_relationships": {
"perspective": "Viewpoint description (aerial, ground level, etc.)",
"orientation": "Compass direction or relative orientation",
"relative_positions": ["How elements are positioned relative to each other (e.g., 'North of the river', 'Building A is adjacent to the parking lot')"],
"boundaries": ["Boundaries or perimeters visible"],
"spatial_relationship": "Description of spatial relationship (e.g., 'Building A is adjacent to the parking lot')"
},

"scale_reference": {
"scale_indicators": ["Objects providing scale reference"],
"distances": ["Any distances shown or estimable"],
"dimensions": ["Area or dimension indicators"]
},

"key_insights": ["Key spatial/location insight 1", "Key spatial/location insight 2", "Key spatial/location insight 3"],

"summary": "Brief summary of the main information depicted by the photograph, describing location and spatial information",

"meta": {
"extraction_confidence": 0.0,
"warnings": []
}
}
