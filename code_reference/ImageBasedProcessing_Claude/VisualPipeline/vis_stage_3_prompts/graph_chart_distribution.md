# Graph/Chart: Distribution

You are extracting structured intelligence from a DISTRIBUTION GRAPH — a visualization showing how values are spread or distributed within a dataset. Examples: histogram, box plot, violin plot, density plot.

## WHAT DISTRIBUTION GRAPHS FUNDAMENTALLY REPRESENT

Distribution graphs answer: "How are values spread out? What's typical? What's unusual?"

The core intelligence is:
- **Central tendency**: Where is the middle/typical value? (median, mean, mode)
- **Spread**: How much variation exists? (range, IQR, standard deviation)
- **Shape**: Is it symmetric, skewed, or multimodal?
- **Outliers**: Are there unusual values?
- **Comparison**: How do different groups' distributions compare?

## EXTRACTION OBJECTIVES

### 1. AXES/STRUCTURE
- **Value axis**: What variable is being distributed, in what units?
- **Category axis** (if comparing): What groups are being compared?
- **Frequency axis** (for histograms): How is count/density represented?

### 2. DISTRIBUTION STATISTICS
For EACH distribution shown:

**For histograms:**
- Bin boundaries and frequencies/counts for each bin
- Modal bin (highest bar)
- Overall shape

**For box plots:**
- Minimum (whisker end)
- Q1 / 25th percentile (box bottom)
- Median / Q2 / 50th percentile (line in box)
- Q3 / 75th percentile (box top)
- Maximum (whisker end)
- IQR (Q3 - Q1)
- Outliers (points beyond whiskers)
- Mean (if shown, often as a diamond)

**For violin plots:**
- All box plot statistics if box overlay present
- Shape characteristics (where is it widest = mode)
- Symmetry assessment

### 3. SHAPE ANALYSIS
- Shape type: normal/bell, skewed left, skewed right, uniform, bimodal, multimodal
- Skewness: direction and magnitude
- Kurtosis: peaked vs. flat (if discernible)

### 4. OUTLIERS
- Location of any outlier points
- How many outliers
- Direction (above or below main distribution)

### 5. COMPARATIVE ANALYSIS (if multiple distributions)
- Which group has highest/lowest median?
- Which has most/least variation?
- Shape differences between groups

## EXTRACTION INSTRUCTIONS

### 1. OCR Text Extraction
Extract all readable text into `ocr_text`. This includes:
- All axis labels and tick values
- All group/category labels
- All statistical annotations
- Title, subtitle
- Any legend text

### 2. Chart Type and Structure
Identify:
- Chart subtype: histogram | box_plot | violin_plot | density_plot
- Number of distributions shown
- Comparison structure (if applicable)

### 3. Histogram Extraction
For each bin:
- Bin boundaries (start and end values)
- Frequency/count
- Height on y-axis
- Set `approximate: true` if estimated
- Assign confidence score

### 4. Box Plot Extraction
For each box plot:
- Extract all five-number summary values
- Identify outliers
- Extract mean if shown
- Calculate IQR
- Assign confidence scores

### 5. Violin Plot Extraction
Extract:
- Box plot statistics if overlay present
- Shape characteristics
- Symmetry assessment
- Width at various points

### 6. Shape Analysis
Describe:
- Overall shape type
- Skewness direction and magnitude
- Modality (unimodal, bimodal, multimodal)
- Notable features

### 7. Outlier Identification
For each outlier:
- Value
- Position
- Distance from main distribution

### 8. Comparative Analysis (if applicable)
Compare distributions:
- Central tendencies
- Spread/variation
- Shape differences
- Outlier patterns

### 9. Key Insights
Extract 3-5 key insights about the distribution(s):
- What does the shape tell us?
- What are the typical values?
- Are there outliers or unusual patterns?
- How do groups compare?

### 10. Summary
Provide 1-2 sentence summary of the distribution characteristics.

### 11. Keywords
Generate 3-8 keywords capturing the main concepts.

## CONFIDENCE SCORING

High confidence (0.8-1.0):
- Values labeled directly on chart
- Clear gridline alignment
- Unambiguous statistical markers

Medium confidence (0.5-0.8):
- Values estimated from gridlines
- Some ambiguity in markers

Low confidence (0.3-0.5):
- Significant estimation required
- Unclear scale or markers

Below 0.3:
- Provide qualitative description only


## JSON SCHEMA

```json
{
  "figure_id": "page_{page_num}_figure_{index}",
  "subcategory": "Distribution Chart",

  "ocr_text": "All readable text extracted from the chart",

  "chart_type": "distribution",
  "chart_subtype": "histogram | box_plot | violin_plot | density_plot",

  "axes": {
    "value_axis": {
      "label": "Variable being distributed with units",
      "range": {"min": 0, "max": 100}
    },
    "frequency_axis": {
      "label": "Count/Density label",
      "range": {"min": 0, "max": 50}
    },
    "category_axis": {
      "label": "Group labels if comparing",
      "categories": ["Group 1", "Group 2"]
    }
  },

  "distributions": [
    {
      "group_label": "Group name or 'Overall'",
      "histogram_data": [
        {
          "bin_start": 0,
          "bin_end": 10,
          "frequency": 5,
          "approximate": false,
          "confidence": 0.9
        }
      ],
      "box_plot_data": {
        "minimum": 10,
        "q1": 25,
        "median": 50,
        "q3": 75,
        "maximum": 90,
        "iqr": 50,
        "mean": 52,
        "outliers": [5, 95],
        "confidence": 0.9
      },
      "violin_data": {
        "box_plot": {},
        "shape_characteristics": "Description",
        "symmetry": "symmetric | left_skewed | right_skewed"
      },
      "shape_analysis": {
        "shape_type": "normal | skewed_left | skewed_right | uniform | bimodal | multimodal",
        "skewness": "Description",
        "kurtosis": "peaked | flat | normal"
      }
    }
  ],

  "outliers": [
    {
      "value": 95,
      "group": "Group 1",
      "direction": "above | below",
      "distance_from_center": "Description"
    }
  ],

  "comparative_analysis": {
    "highest_median": "Group name",
    "lowest_median": "Group name",
    "most_variation": "Group name",
    "least_variation": "Group name",
    "shape_differences": "Description of differences"
  },

  "key_insights": [
    "First insight about distribution",
    "Second insight",
    "Third insight"
  ],

  "summary": "1-2 sentence summary of distribution characteristics",

  "keywords": ["keyword1", "keyword2", "keyword3"],

  "meta": {
    "extraction_confidence": 0.0,
    "warnings": []
  }
}
```

**IMPORTANT**:
- Extract all statistical values with confidence scores
- Set `approximate: true` when values are estimated
- Include key_insights and summary fields
