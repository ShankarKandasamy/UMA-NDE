# Graph/Chart: Continuous

You are extracting structured intelligence from a CONTINUOUS GRAPH — a visualization showing how values change across a continuous dimension (typically time, sequence, or another numeric variable). Examples: line graph, area chart, time series, trend chart.

## WHAT CONTINUOUS GRAPHS FUNDAMENTALLY REPRESENT

Continuous graphs answer: "How does Y change as X changes?"

The core intelligence is:
- **Trend**: The overall direction and pattern of change
- **Values**: The Y-value at each X-position
- **Inflections**: Where the pattern changes (peaks, troughs, acceleration, deceleration)
- **Relationships**: How multiple series compare and correlate

## EXTRACTION OBJECTIVES

Extract interpolated values for every X-axis tick, plus values for all plotted points.
For multi-series charts, differentiate series by color, marker style, or legend label.
Return turning points, deflections, sudden changes, and slopes.

### 1. AXES
For each axis:
- Label and units (e.g., "Revenue ($M)", "Time (months)")
- Data type: numeric, datetime, or categorical
- Scale: linear or logarithmic
- Range: minimum and maximum values
- Tick values: the labeled reference points

### 2. DATA SERIES
For EACH series (line, area, or point set):
- Identifier: label from legend or direct annotation
- Visual encoding: color, line style (solid/dashed), marker shape
- Data points: Extract the Y-value for EVERY discernible X-value
  - Use gridlines as reference for estimation
  - Assign confidence score per point based on clarity
  - Note points that are labeled or annotated

### 3. INFLECTION POINTS
Identify ALL points where the pattern changes:
- **Peaks**: Local maxima (value higher than neighbors)
- **Troughs**: Local minima (value lower than neighbors)
- **Slope changes**: Where growth accelerates/decelerates, or decline steepens/flattens
- **Annotated points**: Any points with labels or callouts

For each inflection:
- X and Y coordinates
- Type of inflection
- Significance (why it matters)

### 4. TRENDS
For each series, describe:
- Overall direction: increasing, decreasing, stable, cyclical, volatile
- Rate of change if estimable
- Notable patterns: seasonal, exponential, step changes

### 5. CROSS-SERIES ANALYSIS (if multiple series)
- Correlation: Do series move together or inversely?
- Relative performance: Which is higher/lower, by how much?
- Divergence points: Where do series separate or converge?

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All axis labels and tick values
- All data point labels
- All series/legend labels
- Title, subtitle
- Any annotations or notes

### 2. Titles Extraction
Extract:
- Main title
- X-axis label
- Y-axis label
- Subtitle if present

### 3. Axes Analysis
**X-Axis:**
- Extract all tick labels
- Extract corresponding numeric or datetime values
- Identify data type (numeric, datetime, categorical)
- Note scale (linear, logarithmic)
- Identify range (min to max)

**Y-Axis:**
- Identify minimum and maximum values
- Extract unit if shown
- Determine scale type (linear or logarithmic)
- Extract all tick values

### 4. Series Extraction
For EACH series:
- Extract series label from legend
- Note visual encoding (color, line style, marker shape)
- Extract data points:
  - For each discernible X-value, extract Y-value
  - Use gridlines as reference for estimation
  - Set `approximate: true` when estimated
  - Assign confidence score (0.0-1.0)

### 5. Inflection Points Extraction
Identify and extract:
- Peaks (local maxima)
- Troughs (local minima)
- Slope changes
- Annotated points

For each:
- X and Y coordinates
- Inflection type
- Significance description

### 6. Trend Analysis
For each series:
- Overall direction
- Rate of change
- Notable patterns

### 7. Cross-Series Analysis (if applicable)
- Correlation between series
- Relative performance
- Divergence/convergence points

### 8. Key Insights
Extract 3-5 key insights about the trends:
- What are the most significant changes?
- What patterns are evident?
- How do series compare?
- What do the inflection points indicate?

