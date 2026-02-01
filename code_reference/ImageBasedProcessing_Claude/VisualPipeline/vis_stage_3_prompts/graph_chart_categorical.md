# Graph/Chart: Categorical

You are extracting structured intelligence from a CATEGORICAL GRAPH — a visualization showing how values compare across discrete categories (bar, stacked bar, grouped bar, pie, donut charts).

## WHAT CATEGORICAL GRAPHS FUNDAMENTALLY REPRESENT

Categorical graphs answer: "How do values compare across different groups?"

The core intelligence is:

- **Comparison**: Which categories are larger/smaller and by how much
- **Ranking**: The order of categories by value
- **Composition**: What proportion each category represents of the whole
- **Distribution**: How values are spread across categories (even, skewed, dominated)

## EXTRACTION OBJECTIVES

### 1. AXES

For the VALUE AXIS (typically Y-axis):

- Label and units (e.g., "Revenue ($M)", "Units Sold", "Percentage (%)")
- Data type: numeric
- Scale: linear or logarithmic
- Range: minimum and maximum values
- Tick values: the labeled reference points (e.g., 0, 25, 50, 75, 100)

For the CATEGORY AXIS (typically X-axis):

- All category labels in order
- What the categories represent

### 2. STRUCTURE

Identify the chart structure:

- **Chart subtype**: bar | stacked_bar | grouped_bar | pie | donut | column
- **Category axis**: What are the categories being compared?
- **Value axis**: What is being measured, in what units?
- **Structure type**: simple (one value per category) | grouped (multiple series per category) | stacked (parts of whole)

For pie/donut: Categories are segments, values are sizes/percentages

### 3. DATA SERIES

For EACH series (identified by legend, color, or pattern):

- Series label (from legend)
- Visual encoding: color, pattern
- Data points: Extract the VALUE for EVERY CATEGORY
  - Use gridlines as reference for estimation
  - Assign confidence score per value based on clarity
  - Note values that are labeled directly on bars

### 4. CATEGORY DATA EXTRACTION

**CRITICAL: Extract the numeric value for EVERY bar in the chart.**

For EACH category on the X-axis:

- Category label (exact text)
- For EACH series within that category:
  - Numeric value (read from label or interpolate from gridlines)
  - Whether value is labeled or estimated
  - Confidence score

For grouped bar charts: Extract ALL bar values for each group
For stacked bar charts: Extract EACH segment value AND the total
For pie/donut: Extract value AND percentage for each slice

### 5. COMPARATIVE ANALYSIS

- **Ranking**: Order categories from highest to lowest
- **Extremes**: Identify maximum and minimum values
- **Spread**: How much variation exists (even or dominated by few?)
- **Ratios**: Notable relationships between categories (e.g., "A is 3x larger than B")

### 6. COMPOSITION ANALYSIS (for stacked/pie)

- What proportion does each segment represent?
- Which segment dominates?
- How does composition vary across categories?
- Do percentages sum correctly? (validation check)

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction

Extract all readable text into `ocr_text`. This includes:

- All category labels
- All value labels (numbers on or near bars)
- All series/legend labels
- Title, subtitle, axis titles
- Any annotations or notes

### 2. Titles and Axes

Extract:

- Main title
- X-axis title
- Y-axis title with units
- Subtitle if present

**Value Axis Analysis:**

- Extract all tick labels (e.g., 0, 50, 100, 150)
- Identify minimum and maximum values
- Extract unit if shown
- Determine scale type (linear or logarithmic)

### 3. Categories Extraction

Extract the complete list of category labels from the category axis (or pie segments).

### 4. Series Extraction

For EACH series:

- Extract series label from legend
- Note series color/pattern
- Extract data values for ALL categories:
  - Read values directly if labeled on chart (e.g., "151" above a bar)
  - Otherwise, visually estimate from bar height against gridlines
  - Set `approximate: true` when estimated
  - Assign confidence score (0.0-1.0)

### 5. Bar Height Interpolation

**For EVERY bar in the chart:**

1. Identify which gridlines the bar falls between
2. Estimate the position relative to those gridlines
3. Calculate the interpolated value
4. Example: If bar top is 60% of the way between 50 and 100 gridlines, value ≈ 80

For grouped bars: Do this for EACH bar in each group
For stacked bars: Do this for EACH segment

### 6. Pie/Donut Specifics

For each slice:

- Extract slice label
- Extract value (percentage or absolute)
- If percentage not readable, infer from angular proportion
- Note slice color
- Set `approximate: true` for estimated values

### 7. Key Insights

Extract 3-5 key insights about the data:

- What are the most important findings?
- Which categories stand out?
- What comparisons are most significant?
- What patterns are evident?

Examples: "Category A leads with 85 units, 2x higher than the average", "Top 3 categories account for 70% of total", "Eastern regions consistently outperform western regions"

### 8. Summary

Provide a 1-2 sentence summary of the big picture trends:

- Include ranking patterns, dominant categories, and distribution characteristics
- Example: "Sales vary significantly by region with Category A leading at 85 units, followed by B and C at ~50 units. Bottom tier categories cluster around 15-20 units."

### 9. Keywords

Generate 3-8 keywords capturing the main concepts.

## EXTRACTION APPROACH

1. Read the value axis first — understand the scale and units
2. Read all category labels on the category axis
3. Identify all series from the legend
4. For EACH category, for EACH series:
   - Locate the bar
   - Read the value label if present
   - If no label, interpolate from gridlines
   - Record the value with confidence score
