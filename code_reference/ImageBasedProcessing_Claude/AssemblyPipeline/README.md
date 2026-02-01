# Assembly Pipeline

The Assembly Pipeline merges data from two separate pipelines and prepares it for three storage systems:

**Input Sources**:
1. **Text Extraction Pipeline** (Stage 12 output) - Extracted text content from PDFs
2. **Visual Analysis Pipeline** (Stage 3 output) - Analyzed images and tables with detailed metadata

**Output Destinations**:
1. **Semantic Search** - Vector embeddings for ChromaDB
2. **Full-Text Search** - Indexed chunks for keyword search
3. **Graph Database** - Entity/edge/claims for Neo4j

## Pipeline Structure

```
AssemblyPipeline/
├── ass_stage_1_merge_data.py    # Merges text + visual analysis
├── ass_stage_2_hierarchy.py     # Extracts document hierarchy with GPT-4o-mini
├── ass_stage_3_llm_chunks.py    # LLM-based semantic chunking with GPT-4o
├── ass_stage_4_fts_chunks.py    # Creates vector embeddings
├── ass_stage_5_graph_data.py    # Prepares graph DB payload
├── ass_test_pipeline.py         # Test orchestrator (runs all stages)
└── README.md                     # This file
```

## Complete Pipeline Flow

```
Stage 12 (Text) ────┐
                     ├──> Stage 1: Merge ──> Stage 2: Hierarchy ──> Stage 3: LLM Chunks ──┬──> Stage 4: FTS/Embeddings
Stage 3 (Visual) ───┘                                                                      └──> Stage 5: Graph Payload
                                                                                                    │
                                                                                                    ├──> Entity/Edge Extraction
                                                                                                    └──> Claims Extraction
```

---

## Stage 1: Merge Data

**Status**: ✅ FULLY OPERATIONAL - Production ready

**Purpose**: Combine extracted text content with visual analysis into a single JSON structure.

**Input**:
- Text content: `{document}/stage_12_final/page_N_final.md` (markdown files)
- Visual analysis: `VisualPipeline/{document}/stage_3_analysis/stage_3_analysis_metadata.json`

**Output**: `{document}/assembly/merged_data.json`

**Output Format**:
```json
{
  "document_name": {
    "page_1": {
      "text_content": "# Full markdown text content...",
      "visual_analysis": {
        "image_1": {
          "type": "Picture",
          "bbox": {...},
          "category": "graph/chart: relationship",
          "visual_analysis": {...}
        },
        "table_1": {
          "type": "Table",
          "bbox": {...},
          "category": "diagram: technical",
          "visual_analysis": {...}
        }
      }
    },
    "page_2": {...}
  }
}
```

### Usage

```bash
# Merge DeepWalk document
python ass_stage_1_merge_data.py DeepWalk

# Merge with custom output path
python ass_stage_1_merge_data.py DeepWalk --output custom/path/output.json

# Merge document with spaces in name
python ass_stage_1_merge_data.py "Nelson Advanced Functions 12 Textbook"
```

### Example Output Statistics

**DeepWalk Document**:
- Total pages: 6
- Text content: 4,409 - 6,406 characters per page
- Visual elements:
  - Page 1: 1 image (relationship chart)
  - Page 2: 0 visual elements
  - Page 3: 1 image (continuous chart)
  - Page 4: 1 table (algorithm pseudocode)
  - Page 5: 2 images (explanatory diagram + continuous chart)
  - Page 6: 0 visual elements
- Output file size: 64.9 KB

## Implementation Details

### Visual Element Naming Convention

Visual elements are numbered sequentially per page:
- **Images**: `image_1`, `image_2`, `image_3`, ...
- **Tables**: `table_1`, `table_2`, `table_3`, ...

The script maintains separate counters for images and tables, incrementing each when a detection of that type is encountered.

### Data Preservation

The merge process preserves **all** metadata from both pipelines:
- Complete text content (including markdown formatting)
- Full visual analysis results (nodes, edges, data series, etc.)
- Bounding box coordinates
- Confidence scores
- Category classifications
- Model metadata (timestamps, token counts, etc.)

### Error Handling

