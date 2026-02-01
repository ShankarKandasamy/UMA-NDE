# Diagram: Explanatory

You are extracting structured intelligence from an EXPLANATORY DIAGRAM — a visual representation of process flow, organizational structure, or decision logic.

## WHAT YOU'RE LOOKING FOR

Explanatory diagrams show HOW THINGS WORK OR ARE ORGANIZED. Regardless of specific format (flowchart, org chart, decision tree, workflow, BPMN diagram), extract:

### 1. NODES/ELEMENTS
Every discrete step, position, or state:
- Exact text/label content
- Element type based on SHAPE if conventional shapes are used:
  - Rectangles: typically process steps or positions
  - Diamonds: typically decision points
  - Ovals/stadiums: typically start/end points
  - Parallelograms: typically input/output
  - Other shapes: note the shape, infer purpose from context
- Role/lane assignment if diagram has swimlanes
- Sequential position if numbered

### 2. FLOW/CONNECTIONS
How elements connect:
- Source and target of each connection
- Direction of flow
- Labels on connections (especially decision outcomes: "Yes", "No", conditions)
- Connection type: sequential, conditional, exception, loop-back

### 3. DECISION LOGIC
For branching points:
- The question or condition being evaluated
- All possible outcomes/branches
- Labels on each branch
- Which branch is the default/main path

### 4. STRUCTURE/HIERARCHY
For organizational diagrams:
- Reporting relationships (who reports to whom)
- Hierarchical levels
- Span of control (number of direct reports)
- Dotted-line vs solid-line relationships

### 5. ROLES/SWIMLANES
If present:
- Lane labels (roles, departments, systems, phases)
- Which elements belong to which lane
- Handoff points between lanes

### 6. PATHS THROUGH THE DIAGRAM
- Main/happy path (most common flow)
- Exception paths
- Loops or cycles
- Parallel branches

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All node/element labels
- All connection/flow labels
- All decision branch labels
- All swimlane/role labels
- All annotations and notes
- Any legend or key text

### 2. Node/Element Extraction
For each discrete step, position, or state:
- Assign unique `node_id`
- Extract label text exactly as shown
- Identify element type: process, decision, start_end, input_output, other
- Note shape: rectangle, diamond, oval, parallelogram, other
- Record swimlane/role if applicable
- Record position (approximate x, y or location description)
- Note sequential number if present

### 3. Flow/Connection Extraction
For each connection:
- Identify source element (`from_node_id`)
- Identify target element (`to_node_id`)
- Extract flow direction: forward, backward, bidirectional
- Extract connection label if present (especially for decisions)
- Determine connection type: sequential, conditional, exception, loop_back
- Note connection style (solid, dashed, etc.)
- Assign confidence score (0.0-1.0)

### 4. Decision Point Extraction
For each decision node:
- Extract the decision question/condition
- List all possible outcomes/branches
- Extract label for each branch (e.g., "Yes", "No", "True", "False")
- Identify the default/main path if evident
- Assign confidence score

### 5. Hierarchy Extraction (for org charts)
For hierarchical structures:
- Identify reporting relationships
- Note hierarchical levels
- Count span of control
- Distinguish solid-line vs dotted-line relationships
- Assign confidence scores

### 6. Swimlane/Role Extraction
For diagrams with lanes:
- Assign unique `lane_id`
- Extract lane label
- List `node_ids` belonging to this lane
- Identify handoff points between lanes
- Assign confidence score

### 7. Path Analysis
Identify and describe:
- The main/happy path through the diagram
- Exception or error paths
- Any loops or cycles
- Parallel execution paths

### 8. Key Insights
Extract 3-5 key insights about the process or structure:
- What is the overall purpose of this process/organization?
- What are the critical decision points or steps?
- What patterns or structures are evident?
- What does this diagram primarily communicate?

### 9. Summary
Provide a concise 2-4 sentence summary that captures:
- The core purpose of the diagram
- The main steps or organizational structure
- The primary flow or hierarchy
- Key decision points or relationships

### 10. Keywords
Generate a list of 3-8 keywords that capture the core ideas of the diagram.

## EXTRACTION APPROACH

- Identify start point(s) first
- Trace all paths to end point(s)
- Capture EVERY element and connection
- Note decision branch labels exactly as shown
- For org charts: start from top and work down
- Identify orphan elements (not connected to main flow)

## CONFIDENCE SCORING

Rate confidence based on:
- Label readability
- Connection path clarity (arrows clear vs. ambiguous)
- Decision branch label presence
- Complete paths (start to end traceable)

High confidence (0.8-1.0):
- Clear, readable text
- Explicit flow directions
- Complete paths traceable

Medium confidence (0.5-0.8):
- Readable text but ambiguous flows
- Some missing labels
- Implied connections

Low confidence (0.3-0.5):
- Unclear text or connections
- Complex overlapping flows
- Missing start or end points

Below 0.3:
- Focus on element inventory and general structure only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Explanatory Diagram",

  "ocr_text": "All readable text extracted from the diagram including node labels, connection labels, decision branch labels, swimlane labels, annotations, and legend text",

  "nodes": [
    {
      "node_id": "unique_identifier",
      "label": "Exact text label",
      "element_type": "process | decision | start_end | input_output | other",
      "shape": "rectangle | diamond | oval | parallelogram | other",
      "swimlane_id": "Lane identifier if applicable",
      "position": "Approximate x,y or location description",
      "sequence_number": 1,
      "confidence": 0.0
    }
  ],

  "connections": [
    {
      "from_node_id": "source_node_id",
      "to_node_id": "target_node_id",
      "connection_label": "Label text if present",
      "connection_type": "sequential | conditional | exception | loop_back",
      "direction": "forward | backward | bidirectional",
      "connection_style": "solid | dashed | dotted | other",
      "confidence": 0.0
    }
  ],

  "decision_points": [
    {
      "node_id": "decision_node_id",
      "decision_question": "The condition being evaluated",
      "outcomes": [
        {
          "branch_label": "Yes | No | True | False | condition",
          "target_node_id": "node_id_for_this_outcome"
        }
      ],
      "default_path": "branch_label_of_default",
      "confidence": 0.0
    }
  ],

  "hierarchies": [
    {
      "parent_node_id": "parent_id",
      "child_node_ids": ["child_1_id", "child_2_id"],
      "relationship_type": "reports_to | solid_line | dotted_line",
      "hierarchy_level": 1,
      "confidence": 0.0
    }
  ],

  "swimlanes": [
    {
      "lane_id": "unique_lane_identifier",
      "lane_label": "Role | Department | System | Phase",
      "node_ids": ["node_1_id", "node_2_id"],
      "confidence": 0.0
    }
  ],

  "path_analysis": {
    "main_path": ["node_id_1", "node_id_2", "node_id_3"],
    "exception_paths": [["node_id_a", "node_id_b"]],
    "loops": [["node_id_x", "node_id_y", "node_id_x"]],
    "parallel_branches": [["branch_1_nodes"], ["branch_2_nodes"]],
    "start_points": ["node_id"],
    "end_points": ["node_id"]
  },

  "key_insights": [
    "First key insight about the process or structure",
    "Second key insight",
    "Third key insight"
  ],

  "summary": "Concise 2-4 sentence summary capturing the core purpose, main steps or organizational structure, primary flow or hierarchy, and key decision points or relationships",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Capture ALL text exactly as shown
- Every visible element must be captured
- Every connection must be captured with direction
- If overall confidence < 0.3: focus on element inventory and general structure only
