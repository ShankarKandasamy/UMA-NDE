# VLM Chart Data Extraction Benchmark Report

**Date:** December 16, 2024  
**Purpose:** Evaluate Vision Language Models for accurate chart data extraction  
**Test Images:** Farm Financial Health report charts

---

## Executive Summary

We evaluated multiple Vision Language Models on their ability to accurately extract numerical data from charts. **Claude Opus 4.5** emerged as the most versatile and accurate model, with **Qwen3-VL-235B** as a strong open-source alternative.

| Model                | Provider           | Overall Rating   | Best For                |
| -------------------- | ------------------ | ---------------- | ----------------------- |
| **Claude Opus 4.5**  | Anthropic          | 🥇 **Best**      | All chart types         |
| **Qwen3-VL-235B**    | Fireworks          | 🥇 **Excellent** | Line charts, bar charts |
| **Qwen3-VL-32B**     | Together/Fireworks | 🥈 **Very Good** | Multi-series charts     |
| **Llama 4 Maverick** | Together           | 🥉 **Good**      | Simple line charts      |
| **Gemma 3 27B**      | Replicate          | ⚠️ **Limited**   | Rough estimates only    |

---

## Test Methodology

### Test Images

1. **2-Series Line Chart** (`page_8_image_0.png`) - CPI vs Farm Land Value % Change (1999-2022)
2. **Grouped Bar Chart** (`page_8_image_1.png`) - Land Value by Canadian Province (2020-2022)
3. **4-Series Line Chart** (`page_14_image_0.png`) - Industry Purchase Index (Quarterly, 2019-2023)

### Key Metrics

- **Accuracy:** How close extracted values are to known/visible values
- **Completeness:** Whether all data series and points are captured
- **Token Efficiency:** Tokens used per extraction

---

## Detailed Results

### Test 1: 2-Series Line Chart (CPI & Farm Land Value)

**Key Reference Points:**

- Farm Land 2013 Peak: ~0.22 (22%)
- CPI 2009 Trough: ~0.005 (0.5%)

| Model                | Farm Land Peak | Peak Year   | CPI Trough | Deflections | Tokens |
| -------------------- | -------------- | ----------- | ---------- | ----------- | ------ |
| **Claude Opus 4.5**  | **0.22** ✅    | **2013** ✅ | 0.005 ✅   | 24/24       | 3,750  |
| **Qwen3-VL-235B**    | **0.22** ✅    | **2013** ✅ | 0.005 ✅   | 24-25       | 3,187  |
| **Qwen3-VL-32B**     | 0.21           | 2012        | 0.0 ✅     | 22/22       | 4,096  |
| **Llama 4 Maverick** | **0.225** ✅   | **2013** ✅ | 0.005 ✅   | 13-14       | 3,835  |
| **Gemma 3 27B**      | 0.22 ✅        | **2011** ❌ | 0.01 ❌    | 23-24       | ~2,500 |

**Winner:** Tie between Claude Opus 4.5, Qwen3-VL-235B, and Llama 4 Maverick

**Note on Gemma 3 27B:** Correctly identified peak VALUE (0.22) but assigned it to wrong YEAR (2011 instead of 2013). CPI values were inflated (0.01-0.08 instead of 0.005-0.065).

---

### Test 2: Grouped Bar Chart (Provincial Land Values)

**Key Reference Point:**

- Ontario 2022: $17,962 (stated in chart annotation)

| Model                | Ontario 2022 | Error       | Provinces Found | Tokens |
| -------------------- | ------------ | ----------- | --------------- | ------ |
| **Claude Opus 4.5**  | **$17,962**  | **0.0%** ✅ | 10/10           | 2,177  |
| **Qwen3-VL-235B**    | $18,000      | **0.2%** ✅ | 10/10           | 1,609  |
| **Qwen3-VL-32B**     | $17,000      | 5.4%        | 10/10           | 2,273  |
| **Llama 4 Maverick** | $16,000      | 10.9%       | 10/10           | 2,888  |
| **Gemma 3 27B**      | **$17,962**  | **0.0%** ✅ | 10/10           | ~1,500 |

**Winner:** Claude Opus 4.5 (exact match), Qwen3-VL-235B (close second)

**Note on Gemma 3 27B:** Correctly read Ontario 2022 from text annotation ($17,962), but misassigned the 2019 annotation value ($11,786) to the 2020 column. Read text well, but confused year assignments.

---