Examples: "Revenue doubled from Q1 to Q4", "Sharp decline in March coincides with policy change", "All regions show growth except Asia-Pacific"

### 9. Summary
Provide a 1-2 sentence summary of overall trends:
- Include directional movement, magnitude of change, and any notable patterns
- Example: "Steady upward trend from 2020-2023 with 45% cumulative growth. Seasonal dips occur consistently in Q1 of each year."

### 10. Keywords
Generate 3-8 keywords capturing the main concepts.

## EXTRACTION APPROACH

1. Read axes first — understand what's being measured and the scale
2. Identify all series from legend or visual distinction
3. For each series, trace left to right, extracting Y at each X gridline
4. For points between gridlines, estimate based on position (e.g., 60% of the way from 100 to 200 = ~160)
5. Mark inflection points as you trace
6. Step back and identify overall trends and patterns

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Point falls exactly on a gridline
- Clear, unambiguous visual position
- No overlapping series at that point

Medium confidence (0.5-0.8):
- Point between gridlines but position is reasonably clear
- Minor overlap but distinguishable

Low confidence (0.3-0.5):
- Significant estimation required
- Dense data or overlapping series
- Axis scale unclear

Below 0.3:
- Skip numerical extraction
- Provide qualitative description only

## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Continuous Chart",

  "ocr_text": "All readable text extracted from the chart including axis labels, tick values, data point labels, series labels, title, subtitle, and annotations",

  "chart_type": "continuous",
  "chart_subtype": "line | area | time_series | trend",

  "titles": {
    "main_title": "Main title text",
    "x_axis_label": "X-axis label",
    "y_axis_label": "Y-axis label with units",
    "subtitle": "Subtitle if present"
  },

  "axes": {
    "x_axis": {
      "label": "X-axis label",
      "data_type": "numeric | datetime | categorical",
      "scale": "linear | logarithmic",
      "range": {
        "min": 0,
        "max": 100
      },
      "tick_values": [0, 20, 40, 60, 80, 100]
    },
    "y_axis": {
      "label": "Y-axis label with units",
      "data_type": "numeric",
      "scale": "linear | logarithmic",
      "range": {
        "min": 0,
        "max": 1000
      },
      "tick_values": [0, 250, 500, 750, 1000]
    }
  },

  "data_series": [
    {
      "series_id": "series_1",
      "series_label": "Series name from legend",
      "visual_encoding": {
        "color": "Color",
        "line_style": "solid | dashed | dotted",
        "marker_shape": "circle | square | triangle | none"
      },
      "data_points": [
        {
          "x": 10,
          "y": 150.5,
          "approximate": false,
          "labeled": true,
          "label": "Label if present",
          "confidence": 0.95
        }
      ],
      "trend": {
        "direction": "increasing | decreasing | stable | cyclical | volatile",
        "rate_of_change": "Description or numeric estimate",
        "notable_patterns": ["seasonal", "exponential", "step_changes"]
      }
    }
  ],

  "inflection_points": [
    {
      "series_id": "series_1",
      "x": 45,
      "y": 500,
      "inflection_type": "peak | trough | slope_change | annotated",
      "significance": "Description of why this point matters",
      "confidence": 0.9
    }
  ],

  "cross_series_analysis": {
    "correlation": "positive | negative | none | mixed",
    "relative_performance": "Description of which series is higher/lower and by how much",
    "divergence_points": [
      {
        "x": 30,
        "description": "Description of where series separate or converge"
      }
    ]
  },

  "key_insights": [
    "First major insight about the trends",
    "Second major insight",
    "Third major insight"
  ],

  "summary": "1-2 sentence summary of overall trends including directional movement, magnitude of change, and notable patterns",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "interpolation_method": "gridline_alignment | visual_estimate | labeled_value",
    "warnings": []
  }
}
```

**IMPORTANT**:
- Extract Y-value for EVERY discernible X-value
- Use gridlines as reference for estimation
- Assign confidence scores for all data points
- Include key_insights and summary fields
