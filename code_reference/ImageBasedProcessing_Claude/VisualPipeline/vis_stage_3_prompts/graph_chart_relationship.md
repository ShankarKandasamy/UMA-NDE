# Graph/Chart: Relationship

You are extracting structured intelligence from a RELATIONSHIP GRAPH — a visualization showing how quantities flow between entities or how nodes connect in a network. Examples: Sankey diagram, network graph, flow chart, alluvial diagram, chord diagram.

## WHAT RELATIONSHIP GRAPHS FUNDAMENTALLY REPRESENT

Relationship graphs answer: "How do things connect? Where does quantity flow? What's the structure?"

The core intelligence is:
- **Nodes**: What entities exist in the system?
- **Connections**: What connects to what, and how strongly?
- **Flow**: How much quantity moves along each path?
- **Structure**: What's the overall topology? (hierarchical, networked, linear)
- **Bottlenecks**: Where does flow concentrate or get constrained?

## EXTRACTION OBJECTIVES

### 1. NODES/ENTITIES
For EACH node in the graph:
- Label/name
- Value/magnitude if shown (e.g., total flow through this node)
- Position in hierarchy or layout (level, stage)
- Node type if distinguishable (source, sink, intermediate)
- Visual attributes (color, size)

### 2. CONNECTIONS/EDGES
For EACH connection:
- Source node
- Target node
- Direction (if directed)
- Value/weight/flow magnitude
- Label (if any)
- Visual attributes (thickness, color)

### 3. FLOW ANALYSIS (for flow-based graphs)
- Total input to the system
- Total output from the system
- Flow conservation: does input ≈ output? (Sankey diagrams should balance)
- Stage-to-stage conversion rates
- Leakage/loss points

### 4. NETWORK STRUCTURE (for network graphs)
- Identify highly connected nodes (hubs)
- Identify isolated or weakly connected nodes
- Note clusters or communities
- Identify bridges between clusters

### 5. PATH ANALYSIS
- Primary/critical path (highest flow or importance)
- Alternative paths
- Bottleneck points (where flow concentrates)
- Dead ends or sinks

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All node labels/names
- All connection labels/values
- Flow values
- Stage names
- Title, subtitle
- Legend text

### 2. Node/Entity Extraction
For each node:
- Assign unique `node_id`
- Extract label/name exactly as shown
- Extract value/magnitude if displayed
- Identify node type: source | sink | intermediate | hub
- Note position: level, stage, or layout position
- Note visual attributes (color, size)
- Assign confidence score

### 3. Connection/Edge Extraction
For each connection:
- Identify source node (`from_node_id`)
- Identify target node (`to_node_id`)
- Extract flow value/weight if shown
- Note direction: directed | undirected
- Extract label if present
- Note visual attributes (thickness, color)
- Assign confidence score

### 4. Flow Analysis (for Sankey/flow diagrams)
Calculate:
- Total input (sum of all source flows)
- Total output (sum of all sink flows)
- Flow balance check
- Stage-to-stage conversion/retention rates
- Identify leakage or loss points

### 5. Network Analysis (for network graphs)
Identify:
- Highly connected nodes (hubs)
- Isolated or weakly connected nodes
- Clusters or communities
- Bridge nodes connecting clusters
- Network density

### 6. Path Analysis
Identify:
- Primary/critical paths (highest flow)
- Alternative paths
- Bottleneck points
- Dead ends or terminal nodes

### 7. Key Insights
Extract 3-5 key insights about the relationships:
- What are the main flows or connections?
- Where are the bottlenecks?
- Which nodes are most central or important?
- What patterns emerge in the network?

### 8. Summary
Provide 1-2 sentence summary of the relationship structure and main flows.

### 9. Keywords
Generate 3-8 keywords capturing the main concepts.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Values labeled directly on flows/edges
- Clear node and connection structure
- Unambiguous labels

Medium confidence (0.5-0.8):
- Values estimated from visual thickness/size
- Some structural ambiguity
- Partial labels

Low confidence (0.3-0.5):
- Significant estimation required
- Complex overlapping structure
- Missing labels

Below 0.3:
- Provide qualitative structure description only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Relationship Chart",

  "ocr_text": "All readable text extracted from the chart",

  "chart_type": "relationship",
  "chart_subtype": "sankey | network | flow | alluvial | chord | other",

  "nodes": [
    {
      "node_id": "node_1",
      "label": "Node name",
      "value": 100,
      "node_type": "source | sink | intermediate | hub",
      "position": {
        "level": 1,
        "stage": "Stage name"
      },
      "visual_attributes": {
        "color": "Color",
        "size": "Size description"
      },
      "confidence": 0.9
    }
  ],

  "connections": [
    {
      "from_node_id": "node_1",
      "to_node_id": "node_2",
      "flow_value": 50,
      "label": "Connection label",
      "direction": "directed | undirected",
      "visual_attributes": {
        "thickness": "Thickness description",
        "color": "Color"
      },
      "confidence": 0.9
    }
  ],

  "flow_analysis": {
    "total_input": 100,
    "total_output": 95,
    "flow_balance": "balanced | loss | gain",
    "conversion_rates": [
      {
        "from_stage": "Stage 1",
        "to_stage": "Stage 2",
        "retention_rate": 0.85,
        "loss": 15
      }
    ],
    "leakage_points": ["Description of loss points"]
  },

  "network_analysis": {
    "hub_nodes": ["node_ids of highly connected nodes"],
    "isolated_nodes": ["node_ids of isolated nodes"],
    "clusters": [
      {
        "cluster_id": "cluster_1",
        "node_ids": ["node_1", "node_2", "node_3"]
      }
    ],
    "bridge_nodes": ["node_ids connecting clusters"],
    "network_density": 0.35
  },

  "path_analysis": {
    "primary_paths": [
      {
        "path": ["node_1", "node_2", "node_3"],
        "total_flow": 75,
        "description": "Main flow path"
      }
    ],
    "alternative_paths": [
      {
        "path": ["node_1", "node_4", "node_3"],
        "total_flow": 25
      }
    ],
    "bottlenecks": [
      {
        "node_id": "node_2",
        "flow_concentration": 0.75,
        "description": "75% of flow passes through this node"
      }
    ],
    "dead_ends": ["node_ids with no outgoing connections"]
  },

  "key_insights": [
    "First insight about relationships and flows",
    "Second insight",
    "Third insight"
  ],

  "summary": "1-2 sentence summary of relationship structure and main flows",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Extract all nodes and connections with confidence scores
- Calculate flow totals and check balance
- Identify critical paths and bottlenecks
- Include key_insights and summary fields
