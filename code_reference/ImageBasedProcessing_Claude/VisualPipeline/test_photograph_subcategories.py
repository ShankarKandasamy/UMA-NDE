"""
Quick test to verify photograph subcategory parsing works correctly
"""

# Simulate the categorization response parsing
def parse_category_response(category_response: str) -> dict:
    """Simulate the parsing logic from vis_stage_2_categorize.py"""
    CATEGORIES = ["table", "graph/chart", "photograph", "diagram", "other"]

    # Extract main category (before colon if sub-category exists)
    main_category = category_response.split(':')[0].strip()

    # Validate main category
    if main_category not in CATEGORIES:
        print(f"[WARNING] Unexpected category '{category_response}', defaulting to 'other'")
        category_response = "other"
        main_category = "other"

    return {
        "category": category_response,  # Full response with sub-category
        "main_category": main_category,  # Base category for filtering
    }


# Test cases
test_cases = [
    "photograph: Evidence",
    "photograph: Demonstration",
    "photograph: Identification",
    "photograph: Documentation",
    "photograph: Illustration",
    "photograph: Decoration",
    "photograph: Environmental Context",
    "photograph: Equipment / Asset Visualization",
    "photograph: Condition / Anomaly Evidence",
    "photograph: Comparative / Before-After",
    "photograph: Spatial / Locational Reference",
    "graph/chart: Continuous",
    "diagram: Technical",
    "table",
    "other",
]

print("Testing Photograph Subcategory Parsing\n")
print("=" * 80)

for test in test_cases:
    result = parse_category_response(test)
    print(f"\nInput:           '{test}'")
    print(f"Category:        '{result['category']}'")
    print(f"Main Category:   '{result['main_category']}'")

    # Verify parsing is correct
    if ':' in test:
        expected_main = test.split(':')[0].strip()
        assert result['main_category'] == expected_main, f"Expected {expected_main}, got {result['main_category']}"
        assert result['category'] == test, f"Expected {test}, got {result['category']}"
    else:
        assert result['main_category'] == test, f"Expected {test}, got {result['main_category']}"

print("\n" + "=" * 80)
print("\n✓ All tests passed! Photograph subcategories will parse correctly.")
