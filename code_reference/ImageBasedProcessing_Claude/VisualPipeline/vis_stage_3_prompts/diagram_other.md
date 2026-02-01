# Diagram: Other

You are extracting structured intelligence from a SPECIALIZED DIAGRAM that represents temporal, spatial, compositional, or domain-specific information (map, timeline, genealogy tree, floor plan, seating chart, pyramid, cycle diagram, or other specialized type).

## FIRST: IDENTIFY WHAT THE DIAGRAM REPRESENTS

Before extracting, determine the diagram's fundamental purpose:

- **Timeline** (temporal sequence)
- **Map** (geographic or spatial)
- **Floor plan** (architectural layout)
- **Seating chart** (spatial arrangement)
- **Genealogy tree** (family relationships)
- **Pyramid** (hierarchical composition)
- **Cycle diagram** (cyclical process)
- **Other specialized type**

## EXTRACTION OBJECTIVES BY TYPE

### TEMPORAL DIAGRAMS
Shows events/periods along a time axis:
- Look for: dates, time markers, chronological sequence, periods/eras
- Extract: events with dates, periods with ranges, temporal relationships
- Note: chronological order, temporal direction (left→right, top→bottom)
- Identify: milestones or emphasized events

### SPATIAL DIAGRAMS
Shows positions in physical or conceptual space:
- Look for: locations, regions, floor plans, seating arrangements, maps
- Extract: locations with positions, spatial relationships, areas/zones
- Note: labeled locations or rooms, regions or zones
- Identify: routes or paths, dimensions or scale if shown

### COMPOSITIONAL DIAGRAMS
Shows parts of a whole or cyclical processes:
- Look for: pyramids, pie-like segments, cyclical arrows, layers
- Extract: components with proportions, sequence in cycles, hierarchy in pyramids
- Note: the composition type (cycle, pyramid, layers)
- Identify: direction for cycles, proportion principle

### RELATIONAL DIAGRAMS
Shows specific relationship types (family, network):
- Look for: connecting lines between people/entities, generations, hierarchies
- Extract: entities with attributes, relationships with types
- Note: relationship types (parent, child, spouse, sibling)
- Identify: generational levels, attributes (dates, titles, descriptions)

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All event labels and dates
- All location names and labels
- All component/entity names
- All relationship labels
- All annotations and notes
- Any legend or key text
- Dimensions, scale, or measurements

### 2. Type Identification
Determine the diagram type and extract accordingly:
- **diagram_type**: temporal | spatial | compositional | relational | other
- **diagram_subtype**: timeline | map | floor_plan | seating_chart | genealogy | pyramid | cycle | other

### 3. Element Extraction
For all diagram types, extract:
- All nodes/elements with unique identifiers
- All labels exactly as shown
- All connections or relationships
- Spatial or temporal positioning information
- Any measurable values (dates, dimensions, proportions)

### 4. Type-Specific Extraction

**For TEMPORAL diagrams:**
- Extract all events with dates/times
- Note period ranges (start and end dates)
- Capture temporal direction
- Identify milestones

**For SPATIAL diagrams:**
- Extract all labeled locations/rooms
- Note regions or zones
- Capture routes or paths
- Extract dimensions or scale

**For COMPOSITIONAL diagrams:**
- Extract all components/stages in order
- Note proportions or sizes
- Capture the organizing principle
- Identify direction for cycles

**For RELATIONAL diagrams:**
- Extract all entities (people, nodes)
- Identify relationship types
- Note attributes (dates, titles)
- Capture generational or hierarchical levels

### 5. Key Insights
Extract 3-5 key insights about the structure or organization:
- What is the main purpose or theme?
- What are the most important elements or events?
- What patterns or structures are evident?
- What does this diagram primarily communicate?

### 6. Summary
Provide a concise 2-4 sentence summary that captures:
- The diagram type and purpose
- The main elements or events represented
- The primary organization or structure
- Key relationships or patterns

### 7. Keywords
Generate a list of 3-8 keywords that capture the core ideas of the diagram.

## EXTRACTION APPROACH

### For TEMPORAL diagrams:
- Identify the time scale (years, months, days, eras)
- Extract every event with its date/position
- Note periods/ranges with start and end
- Capture the temporal direction (left→right, top→bottom)
- Identify milestones or emphasized events

