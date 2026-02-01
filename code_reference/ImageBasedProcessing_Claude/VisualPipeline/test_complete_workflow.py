"""
Complete workflow test: Stage 2 → Stage 3
Demonstrates full pipeline from categorization to extraction
"""

from vis_stage_3_prompt_manager import get_prompt_for_category, list_supported_categories

# Simulate Stage 2 categorization results
stage_2_results = [
    {"image": "chart_1.png", "category": "graph/chart: Continuous"},
    {"image": "chart_2.png", "category": "graph/chart: Categorical"},
    {"image": "photo_1.png", "category": "photograph: Evidence"},
    {"image": "photo_2.png", "category": "photograph: Equipment / Asset Visualization"},
    {"image": "photo_3.png", "category": "photograph: Condition / Anomaly Evidence"},
    {"image": "photo_4.png", "category": "photograph: Documentation"},
    {"image": "table_1.png", "category": "table"},
    {"image": "diagram_1.png", "category": "diagram: Technical"},
]

print("=" * 80)
print("COMPLETE WORKFLOW TEST: Stage 2 -> Stage 3")
print("=" * 80)

print("\n1. Stage 2 Categorization Results:")
print("-" * 80)
for result in stage_2_results:
    print(f"  {result['image']:20s} -> {result['category']}")

print("\n2. Stage 3 Prompt Selection:")
print("-" * 80)

supported_count = 0
unsupported_count = 0

for result in stage_2_results:
    category = result['category']
    prompt_data = get_prompt_for_category(category)

    if prompt_data:
        supported_count += 1
        print(f"\n  [OK] {result['image']} ({category})")
        print(f"       Category Type: {prompt_data['category_type']}")
        print(f"       Subcategory: {prompt_data['subcategory']}")
        print(f"       System Prompt: {len(prompt_data['system_prompt'])} chars")
        print(f"       User Prompt: {len(prompt_data['user_prompt'])} chars")
        print(f"       Schema Fields: {len(prompt_data['schema'])} top-level keys")
    else:
        unsupported_count += 1
        print(f"\n  [SKIP] {result['image']} ({category})")
        print(f"         Status: Not yet supported in Stage 3")

print("\n3. Coverage Summary:")
print("-" * 80)
print(f"  Supported: {supported_count}/{len(stage_2_results)} images")
print(f"  Unsupported: {unsupported_count}/{len(stage_2_results)} images")
print(f"  Coverage: {(supported_count/len(stage_2_results))*100:.1f}%")

print("\n4. Supported Categories:")
print("-" * 80)
categories = list_supported_categories()
for cat_type, subcats in categories.items():
    print(f"\n  {cat_type}: {len(subcats)} subcategories")
    for subcat in subcats:
        print(f"    - {subcat}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
