# Diagram: Technical

You are extracting structured intelligence from a TECHNICAL DIAGRAM — a precise visual representation of a system, its components, and their interconnections (examples: circuit diagram, blueprint, schematic, wiring diagram, CAD drawing, engineering schematic, P&ID, electrical diagram, mechanical drawing).

## WHAT YOU'RE LOOKING FOR

Technical diagrams document SYSTEM SPECIFICATIONS. Regardless of domain (electrical, mechanical, architectural, software, process engineering), extract:

### 1. COMPONENTS
Every discrete element in the system:
- Identifier/reference designator (e.g., "R1", "Pump-101", "Room A", "IC1")
- Component type/name if labeled (resistor, valve, motor, sensor, etc.)
- Note shape if it's a standard technical symbol
- Specifications/values (ratings, dimensions, materials, capacitance, voltage)
- **DO NOT** guess component types from symbols alone — only report what is explicitly labeled

### 2. CONNECTIONS
How components link together:
- What connects to what (source → target)
- Connection type if indicated (power, signal, structural, flow, data)
- Any labels on connections (wire numbers, signal names)
- Line style (solid, dashed, color-coded)
- Directionality (unidirectional, bidirectional, none)

### 3. SPECIFICATIONS & VALUES
All technical data:
- Numerical values with units
- Ratings and tolerances
- Dimensions and measurements
- Material callouts
- Part numbers

### 4. ANNOTATIONS
Every piece of text:
- Title block information (drawing number, revision, date, author)
- Notes and callouts
- Reference designators
- Standards references
- Legends and symbol keys

### 5. SYSTEM BOUNDARIES
- Input points (where signals/flow/material enters)
- Output points (where it exits)
- Interfaces to external systems

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All component identifiers and labels
- All connection labels and wire numbers
- All specifications and values
- All annotations and notes
- Title block information
- Legend and symbol key text
- Part numbers and reference designators
- Standards references

### 2. Component Extraction
For each discrete element:
- Assign unique `component_id`
- Extract identifier/reference designator exactly as shown
- Note component type if labeled
- Extract shape if standard technical symbol
- Extract all specifications/values (ratings, dimensions, materials)
- Record position (approximate x, y or location description)
- Assign confidence score (0.0-1.0)

### 3. Symbol Identification
Note the function of standardized symbols within the `type` field:
- Resistor, Capacitor, Inductor
- AND Gate, OR Gate, NOT Gate
- Power Source, Ground
- Valve, Pump, Motor, Sensor
- Switch, Relay, Fuse
- etc.

**CRITICAL RULE**: Only identify symbols if explicitly labeled or if confidence is very high based on standard conventions. Do NOT guess.

### 4. Connection Extraction
For each connection/wire:
- Identify source component (`from_component_id`)
- Identify target component (`to_component_id`)
- Extract connection label if present (wire number, signal name)
- Note connection type: power | signal | structural | flow | data | other
- Note direction: unidirectional | bidirectional | none
- Note connection style: solid | dashed | dotted | color_coded | other
- Assign confidence score (0.0-1.0)

### 5. Technical Features Extraction
For specialized technical elements:
- Identify feature type (resistor, capacitor, valve, joint, CAD_shape, architectural_symbol, etc.)
- Extract label if present
- Extract numeric value if shown (resistance, capacitance, voltage, pressure, temperature, etc.)
- Extract unit if shown (Ω, F, V, PSI, °C, etc.)
- Set `approximate: true` when estimated
- Assign confidence score

### 6. System Boundaries
Identify:
- Input points (where signals/flow/material enters)
- Output points (where it exits)
- Interfaces to external systems
- Connection points to other diagrams or systems

### 7. Signal/Flow Path Analysis
Describe:
- The signal flow or power delivery path
- Main pathways through the system
- Critical paths or loops
- Feedback mechanisms if present

### 8. Key Insights
Extract 3-5 key insights about the technical system:
- What is the primary function of this system?
- What are the critical components?
- What are the main signal/power/flow paths?
- What safety or operational features are evident?

### 9. Summary
Provide a concise 2-4 sentence summary that captures:
- The type of technical diagram
- The system being represented
- The primary components and connections
- The main function or purpose