### Test 3: 4-Series Quarterly Line Chart (Industry Purchase Index)

**Key Reference Points:**

- Green (Crop) 2023 Q1 Peak: ~130
- Red (Machinery) 2021 Q2 Trough: ~99
- All 4 series should be identified

| Model                | Series Found | Crop Peak  | Machinery Trough | Distinct Values  |
| -------------------- | ------------ | ---------- | ---------------- | ---------------- |
| **Claude Opus 4.5**  | **4/4** ✅   | **130** ✅ | **99** ✅        | Yes ✅           |
| **Qwen3-VL-235B**    | 0/4\*        | N/A        | N/A              | N/A              |
| **Qwen3-VL-32B**     | **4/4** ✅   | 128        | 99.5 ✅          | No (3 identical) |
| **Llama 4 Maverick** | 2/4 ❌       | 132        | N/A              | Yes              |

\*Qwen3-VL-235B correctly refused because prompt asked for specific series not in chart.

**Winner:** Claude Opus 4.5

---

## Model Profiles

### Claude Opus 4.5 (Anthropic)

- **Strengths:** Most accurate across all chart types, reads text annotations, handles complex multi-series charts
- **Weaknesses:** Highest cost, proprietary
- **Best Use Case:** Production systems requiring highest accuracy
- **Cost:** ~$15/M input, $75/M output tokens

### Qwen3-VL-235B (Fireworks)

- **Strengths:** Matches Claude on structured extraction, efficient token usage, open-source
- **Weaknesses:** Follows prompts very literally (may refuse if series names don't match)
- **Best Use Case:** Cost-effective alternative for known chart formats
- **Cost:** ~$0.90/M input, $0.90/M output tokens

### Qwen3-VL-32B (Together/Fireworks)

- **Strengths:** Identifies all series in complex charts, good balance of cost/accuracy
- **Weaknesses:** Slightly compressed values, sometimes gives identical values for similar series
- **Best Use Case:** General-purpose chart extraction at lower cost
- **Cost:** ~$0.20/M input, $0.20/M output tokens

### Llama 4 Maverick (Together)

- **Strengths:** Excellent on simple line charts, good peak/trough detection
- **Weaknesses:** Struggles with bar charts (10.9% error), misses series in complex charts
- **Best Use Case:** Simple 2-series line charts
- **Cost:** ~$0.27/M input, $0.85/M output tokens

### Gemma 3 27B (Replicate)

- **Strengths:** Reads text annotations correctly, extracts exact values when visible in text
- **Weaknesses:** Misassigns years (placed 2013 peak at 2011), confuses annotation values between years, inflated CPI values
- **Best Use Case:** Not recommended for precise extraction; may work for rough estimates
- **Cost:** ~$0.05/run on Replicate
- **Note:** The smaller Gemma 3 4B performed significantly worse (hallucinated values entirely)

---

## Recommendations

### For Production Use:

1. **Highest Accuracy Required:** Claude Opus 4.5
2. **Cost-Sensitive with Good Accuracy:** Qwen3-VL-235B
3. **Budget Option:** Qwen3-VL-32B

### For Specific Chart Types:

- **Line Charts (2 series):** Any of the top 4 models
- **Bar Charts:** Claude Opus 4.5 or Qwen3-VL-235B
- **Multi-Series Charts (3+ series):** Claude Opus 4.5 or Qwen3-VL-32B

### Models NOT Recommended for Chart Extraction:

- **GPT-4o:** Missed key features (2013 peak), only 12 deflection points
- **GPT-4o-mini:** Hallucinated values, excessive tokens
- **DeepSeek-VL2:** Generated fabricated linear data
- **LLaMA 3.2 Vision 90B:** Hallucinated data patterns
- **Ministral 3 14B:** Too small, generated micro-deflections
- **Gemma 3 4B:** Too small, hallucinated values entirely
- **Gemma 3 27B:** Misassigns years, confuses annotation values (use with caution)

---

## Conclusion

For chart data extraction tasks, **Claude Opus 4.5 provides the best overall accuracy** across all chart types, correctly reading both visual gridlines and text annotations. **Qwen3-VL-235B is an excellent open-source alternative** that matches Claude's accuracy on structured extraction tasks at a fraction of the cost.

For teams with budget constraints, **Qwen3-VL-32B** offers a good balance of accuracy and cost, while **Llama 4 Maverick** is suitable for simpler line chart extractions.

---

_Report generated from testing conducted on December 16, 2024_