The script handles common edge cases:
- Missing stage 12 directory (warns, continues with empty text)
- Missing stage 3 file (warns, continues without visual data)
- Pages with only text (no visual elements)
- Pages with only visual elements (no text)
- Unicode encoding issues (uses UTF-8)

---

## Stage 2: Hierarchy Extraction

**Status**: ✅ FULLY OPERATIONAL - Production ready

**Purpose**: Extract document hierarchy (headings, sections, structure) using GPT-4o-mini to provide structural context for downstream chunking.

**Input**: `{document}/ass_stage_1_merge_data/merged_data.json`

**Output**:
- Hierarchy data: `{document}/ass_stage_2_hierarchy/hierarchy_data.json`
- Corrected markdown: `{document}/ass_stage_2_hierarchy/{doc}_corrected.md`
- Text payload: `{document}/ass_stage_2_hierarchy/{doc}_hierarchy_payload.json`

**Output Format** (Enhanced JSON):
```json
{
  "document_name": "DeepWalk",
  "total_pages": 6,
  "hierarchy": {
    "page_1": {
      "corrected_markdown": "# DeepWalk: Online Learning\n\n## Introduction...",
      "headings": [
        {"level": 1, "text": "DeepWalk", "char_start": 0, "char_end": 9},
        {"level": 2, "text": "Introduction", "char_start": 150, "char_end": 162}
      ],
      "sections": [
        {
          "title": "Introduction",
          "heading_level": 2,
          "char_start": 150,
          "char_end": 500,
          "parent_title": null,
          "subsections": []
        }
      ],
      "metadata": {
        "structure_type": "academic_paper",
        "has_numbered_sections": true,
        "total_headings": 5
      },
      "_meta": {
        "page_key": "page_1",
        "model": "gpt-4o-mini",
        "timestamp": "2025-12-22T...",
        "total_tokens": 1595
      }
    }
  }
}
```

**Key Features**:
- **Enhanced JSON Output**: Returns both corrected markdown AND extracted structure in one API call
- **GPT-4o-mini Analysis**: Identifies document structure with validated JSON responses
- **Heading Correction**: Fixes heading levels and removes false headings (figures, captions, lists)
- **Character-Precise Positions**: Exact char_start/char_end offsets in corrected markdown
- **Section Boundaries**: Maps out major sections with parent-child relationships
- **Structure Type Classification**: Identifies document type (academic paper, textbook, report, etc.)
- **Corrected Markdown**: Saves cleaned markdown with proper heading hierarchy
- **Payload Preservation**: Saves original text content for comparison and debugging
- **Validation**: Automatic schema validation prevents malformed responses

### Usage

```bash
# Extract hierarchy for DeepWalk document
python ass_stage_2_hierarchy.py DeepWalk

# Extract with custom output path
python ass_stage_2_hierarchy.py DeepWalk --output custom/path/hierarchy.json
```

### Example Output Statistics

**DeepWalk Document** (6 pages):
- Total headings: 15-20 (varies by document complexity)
- Total sections: 8-12 major sections
- Structure type: academic_paper
- Output file size: ~10-15 KB

---

## Stage 3: LLM-based Semantic Chunking

**Status**: ✅ FULLY OPERATIONAL - Production ready

**Purpose**: Create semantically coherent chunks using GPT-4o-mini for optimal RAG retrieval. Uses hierarchy from Stage 2 to inform semantic boundaries.

**Input**:
- Merged data: `{document}/ass_stage_1_merge_data/merged_data.json`
- Hierarchy data (optional): `{document}/ass_stage_2_hierarchy/hierarchy_data.json`

**Output**:
- Chunked data: `{document}/ass_stage_3_llm_chunks/chunked_data.json`
- Payloads: `{document}/ass_stage_3_llm_chunks/{doc}_payloads.json`

**Key Features**:
- **GPT-4o-mini Chunking**: Intelligent semantic chunking (700-900 characters target)
- **Hierarchy-Aware**: Can leverage document structure from Stage 2
- **Visual Integration**: Includes figures and tables in relevant chunks
- **Batch Processing**: Processes 2 pages per batch to avoid API timeouts
- **Metadata Preservation**: Tracks chunks, tokens, character counts