### 10. Keywords
Generate a list of 3-8 keywords that capture the core technical elements of the diagram.

## EXTRACTION APPROACH

- Extract ALL visible text — this is critical for technical diagrams
- Capture component identifiers exactly as shown
- Link connections by the component identifiers at each end
- Note specifications in their original format with units
- If a symbol is unrecognized, mark it as such — do not guess

## CRITICAL RULE

For symbols you cannot confidently identify:
- Still capture its position and connections
- Mark `component_type` as "unidentified"
- Note any visible labels or values associated with it
- **DO NOT** invent component types based on symbol shape

## CONFIDENCE SCORING

Rate confidence based on:
- Text/label clarity
- Connection path clarity (explicit lines vs. implied)
- Completeness of specifications

High confidence (0.8-1.0):
- Clear, readable labels
- Explicit connections with labels
- Complete specifications

Medium confidence (0.5-0.8):
- Readable labels but some ambiguity
- Implied connections
- Partial specifications

Low confidence (0.3-0.5):
- Unclear labels or connections
- Missing critical information
- Complex overlapping elements

Below 0.3:
- Focus on text inventory only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Technical Diagram",

  "ocr_text": "All readable text extracted from the diagram including component identifiers, connection labels, specifications, annotations, title block information, legend text, part numbers, and standards references",

  "diagram_domain": "electrical | mechanical | architectural | software | process_engineering | other",
  "description": "Overall description of what the diagram represents",

  "components": [
    {
      "component_id": "unique_identifier",
      "reference_designator": "R1 | Pump-101 | IC1 | etc.",
      "component_type": "resistor | capacitor | valve | pump | motor | sensor | switch | gate | unidentified | other",
      "label": "Component label or name",
      "symbol_shape": "Standard symbol shape if applicable",
      "specifications": {
        "value": "Numeric value",
        "unit": "Unit of measurement",
        "rating": "Rating if applicable",
        "tolerance": "Tolerance if applicable",
        "dimension": "Dimension if applicable",
        "material": "Material if applicable",
        "part_number": "Part number if visible"
      },
      "position": "Approximate x,y or location description",
      "confidence": 0.0
    }
  ],

  "connections": [
    {
      "from_component_id": "source_component_id",
      "to_component_id": "target_component_id",
      "connection_label": "Wire number, signal name, or label",
      "connection_type": "power | signal | structural | flow | data | other",
      "direction": "unidirectional | bidirectional | none",
      "connection_style": "solid | dashed | dotted | color_coded | other",
      "confidence": 0.0
    }
  ],

  "system_boundaries": {
    "input_points": [
      {
        "label": "Input label",
        "type": "signal | power | flow | material | other"
      }
    ],
    "output_points": [
      {
        "label": "Output label",
        "type": "signal | power | flow | material | other"
      }
    ],
    "external_interfaces": ["Interface descriptions"]
  },

  "technical_features": [
    {
      "feature_type": "resistor | capacitor | valve | joint | CAD_shape | architectural_symbol | other",
      "label": "Feature label",
      "value": "Numeric value",
      "unit": "Unit",
      "approximate": false,
      "confidence": 0.0
    }
  ],

  "annotations": {
    "title_block": {
      "drawing_number": "Drawing number if present",
      "revision": "Revision if present",
      "date": "Date if present",
      "author": "Author if present"
    },
    "notes": ["Note 1", "Note 2"],
    "standards_references": ["Standard references"],
    "legend": ["Legend entries"]
  },

  "signal_flow_analysis": {
    "main_paths": ["Description of main signal/power/flow paths"],
    "critical_paths": ["Critical paths or loops"],
    "feedback_mechanisms": ["Feedback mechanisms if present"]
  },

  "key_insights": [
    "First key insight about the technical system",
    "Second key insight",
    "Third key insight"
  ],

  "summary": "Concise 2-4 sentence summary capturing the type of technical diagram, the system being represented, primary components and connections, and main function or purpose",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Preserve ALL text exactly as shown (including part numbers, abbreviations)
- Every visible component must be captured
- Every visible connection must be captured
- If overall confidence < 0.3: focus on text inventory only
- DO NOT guess component types from symbols alone
