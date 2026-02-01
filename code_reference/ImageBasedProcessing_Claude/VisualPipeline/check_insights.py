import json
from pathlib import Path

# Load metadata
metadata_file = Path("Farm Financial Health/stage_3_analysis/stage_3_analysis_metadata.json")
with open(metadata_file) as f:
    data = json.load(f)

# Find graph analyses
graphs = [(p['page_number'], d) for p in data['pages']
          for d in p['detections']
          if 'graph/chart' in d.get('category', '') and 'visual_analysis' in d]

print(f"Found {len(graphs)} graph analyses\n")

if graphs:
    page_num, detection = graphs[0]
    va = detection['visual_analysis']

    print(f"Page {page_num}")
    print(f"Category: {detection['category']}")
    print(f"\nKeys in visual_analysis: {list(va.keys())}")
    print(f"\nHas key_insights: {'key_insights' in va}")
    print(f"Has overall_trends: {'overall_trends' in va}")

    if 'key_insights' in va:
        print("\n" + "="*80)
        print("KEY INSIGHTS")
        print("="*80)
        for i, insight in enumerate(va['key_insights'], 1):
            print(f"{i}. {insight}")

        print("\n" + "="*80)
        print("OVERALL TRENDS")
        print("="*80)
        print(va['overall_trends'])

        print("\n" + "="*80)
        print(f"Model used: {va.get('_stage3_meta', {}).get('model', 'unknown')}")
        print(f"Tokens: {va.get('_stage3_meta', {}).get('total_tokens', 0):,}")
    else:
        print("\nNo key_insights found. Visual analysis keys:", list(va.keys()))
