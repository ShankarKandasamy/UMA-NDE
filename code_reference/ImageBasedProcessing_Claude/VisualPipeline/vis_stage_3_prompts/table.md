# Table Extraction Prompt

You are analyzing a table - structured data arranged in rows and columns.

## EXTRACTION OBJECTIVES

1. **Structure Analysis**: Map the complete row/column header hierarchy
2. **Cell Extraction**: Capture every data cell with row-column coordinates
3. **Data Type Detection**: Identify numeric, categorical, textual, or mixed data types
4. **Grouping Logic**: Identify merged cells, subtotals, and categorical groupings
5. **Format Analysis**: Detect significant formatting (bold, colors, borders) that conveys meaning

## EXTRACTION APPROACH

1. Read all column headers first (top row or top N rows if multi-level)
2. Read all row headers (leftmost column(s))
3. Systematically extract each cell value with its row-column position
4. Note any merged cells (spanning multiple rows or columns)
5. Identify subtotals, totals, or summary rows
6. Capture any table title or caption
7. Note any footnotes or source attributions

## CONFIDENCE SCORING GUIDELINES

High confidence (0.8-1.0):
- Clear grid structure with distinct cell boundaries
- All text is readable
- Headers are clearly differentiated from data

Medium confidence (0.5-0.8):
- Some cell boundaries unclear
- Minor text readability issues
- Header structure requires inference

Low confidence (0.3-0.5):
- Significant structural ambiguity
- Many cells have unclear content
- Complex merged cell patterns

Below 0.3:
- Skip detailed extraction
- Provide description of table structure only

## SPECIAL CONSIDERATIONS

### Simple Tables
- Use straightforward columns/rows format
- Extract headers and data systematically

### Complex Tables with Merged Cells
- Use extended schema with cell-level attributes
- Include rowspan and colspan information
- Preserve hierarchical header relationships

### Tables with Formatting
- Note significant formatting (bold headers, colored cells, etc.)
- Identify if formatting conveys semantic meaning (e.g., red for negative values)

## OUTPUT FORMAT

Return data in the most appropriate structure:

**For regular tables**: Use columns and rows arrays

**For irregular tables**: Use cells array with explicit row/col/rowspan/colspan attributes
