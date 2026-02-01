# Prompt Cleanup Summary

## Changes Made

### Removed Redundant Output Instructions

**From ALL category-specific prompts:**
- ❌ Removed: "Return ONLY valid JSON matching the schema below"
- ❌ Removed: "Return ONLY valid JSON matching the schema"  
- ❌ Removed: Empty "## OUTPUT REQUIREMENTS" headers

**Why:** These generic output formatting instructions are now handled by the universal `OUTPUT_PROMPT` in `stage_4_visual_analysis.py`.

---

## What Was Kept (Category-Specific)

### ✅ JSON Schemas
All category-specific JSON schemas remain intact:
- Field definitions and data types
- Required vs optional fields
- Nested object structures
- Enum values and constraints

### ✅ Category-Specific Output Guidance
Examples of preserved category-specific instructions:

**table.md:**
```
## OUTPUT FORMAT

Return data in the most appropriate structure:

**For regular tables**: Use columns and rows arrays
**For irregular tables**: Use cells array with explicit row/col/rowspan/colspan attributes
```

**graph_chart_continuous.md:**
```
**IMPORTANT**:
- Extract Y-value for EVERY discernible X-value
- Use gridlines as reference for estimation
- Assign confidence scores for all data points
- Include key_insights and summary fields
```

---

## Result

**Before:**
```
[Category-specific instructions]
...
## OUTPUT REQUIREMENTS
Return ONLY valid JSON matching the schema below.

## JSON SCHEMA
{...}
```

**After:**
```
[Category-specific instructions]
...
## JSON SCHEMA
{...}
```

The universal output requirements are now prepended via `OUTPUT_PROMPT`:
```python
final_prompt = GENERAL_PROMPT + category_prompt + OUTPUT_PROMPT
```

---

## Files Affected

All prompt files in `vis_stage_3_prompts/`:
- ✓ diagram_*.md (4 files)
- ✓ graph_chart_*.md (6 files)
- ✓ other_*.md (7 files)
- ✓ photograph_*.md (10 files)
- ✓ table.md (1 file)

**Total: 28 prompt files cleaned**

---

## Benefits

1. **Single Source of Truth**: Output formatting rules in one place (`OUTPUT_PROMPT`)
2. **Consistency**: All images get same JSON formatting instructions
3. **Maintainability**: Update output requirements once, applies to all categories
4. **Clarity**: Category prompts focus on extraction logic, not formatting
5. **Reduced Redundancy**: ~28 duplicate instructions removed

