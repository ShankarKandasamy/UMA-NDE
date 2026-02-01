# Graph/Chart: Matrix

You are extracting structured intelligence from a MATRIX GRAPH — a visualization showing values across two categorical dimensions, typically displayed as a grid with color-coded cells. Examples: heatmap, confusion matrix, correlation matrix.

## WHAT MATRIX GRAPHS FUNDAMENTALLY REPRESENT

Matrix graphs answer: "What is the value at each intersection of two categorical dimensions?"

The core intelligence is:
- **Cell values**: The value at each row/column intersection
- **Patterns**: Hot spots (high values), cold spots (low values), clusters
- **Relationships**: Correlations, confusions, co-occurrences
- **Symmetry**: Is the matrix symmetric? (relevant for correlation matrices)
- **Diagonal significance**: Often the diagonal has special meaning (e.g., correct predictions)

## EXTRACTION OBJECTIVES

### 1. MATRIX STRUCTURE
- Row labels (complete list in order)
- Column labels (complete list in order)
- Matrix dimensions (rows × columns)
- Is it symmetric? (rows = columns, values mirror across diagonal)

### 2. COLOR SCALE
- Scale type: sequential (low→high), diverging (negative↔positive), or categorical
- Color mapping: what colors represent what values?
- Value range: minimum and maximum values
- Midpoint (for diverging scales)

### 3. CELL VALUES
For EACH cell:
- Row label
- Column label
- Value (read directly if displayed, or estimate from color)
- Confidence based on clarity

### 4. PATTERN ANALYSIS
- **Hot spots**: Where are the highest values? Are they clustered?
- **Cold spots**: Where are the lowest values?
- **Diagonal**: What pattern exists along the diagonal? (often important)
- **Off-diagonal**: What patterns exist away from the diagonal?
- **Clusters**: Are there blocks of similar values?

### 5. STATISTICAL SUMMARY
- Row-wise: totals, averages, or dominant values per row
- Column-wise: totals, averages, or dominant values per column
- Overall: min, max, mean across the matrix

### 6. SPECIAL INTERPRETATION (by matrix type)
**Confusion matrix:**
- Diagonal = correct predictions
- Off-diagonal = errors/confusions
- Calculate precision, recall if possible

**Correlation matrix:**
- Diagonal = perfect correlation (1.0)
- Off-diagonal = cross-correlations
- Identify strongest correlations

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All row labels
- All column labels
- All cell values (if displayed)
- Color scale labels and values
- Title, subtitle
- Legend text

### 2. Matrix Structure Identification
Extract:
- Complete list of row labels in order
- Complete list of column labels in order
- Matrix dimensions
- Symmetry check

### 3. Color Scale Analysis
Identify:
- Scale type (sequential, diverging, categorical)
- Color-to-value mapping
- Value range (min, max)
- Midpoint for diverging scales

### 4. Cell Value Extraction
For each cell:
- Extract or estimate value
- Set `approximate: true` if estimated from color
- Assign confidence score
- Note row and column labels

### 5. Pattern Recognition
Identify:
- Hot spots and their locations
- Cold spots and their locations
- Diagonal patterns
- Off-diagonal patterns
- Clustered regions

### 6. Statistical Summaries
Calculate:
- Row-wise statistics
- Column-wise statistics
- Overall statistics (min, max, mean, median)

### 7. Special Interpretation
For specific matrix types:
- Confusion matrix: accuracy, precision, recall
- Correlation matrix: strongest correlations
- Co-occurrence matrix: most common pairs

### 8. Key Insights
Extract 3-5 key insights about the matrix:
- What are the most significant patterns?
- What relationships stand out?
- What does the diagonal tell us?
- Are there notable clusters or outliers?

### 9. Summary
Provide 1-2 sentence summary of the matrix patterns and relationships.

### 10. Keywords
Generate 3-8 keywords capturing the main concepts.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Values labeled directly in cells
- Clear color-to-value mapping
- Unambiguous row/column labels

Medium confidence (0.5-0.8):
- Values estimated from color scale
- Some label ambiguity
- Partial color mapping

Low confidence (0.3-0.5):
- Significant color estimation required
- Unclear labels
- Ambiguous color scale

Below 0.3:
- Provide qualitative pattern description only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Matrix Chart",

  "ocr_text": "All readable text extracted from the matrix",

  "chart_type": "matrix",
  "chart_subtype": "heatmap | confusion_matrix | correlation_matrix | co_occurrence",

  "matrix_structure": {
    "row_labels": ["Row 1", "Row 2", "Row 3"],
    "column_labels": ["Col 1", "Col 2", "Col 3"],
    "dimensions": {"rows": 3, "columns": 3},
    "is_symmetric": false
  },

  "color_scale": {
    "scale_type": "sequential | diverging | categorical",
    "color_mapping": "Description of color-to-value mapping",
    "value_range": {"min": 0, "max": 100},
    "midpoint": 50,
    "legend": ["Legend entries"]
  },

  "cell_values": [
    {
      "row": "Row 1",
      "column": "Col 1",
      "value": 75.5,
      "approximate": false,
      "confidence": 0.9
    }
  ],

  "pattern_analysis": {
    "hot_spots": [
      {
        "location": "Row 2, Col 3",
        "value": 95,
        "description": "Highest value region"
      }
    ],
    "cold_spots": [
      {
        "location": "Row 1, Col 1",
        "value": 5,
        "description": "Lowest value region"
      }
    ],
    "diagonal_pattern": "Description of diagonal pattern",
    "off_diagonal_pattern": "Description of off-diagonal patterns",
    "clusters": ["Description of clustered regions"]
  },

  "statistical_summary": {
    "row_wise": {
      "Row 1": {"total": 150, "average": 50, "max": 75}
    },
    "column_wise": {
      "Col 1": {"total": 200, "average": 66.7, "max": 90}
    },
    "overall": {
      "min": 5,
      "max": 95,
      "mean": 50,
      "median": 48
    }
  },

  "special_interpretation": {
    "matrix_type": "confusion_matrix | correlation_matrix | other",
    "accuracy": 0.85,
    "precision": 0.80,
    "recall": 0.82,
    "strongest_correlations": [
      {
        "pair": "Variable A - Variable B",
        "correlation": 0.95
      }
    ]
  },

  "key_insights": [
    "First insight about matrix patterns",
    "Second insight",
    "Third insight"
  ],

  "summary": "1-2 sentence summary of matrix patterns and relationships",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Extract all cell values with confidence scores
- Set `approximate: true` when values are estimated from color
- Identify patterns systematically
- Include key_insights and summary fields