### Usage

```bash
# Chunk with hierarchy context
python ass_stage_3_llm_chunks.py DeepWalk

# Chunk with custom hierarchy file
python ass_stage_3_llm_chunks.py DeepWalk --hierarchy-file path/to/hierarchy.json
```

---

## Stage 4: Full-Text Search Preparation

**Status**: ⏳ BOILERPLATE ONLY - Ready for implementation

**Purpose**: Create vector embeddings for semantic search in ChromaDB.

**Input**: `{document}/ass_stage_3_llm_chunks/chunked_data.json`

**Output**: `{document}/ass_stage_4_fts_chunks/fts_ready.json`

**Planned Features**:
- OpenAI text-embedding-3-large (1536 dimensions)
- Batch processing for efficiency
- ChromaDB-compatible format
- Metadata preservation

**Current Implementation**:
- ✅ Loads chunked data from Stage 3
- ✅ Argument parsing and file path handling
- ⏳ TODO: Embedding creation logic

### Usage

```bash
# Test current boilerplate
python ass_stage_4_fts_chunks.py DeepWalk
```

---

## Stage 5: Graph Database Preparation

**Status**: ⏳ BOILERPLATE ONLY - Ready for implementation

**Purpose**: Prepare extraction payload for entity/edge and claims extraction.

**Input**:
- Chunked data: `{document}/ass_stage_3_llm_chunks/chunked_data.json`
- Merged data: `{document}/ass_stage_1_merge_data/merged_data.json`

**Output**: `{document}/ass_stage_5_graph_data/graph_payload.json`

**Planned Features**:
- Extraction-ready format for graph DB pipeline
- Integrates visual analysis with chunks
- Metadata for entity/edge extraction
- No API costs (pure data transformation)

**Current Implementation**:
- ✅ Loads chunked data from Stage 3
- ✅ Loads merged data from Stage 1
- ✅ Argument parsing and file path handling
- ⏳ TODO: Graph payload creation logic

### Usage

```bash
# Test current boilerplate
python ass_stage_5_graph_data.py DeepWalk
```

---

## Test Pipeline

**Purpose**: Orchestrate all assembly stages in a single command.

**Prerequisites**:
- Text extraction pipeline must be completed (stages 1-12)
- Visual analysis pipeline must be completed (stages 1-4)

**Usage**:
```bash
# Run complete assembly pipeline
python ass_test_pipeline.py DeepWalk

# Process multiple documents
python ass_test_pipeline.py DeepWalk "Nelson Advanced Functions 12 Textbook"

# Specify custom base directory
python ass_test_pipeline.py --base-dir /path/to/base DeepWalk
```

**What It Does**:
1. ✅ Checks prerequisites (text + visual pipeline outputs)
2. ✅ Runs Stage 1: Merge Data (fully functional)
3. ✅ Runs Stage 2: Hierarchy Extraction (fully functional)
4. ✅ Runs Stage 3: LLM Chunking (fully functional)
5. ⏸️ Skips Stage 4: FTS Preparation (boilerplate only)
6. ⏸️ Skips Stage 5: Graph Payload (boilerplate only)
7. 📊 Provides detailed summary and next steps

**Example Output**:
```
================================================================================
ASSEMBLY PIPELINE: DeepWalk
================================================================================
Checking prerequisites...
[OK] Text pipeline: 6 MD files found
[OK] Visual pipeline: Found

STAGE 1: Merge Data
--------------------------------------------------------------------------------
[OK] Stage 1 complete: 6 pages, 5 visual elements (64.9 KB)

STAGE 2: Hierarchy Extraction
--------------------------------------------------------------------------------
[OK] Stage 2 complete: 18 headings, 10 sections (12.3 KB)

STAGE 3: LLM Chunks
--------------------------------------------------------------------------------
[OK] Stage 3 complete: 24 chunks across 3 batches (45.2 KB)

STAGE 4-5: Skipped (boilerplate only)

Successfully processed: 1/1 documents
```

---

## Current Status

### Implemented Stages

**✅ Stage 1: Merge Data** - FULLY OPERATIONAL
- Tested on DeepWalk (6 pages)
- Output: 64.9 KB merged JSON
- Production ready

