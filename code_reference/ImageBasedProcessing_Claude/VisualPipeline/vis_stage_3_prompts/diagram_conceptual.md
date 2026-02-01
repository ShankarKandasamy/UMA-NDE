# Diagram: Conceptual

You are extracting structured intelligence from a CONCEPTUAL DIAGRAM — a visual representation of how ideas, concepts, or entities relate to each other.

## WHAT YOU'RE LOOKING FOR

Conceptual diagrams show KNOWLEDGE STRUCTURE. Regardless of specific format (circles, boxes, trees, overlapping regions, mind maps, Venn diagrams, ER diagrams, concept maps, theoretical frameworks), extract:

### 1. CONCEPTS/ENTITIES
Every distinct idea, term, or named element:
- Extract the exact text/label
- Note visual emphasis (size, color, position, formatting)
- Identify which concepts appear central vs. peripheral
- For ER diagrams: map entities as nodes, attributes/keys as node properties

### 2. RELATIONSHIPS
How concepts connect to each other:
- Direct connections (lines, arrows, containment)
- Relationship labels if present (e.g., "causes", "is a type of", "includes", "implements", "is_related_to", "extends", "has_a", "connects_to")
- Relationship direction (A→B, A↔B, or undirected)
- Relationship type: hierarchical (parent/child), associative (related), overlapping (shared membership), causal (leads to)
- Standard vocabulary: IS_A, HAS_PART, IS_RELATED_TO, CONTAINS, IMPLEMENTS, EXTENDS, HAS_A, LINKS_TO

### 3. GROUPINGS/SETS
How concepts cluster together:
- Explicit groupings (bounded regions, color coding, spatial clustering)
- Overlapping memberships (concepts belonging to multiple groups)
- Group labels if present
- Venn diagram intersections

### 4. STRUCTURE ANALYSIS
- Is there a clear root/central concept?
- How deep is the hierarchy (if hierarchical)?
- Are there isolated concepts with no connections?
- What's the overall topology: tree, network, nested sets, hub-and-spoke?

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All node labels
- All relationship labels
- All group labels
- All annotations and notes
- Any legend or key text

### 2. Node Extraction
For each concept/entity:
- Assign unique `node_id`
- Extract label text exactly as shown
- Note shape type (rectangle, circle, diamond, ellipse, etc.)
- Record color if significant
- Note group membership if part of a bounded region
- Record position (approximate x, y or location description)

### 3. Relationship Extraction
For each connection:
- Identify source concept (`from_node_id`)
- Identify target concept (`to_node_id`)
- Extract relationship direction: unidirectional, bidirectional, none
- Extract relationship label if present
- Determine relationship type: IS_A, HAS_PART, IS_RELATED_TO, CONTAINS, IMPLEMENTS, EXTENDS, HAS_A, LINKS_TO, or custom
- Note connection style (arrow, line, dashed, connector)
- Assign confidence score (0.0-1.0)

### 4. Hierarchy Extraction
For hierarchical structures:
- Identify parent-child relationships
- Note hierarchy depth
- Assign confidence scores

### 5. Grouping Extraction
For bounded regions or clusters:
- Assign unique `group_id`
- Extract group label if present
- List `node_ids` belonging to this group
- Note overlapping memberships
- Assign confidence score

### 6. Key Insights
Extract 3-5 key insights about the conceptual structure:
- What is the main concept or theme?
- What are the most important relationships?
- What patterns or structures are evident?
- What does this diagram primarily communicate?

### 7. Summary
Provide a concise 2-4 sentence summary that captures:
- The core purpose of the diagram
- The main concepts represented
- The primary relationships or structure
- The theoretical framework or conceptual linkage

### 8. Keywords
Generate a list of 3-8 keywords that capture the core ideas of the diagram.

## EXTRACTION APPROACH

- Start from the most visually prominent element (usually the central concept)
- Work outward, capturing all connected concepts
- Note ALL text exactly as shown
- Capture relationship labels verbatim
- Identify grouping boundaries even if unlabeled
- For overlapping regions, explicitly note which concepts appear in intersections

## CONFIDENCE SCORING

Rate confidence based on:
- Text readability (clear labels = high confidence)
- Relationship clarity (explicit arrows/labels = high; implied by proximity = lower)
- Grouping boundaries (explicit borders = high; color-only = medium; spatial-only = lower)

High confidence (0.8-1.0):
- Clear, readable text
- Explicit connections with labels
- Well-defined boundaries

Medium confidence (0.5-0.8):
- Readable text but ambiguous connections
- Implied relationships
- Color-based grouping

Low confidence (0.3-0.5):
- Unclear text or connections
- Spatial-only grouping
- Complex overlapping structures

Below 0.3:
- Focus on concept inventory and general structure description only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Conceptual Diagram",

  "ocr_text": "All readable text extracted from the diagram including node labels, relationship labels, group labels, annotations, and legend text",

  "nodes": [
    {
      "node_id": "unique_identifier",
      "label": "Exact text label",
      "shape": "rectangle | circle | diamond | ellipse | other",
      "color": "Color if significant",
      "group_id": "Group identifier if part of a group",
      "position": "Approximate x,y or location description",
      "emphasis": "central | peripheral | normal",
      "confidence": 0.0
    }
  ],

  "relationships": [
    {
      "from_node_id": "source_node_id",
      "to_node_id": "target_node_id",
      "relationship_label": "Label text if present",
      "relationship_type": "IS_A | HAS_PART | IS_RELATED_TO | CONTAINS | IMPLEMENTS | EXTENDS | HAS_A | LINKS_TO | hierarchical | associative | causal | overlapping | custom",
      "direction": "unidirectional | bidirectional | none",
      "connection_style": "arrow | line | dashed | connector | other",
      "confidence": 0.0
    }
  ],

  "hierarchies": [
    {
      "parent_node_id": "parent_id",
      "child_node_ids": ["child_1_id", "child_2_id"],
      "hierarchy_level": 1,
      "confidence": 0.0
    }
  ],

  "groups": [
    {
      "group_id": "unique_group_identifier",
      "group_label": "Group label if present",
      "node_ids": ["node_1_id", "node_2_id"],
      "boundary_type": "explicit | color | spatial | overlapping",
      "confidence": 0.0
    }
  ],

  "structure_analysis": {
    "has_root_concept": true,
    "root_concept_id": "central_node_id",
    "hierarchy_depth": 3,
    "topology": "tree | network | nested_sets | hub_and_spoke | other",
    "isolated_concepts": ["node_ids_with_no_connections"]
  },

  "key_insights": [
    "First key insight about the conceptual structure",
    "Second key insight",
    "Third key insight"
  ],

  "summary": "Concise 2-4 sentence summary capturing the core purpose, main concepts, primary relationships or structure, and theoretical framework or conceptual linkage",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Preserve all text exactly as shown
- Every visible concept must be captured
- Every visible connection must be captured
- If overall confidence < 0.3: focus on concept inventory and general structure description only