### For SPATIAL diagrams:
- Identify the space type (geographic, floor plan, seating, conceptual)
- Extract all labeled locations/positions
- Note regions or zones
- Capture any routes or paths
- Extract dimensions or scale if shown

### For COMPOSITIONAL diagrams:
- Identify the composition type (cycle, pyramid, layers)
- Extract all components/stages in order
- Note proportions or sizes if indicated
- Capture the principle (hierarchy, sequence, proportion)
- Identify direction for cycles

### For RELATIONAL diagrams:
- Extract all entities (people, nodes)
- Identify relationship types (parent-child, spouse, peer)
- Note any attributes (dates, titles, descriptions)
- Capture generational or hierarchical levels

## CONFIDENCE SCORING

Rate confidence based on:
- Label readability
- Date/value clarity
- Relationship path clarity
- Completeness of information

High confidence (0.8-1.0):
- Clear, readable text
- Explicit dates, labels, or positions
- Well-defined relationships or structure

Medium confidence (0.5-0.8):
- Readable text but some ambiguity
- Implied relationships or positions
- Partial information

Low confidence (0.3-0.5):
- Unclear text or positions
- Complex overlapping elements
- Missing critical information

Below 0.3:
- Focus on element inventory only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Other Diagram",

  "ocr_text": "All readable text extracted from the diagram including event labels, dates, location names, component names, relationship labels, annotations, dimensions, and legend text",

  "diagram_type": "temporal | spatial | compositional | relational | other",
  "diagram_subtype": "timeline | map | floor_plan | seating_chart | genealogy | pyramid | cycle | other",
  "description": "Overall description of what the diagram represents",

  "elements": [
    {
      "element_id": "unique_identifier",
      "label": "Exact text label",
      "element_type": "event | location | component | entity | other",
      "position": "Temporal, spatial, or hierarchical position",
      "attributes": {
        "date": "Date/time if applicable",
        "dimension": "Size/dimension if applicable",
        "proportion": "Proportion if applicable",
        "other_attributes": "Any other relevant attributes"
      },
      "confidence": 0.0
    }
  ],

  "relationships": [
    {
      "from_element_id": "source_element_id",
      "to_element_id": "target_element_id",
      "relationship_type": "parent | child | spouse | sibling | adjacent | contains | follows | precedes | connected_to | other",
      "relationship_label": "Label text if present",
      "confidence": 0.0
    }
  ],

  "temporal_info": {
    "time_scale": "years | months | days | eras | other",
    "temporal_direction": "left_to_right | right_to_left | top_to_bottom | bottom_to_top | other",
    "time_range": {
      "start": "earliest date/time",
      "end": "latest date/time"
    },
    "milestones": ["milestone_element_ids"]
  },

  "spatial_info": {
    "space_type": "geographic | floor_plan | seating | conceptual | other",
    "scale": "Scale information if shown",
    "dimensions": "Overall dimensions if shown",
    "regions": [
      {
        "region_id": "unique_region_id",
        "region_label": "Region name",
        "element_ids": ["elements_in_this_region"]
      }
    ],
    "routes": [
      {
        "route_id": "unique_route_id",
        "route_label": "Route name",
        "element_ids": ["elements_along_route"]
      }
    ]
  },

  "compositional_info": {
    "composition_type": "cycle | pyramid | layers | other",
    "direction": "clockwise | counterclockwise | bottom_to_top | top_to_bottom | other",
    "total_components": 0,
    "organizing_principle": "hierarchy | sequence | proportion | other"
  },

  "relational_info": {
    "relationship_types_present": ["parent_child", "spouse", "sibling", "other"],
    "generational_levels": 0,
    "total_entities": 0
  },

  "key_insights": [
    "First key insight about the structure or organization",
    "Second key insight",
    "Third key insight"
  ],

  "summary": "Concise 2-4 sentence summary capturing the diagram type and purpose, main elements or events, primary organization or structure, and key relationships or patterns",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Capture ALL text and values exactly as shown
- Structure output to match the diagram type identified
- If overall confidence < 0.3: focus on element inventory only