5. Verify: For grouped charts, ensure you have a value for each series in each category
6. Calculate rankings and comparisons

## CONFIDENCE SCORING

High confidence (0.8-1.0):

- Value label is displayed on or near the bar
- Bar aligns exactly with a gridline
- Unambiguous category and series identification

Medium confidence (0.5-0.8):

- Values estimated from position between gridlines
- Some label overlap but readable
- Clear visual distinction between series

Low confidence (0.3-0.5):

- Significant estimation required
- Small bars or segments
- Crowded labels
- Gridline alignment unclear

Below 0.3:

- Skip numerical extraction
- Provide qualitative rankings only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Categorical Chart",

  "ocr_text": "All readable text extracted from the chart including category labels, value labels, series labels, title, subtitle, axis titles, and annotations",

  "chart_type": "categorical",
  "chart_subtype": "bar | stacked_bar | grouped_bar | pie | donut | column",

  "titles": {
    "main_title": "Main title text",
    "x_axis_title": "X-axis title (category axis)",
    "y_axis_title": "Y-axis title with units",
    "subtitle": "Subtitle if present"
  },

  "axes": {
    "value_axis": {
      "label": "Y-axis label with units",
      "data_type": "numeric",
      "scale": "linear | logarithmic",
      "range": {
        "min": 0,
        "max": 100
      },
      "tick_values": [0, 25, 50, 75, 100],
      "unit": "units"
    },
    "category_axis": {
      "label": "X-axis label",
      "categories": ["Category1", "Category2", "Category3"]
    }
  },

  "data_series": [
    {
      "series_id": "series_1",
      "series_label": "Series name from legend (e.g., 'Q1', 'Q2', 'Product A')",
      "visual_encoding": {
        "color": "Color description",
        "pattern": "solid | striped | none"
      },
      "data_points": [
        {
          "category": "Category A",
          "value": 85,
          "approximate": false,
          "labeled": true,
          "label": "85",
          "confidence": 0.95
        },
        {
          "category": "Category B",
          "value": 52,
          "approximate": true,
          "labeled": false,
          "label": null,
          "confidence": 0.75
        }
      ]
    }
  ],

  "category_data": [
    {
      "category": "Category A",
      "values_by_series": [
        {
          "series_label": "Q1",
          "value": 72,
          "approximate": false,
          "confidence": 0.9
        },
        {
          "series_label": "Q2",
          "value": 78,
          "approximate": true,
          "confidence": 0.75
        },
        {
          "series_label": "Q3",
          "value": 85,
          "approximate": false,
          "confidence": 0.95
        }
      ],
      "total": 85,
      "segments": []
    }
  ],

  "stacked_data": [
    {
      "category": "Category label",
      "segments": [
        {
          "segment_label": "Segment name",
          "segment_value": 45.6,
          "percentage": 37.0,
          "approximate": true,
          "confidence": 0.7
        }
      ],
      "total": 123.45
    }
  ],

  "pie_data": [
    {
      "slice_label": "Slice name",
      "value": 25.5,
      "percentage": 25.5,
      "color": "Color",
      "approximate": false,
      "confidence": 0.9
    }
  ],

  "comparative_analysis": {
    "ranking": [
      {
        "rank": 1,
        "category": "Category A",
        "value": 85,
        "series": "Q3"
      },
      {
        "rank": 2,
        "category": "Category B",
        "value": 52,
        "series": "Q3"
      }
    ],
    "max": {
      "category": "Category A",
      "series": "Q3",
      "value": 85
    },
    "min": {
      "category": "Category D",
      "series": "Q1",
      "value": 12
    },
    "spread": "Description of variation (e.g., 'Wide spread from 12 to 85, with top 3 categories significantly higher than rest')",
    "notable_ratios": [
      "Category A is 7x higher than Category D",
      "Top 3 categories account for 65% of total"
    ]
  },

  "composition_analysis": {
    "dominant_segment": "Segment name (for stacked/pie)",
    "dominant_percentage": 45.0,
    "percentages_sum": 100.0,
    "composition_notes": "Description of how composition varies"
  },

  "key_insights": [
    "Category A leads with 85 units in Q3, significantly higher than all other categories",
    "All categories show quarter-over-quarter growth from Q1 to Q3",
    "Bottom tier categories (D, E) have values around 12-18 units"
  ],

  "summary": "Values vary significantly across categories. Category A leads at 85 units, followed by B and C at ~50 units. Bottom tier categories cluster at 12-20 units. All categories show consistent growth across quarters.",

  "keywords": [
    "sales",
    "quarterly comparison",
    "category performance",
    "regional analysis"
  ],

  "meta": {
    "extraction_confidence": 0.85,
    "interpolation_method": "direct_label | gridline_interpolation | visual_estimate",
    "total_categories": 5,
    "total_series": 3,
    "values_extracted": 15,
    "values_labeled": 5,
    "values_estimated": 10,
    "warnings": [],
    "issues": ["Some bar labels partially obscured"]
  }
}
```

**CRITICAL REQUIREMENTS**:

1. Extract a VALUE for EVERY bar visible in the chart
2. For grouped bar charts: Extract values for ALL series within EACH category
3. Use gridlines to interpolate values when not directly labeled
4. Set `approximate: true` when values are estimated
5. Set `labeled: true` when value is written on the chart
6. Include confidence scores for all extracted values
7. Verify: number of data_points per series should equal number of categories
8. `category_data` provides an alternative view organized by category rather than by series