**✅ Stage 2: Hierarchy Extraction** - FULLY OPERATIONAL
- GPT-4o-mini hierarchy extraction
- Headings, sections, structure detection
- Production ready

**✅ Stage 3: LLM Chunks** - FULLY OPERATIONAL
- GPT-4o-mini semantic chunking
- 700-900 character target chunks
- Production ready

**⏳ Stage 4: FTS Preparation** - BOILERPLATE ONLY
- Loads chunked data successfully
- Ready for embedding logic implementation

**⏳ Stage 5: Graph Payload** - BOILERPLATE ONLY
- Loads both merged and chunked data successfully
- Ready for payload creation logic implementation

### Testing Current Implementation

**Option 1: Test Complete Pipeline** (Recommended)
```bash
# Run all stages in sequence
python ass_test_pipeline.py DeepWalk

# Process multiple documents
python ass_test_pipeline.py DeepWalk "Nelson Advanced Functions 12 Textbook"
```

**Option 2: Test Individual Stages**
```bash
# Stage 1: Fully functional
python ass_stage_1_merge_data.py DeepWalk

# Stage 2: Fully functional
python ass_stage_2_hierarchy.py DeepWalk  # Requires Stage 1 output

# Stage 3: Fully functional
python ass_stage_3_llm_chunks.py DeepWalk  # Requires Stage 1 output (Stage 2 optional)

# Stages 4-5: Boilerplate testing
python ass_stage_4_fts_chunks.py DeepWalk  # Requires Stage 3 output
python ass_stage_5_graph_data.py DeepWalk  # Requires Stages 1 & 3 output
```

## Output Files

Currently available after Stages 1-3:

```
DeepWalk/
├── ass_stage_1_merge_data/
│   └── merged_data.json                     # Stage 1: Text + visual merged (✅ Available)
├── ass_stage_2_hierarchy/
│   ├── hierarchy_data.json                  # Stage 2: Enhanced JSON with structure (✅ Available)
│   ├── DeepWalk_corrected.md                # Stage 2: Corrected markdown (✅ Available)
│   └── DeepWalk_hierarchy_payload.json      # Stage 2: Original text payload (✅ Available)
└── ass_stage_3_llm_chunks/
    ├── chunked_data.json                    # Stage 3: Semantic chunks (✅ Available)
    └── DeepWalk_payloads.json               # Stage 3: Payload metadata (✅ Available)
```

After full implementation:

```
DeepWalk/
├── ass_stage_1_merge_data/
│   └── merged_data.json                     # Stage 1: Text + visual merged
├── ass_stage_2_hierarchy/
│   ├── hierarchy_data.json                  # Stage 2: Enhanced JSON with structure
│   ├── DeepWalk_corrected.md                # Stage 2: Corrected markdown
│   └── DeepWalk_hierarchy_payload.json      # Stage 2: Original text payload
├── ass_stage_3_llm_chunks/
│   ├── chunked_data.json                    # Stage 3: Semantic chunks
│   └── DeepWalk_payloads.json               # Stage 3: Payload metadata
├── ass_stage_4_fts_chunks/
│   └── fts_ready.json                       # Stage 4: Vector embeddings (⏳ TODO)
└── ass_stage_5_graph_data/
    └── graph_payload.json                   # Stage 5: Graph DB ready (⏳ TODO)
```

## Next Steps

The assembly pipeline outputs can be used for:

1. **Semantic Search** - Load `fts_ready.json` into ChromaDB
2. **Keyword Search** - Index `chunked_data.json` for FTS
3. **Knowledge Graph** - Process `graph_payload.json` through:
   - Entity/edge extraction (o1-mini)
   - Claims extraction (GPT-4o)
   - Neo4j ingestion

## Implementation Priority

1. ✅ **Stage 1: Merge Data** - COMPLETE
2. ✅ **Stage 2: Hierarchy Extraction** - COMPLETE
3. ✅ **Stage 3: LLM Chunks** - COMPLETE
4. ⏳ **Stage 5: Graph Payload** - Next priority (no API costs, enables graph DB pipeline)
5. ⏳ **Stage 4: FTS Preparation** - Enables semantic search
