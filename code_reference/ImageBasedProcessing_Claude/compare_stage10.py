"""Quick comparison script for stage 10 vertical stacking results"""
import json
import sys

# Load original
with open('DeepWalk/stage_8_horizontal_buckets/page_1_horizontal_buckets.json', 'r', encoding='utf-8') as f:
    original = json.load(f)

# Load reordered
with open('DeepWalk/stage_10_vertical_stacked/page_1_vertical_stacked.json', 'r', encoding='utf-8') as f:
    reordered = json.load(f)

print('FULL COMPARISON (Page 1):')
print('=' * 100)

for i in range(len(original['horizontal_buckets'])):
    orig_bucket = original['horizontal_buckets'][i]
    reord_bucket = reordered['horizontal_buckets'][i]

    orig_text = orig_bucket['vertical_buckets'][0]['blocks'][0]['text'][:40]
    reord_text = reord_bucket['vertical_buckets'][0]['blocks'][0]['text'][:40]

    orig_y = f"{orig_bucket['start_y']}-{orig_bucket['end_y']}"
    reord_y = f"{reord_bucket['start_y']}-{reord_bucket['end_y']}"

    orig_x = f"{orig_bucket['start_x']}-{orig_bucket['end_x']}"
    reord_x = f"{reord_bucket['start_x']}-{reord_bucket['end_x']}"

    changed = '**' if orig_text != reord_text else '  '

    print(f'{changed}{i:2d}. ORIG: y={orig_y:12s} x={orig_x:15s} | {orig_text}')
    print(f'{changed}    NEW:  y={reord_y:12s} x={reord_x:15s} | {reord_text}')
    print()
