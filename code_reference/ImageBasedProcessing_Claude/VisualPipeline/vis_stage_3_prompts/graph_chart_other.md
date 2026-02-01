# Graph/Chart: Other

You are extracting structured intelligence from a SPECIALIZED GRAPH — a visualization with a specific purpose that doesn't fit the standard continuous/categorical/distribution/relationship/matrix patterns. Examples: radar/spider chart, waterfall chart, funnel chart, gauge chart, bullet chart.

## FIRST: IDENTIFY THE VISUALIZATION TYPE

Before extracting, determine what kind of specialized visualization this is:

### 1. RADAR/SPIDER
Multiple variables arranged radially around a center
- Extract: variable names, values for each variable, scale
- Look for: polygonal shapes, radial axes

### 2. WATERFALL
Shows cumulative effect of sequential positive/negative values
- Extract: starting value, increments/decrements, ending value
- Look for: floating bars, running total

### 3. FUNNEL
Shows progressive filtering/conversion through stages
- Extract: stage names, values at each stage, conversion rates
- Look for: tapering shape, decreasing values

### 4. GAUGE/DIAL
Shows single value on a scale (like speedometer)
- Extract: current value, min/max range, threshold zones
- Look for: arc or circular scale, pointer/needle

### 5. BULLET
Compact linear gauge showing performance vs. target
- Extract: actual value, target, qualitative ranges
- Look for: bar with marker, background zones

## EXTRACTION OBJECTIVES BY TYPE

### RADAR/SPIDER CHARTS
- All axis labels (variables)
- Scale for each axis (min, max, intervals)
- Data values for each variable
- Multiple series if overlaid

### WATERFALL CHARTS
- Starting value
- Each increment/decrement with label
- Running total at each step
- Ending value
- Bridge connectors

### FUNNEL CHARTS
- Stage names in order
- Value/count at each stage
- Conversion rates between stages
- Drop-off amounts

### GAUGE CHARTS
- Current value
- Scale range (min to max)
- Threshold zones (e.g., red/yellow/green)
- Target value if shown

### BULLET CHARTS
- Actual value
- Target/goal value
- Qualitative ranges (poor/satisfactory/good)
- Comparative measure if present

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All variable/axis labels
- All value labels
- All stage/category names
- Scale markers
- Title, subtitle
- Legend text

### 2. Chart Type Identification
Determine:
- Specific chart subtype
- Purpose of the visualization
- Primary message

### 3. Type-Specific Extraction
Follow the appropriate extraction pattern based on chart type:

**For Radar:**
- Extract all axes and their scales
- Extract values for each variable
- Note series if multiple

**For Waterfall:**
- Extract starting value
- Extract each change (up or down)
- Track running total
- Extract ending value

**For Funnel:**
- Extract stage names in sequence
- Extract values at each stage
- Calculate conversion rates
- Identify drop-off points

**For Gauge:**
- Extract current value
- Extract scale range
- Identify threshold zones
- Note target if present

**For Bullet:**
- Extract actual performance
- Extract target
- Identify qualitative ranges
- Note comparative measure

### 4. Pattern Analysis
Identify:
- Strengths and weaknesses (radar)
- Biggest changes (waterfall)
- Biggest drop-offs (funnel)
- Performance vs. target (gauge/bullet)

### 5. Key Insights
Extract 3-5 key insights about the visualization:
- What does the chart primarily communicate?
- What are the most significant values or patterns?
- How does actual compare to target?
- What trends or anomalies are evident?

### 6. Summary
Provide 1-2 sentence summary of the main message.

### 7. Keywords
Generate 3-8 keywords capturing the main concepts.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Values labeled directly
- Clear scale markers
- Unambiguous structure

Medium confidence (0.5-0.8):
- Values estimated from position
- Some ambiguity in scale
- Implied values

Low confidence (0.3-0.5):
- Significant estimation required
- Unclear scale or structure
- Missing labels

Below 0.3:
- Provide qualitative description only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Other Chart",

  "ocr_text": "All readable text extracted from the chart",

  "chart_type": "other",
  "chart_subtype": "radar | waterfall | funnel | gauge | bullet | other_specialized",

  "radar_data": {
    "axes": [
      {
        "variable": "Variable name",
        "scale": {"min": 0, "max": 100},
        "value": 75,
        "confidence": 0.9
      }
    ],
    "series": [
      {
        "series_label": "Series name",
        "values": [75, 80, 65, 90, 70]
      }
    ]
  },

  "waterfall_data": {
    "starting_value": 100,
    "changes": [
      {
        "label": "Increment 1",
        "change": 20,
        "direction": "increase | decrease",
        "running_total": 120
      }
    ],
    "ending_value": 150
  },

  "funnel_data": {
    "stages": [
      {
        "stage_name": "Stage 1",
        "value": 1000,
        "conversion_rate": 100.0,
        "drop_off": 0
      }
    ],
    "overall_conversion": 25.0
  },

  "gauge_data": {
    "current_value": 75,
    "scale_range": {"min": 0, "max": 100},
    "threshold_zones": [
      {
        "zone": "red | yellow | green",
        "range": {"min": 0, "max": 33}
      }
    ],
    "target": 80
  },

  "bullet_data": {
    "actual_value": 75,
    "target_value": 80,
    "qualitative_ranges": [
      {
        "range_label": "poor | satisfactory | good",
        "range": {"min": 0, "max": 50}
      }
    ],
    "comparative_measure": 70
  },

  "pattern_analysis": {
    "strengths": ["Variables with high values"],
    "weaknesses": ["Variables with low values"],
    "biggest_changes": ["Largest increments/decrements"],
    "biggest_dropoffs": ["Stages with largest conversion loss"],
    "performance_vs_target": "Description"
  },

  "key_insights": [
    "First insight about the visualization",
    "Second insight",
    "Third insight"
  ],

  "summary": "1-2 sentence summary of the main message",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Identify chart subtype before extraction
- Extract all values with confidence scores
- Set `approximate: true` when values are estimated
- Include key_insights and summary fields
