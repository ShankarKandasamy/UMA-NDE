# Stage Renaming Summary

## Changes Made

### Stage 9: Vertical Column Stacking (NEW)
**Old name**: `stage_10_llm_reorder.py`
**New name**: `stage_9_vertical_stacking.py`

**Purpose**: Groups vertically-aligned horizontal buckets for proper column reading order

**Input**: Stage 8 horizontal buckets
**Output**: Vertically-stacked buckets in reading order

**Key changes**:
- All references to "Stage 10" → "Stage 9"
- All references to "llm_reorder" → "vertical_stacking"
- No functional changes, just renaming

### Stage 10: LLM Context Chunks (RENAMED)
**Old name**: `stage_9_llm_context_chunks.py`
**New name**: `stage_10_llm_context_chunks.py`

**Purpose**: Converts bucket structure to simplified LLM-ready format

**Input**: Stage 9 vertical stacked buckets (CHANGED from Stage 8)
**Output**: Simplified JSON for LLM processing

**Key changes**:
- All references to "Stage 9" → "Stage 10"
- Input changed from Stage 8 → Stage 9
- Now processes `*_vertical_stacked.json` files (instead of `*_horizontal_buckets.json`)
- Uses normalized coordinates directly from Stage 9 (already 0-100 scale)
- Updated `derive_position()` and `derive_width_category()` to work with normalized coords
- Removed `calculate_page_dimensions()` - no longer needed with normalized coords
- Updated `calculate_y_groups()` tolerance from 50px → 5% (normalized scale)

## Updated Pipeline Flow

```
Stage 7: Vertical Buckets (raw pixels)
    ↓
Stage 8: Horizontal Buckets
    - Groups vertical buckets
    - Normalizes coordinates (0-100%)
    - Outputs: raw + normalized coordinates
    ↓
Stage 9: Vertical Column Stacking ← NEW POSITION
    - Groups vertically-aligned buckets
    - Re-orders for column reading flow
    - Preserves normalized coordinates
    ↓
Stage 10: LLM Context Chunks ← NEW INPUT SOURCE
    - Simplifies bucket structure
    - Uses normalized coordinates
    - Outputs LLM-ready JSON
```

## Testing Results

**Test Document**: DeepWalk.pdf (2 pages)

### Stage 9 Output:
- Page 1: 19 buckets (re-ordered from Stage 8)
- Page 2: 4 buckets (re-ordered from Stage 8)
- Column detection: ✓ Working (left column grouped correctly)

### Stage 10 Output:
- Page 1: 19 buckets, 108 texts, 4,524 chars
- Page 2: 4 buckets, 118 texts, 5,983 chars
- Normalized coordinates: ✓ Working (0-100 scale)
- Position/width derivation: ✓ Working with normalized coords

## Files to Remove (Old Versions)

After confirming the new stages work correctly, you can safely remove:
- `stage_10_llm_reorder.py` (replaced by `stage_9_vertical_stacking.py`)
- `stage_9_llm_context_chunks.py` (replaced by `stage_10_llm_context_chunks.py`)

## Why This Makes Sense

**Better Logical Flow**:
1. Stage 9 improves reading order → Should come before LLM processing
2. Stage 10 prepares for LLM → Should use the improved reading order

**Clearer Pipeline**:
- Stages 1-9: Document structure extraction and ordering
- Stage 10: LLM preparation (final transformation before AI processing)

## Compatibility Notes

**Breaking change**: Any code that directly calls `stage_9_llm_context_chunks.py` or `stage_10_llm_reorder.py` needs to be updated.

**Data compatibility**: Old Stage 9 output (`*_llm_ready.json` from Stage 8) will differ from new Stage 10 output (from Stage 9), because:
- New version has better reading order (from vertical stacking)
- Uses normalized coordinates directly (cleaner implementation)

## Summary

✅ **Stage 9 renamed and tested** - Vertical column stacking working
✅ **Stage 10 renamed and tested** - LLM context chunks working
✅ **Pipeline flow improved** - Logical sequence maintained
✅ **Normalized coordinates** - Used throughout Stages 8-10
✅ **Ready for Stage 10 development** - Can now return to LLM context chunk improvements
