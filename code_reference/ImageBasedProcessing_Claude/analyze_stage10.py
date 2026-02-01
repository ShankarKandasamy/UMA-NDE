"""Detailed analysis of stage 10 vertical stacking results"""
import json

# Load original
with open('DeepWalk/stage_8_horizontal_buckets/page_1_horizontal_buckets.json', 'r', encoding='utf-8') as f:
    original = json.load(f)

# Load reordered
with open('DeepWalk/stage_10_vertical_stacked/page_1_vertical_stacked.json', 'r', encoding='utf-8') as f:
    reordered = json.load(f)

# Create mapping from original to new position
orig_to_new = {}
for new_idx, new_bucket in enumerate(reordered['horizontal_buckets']):
    # Find matching bucket in original by comparing y-coordinates and text
    new_text = new_bucket['vertical_buckets'][0]['blocks'][0]['text']
    new_y = new_bucket['start_y']

    for orig_idx, orig_bucket in enumerate(original['horizontal_buckets']):
        orig_text = orig_bucket['vertical_buckets'][0]['blocks'][0]['text']
        orig_y = orig_bucket['start_y']

        if orig_text == new_text and orig_y == new_y:
            orig_to_new[orig_idx] = new_idx
            break

print('VERTICAL STACKING ANALYSIS (Page 1):')
print('=' * 100)
print(f'{"Orig":<5} {"New":<5} {"Move":<6} {"Y-Range":<15} {"X-Range":<18} {"Text Sample":<30}')
print('-' * 100)

for orig_idx in range(len(original['horizontal_buckets'])):
    new_idx = orig_to_new[orig_idx]

    bucket = original['horizontal_buckets'][orig_idx]
    text = bucket['vertical_buckets'][0]['blocks'][0]['text'][:30]

    y_range = f"{bucket['start_y']}-{bucket['end_y']}"
    x_range = f"{bucket['start_x']}-{bucket['end_x']}"

    move = f"{orig_idx}->{new_idx}"
    if orig_idx == new_idx:
        move = "  -  "

    marker = "**" if orig_idx != new_idx else "  "

    print(f'{marker}{orig_idx:<5} {new_idx:<5} {move:<6} {y_range:<15} {x_range:<18} {text}')

print()
print('COLUMN GROUPING ANALYSIS:')
print('=' * 100)

# Identify sequences in new order
print("\nReading order after vertical stacking:")
print('-' * 100)

for new_idx, bucket in enumerate(reordered['horizontal_buckets']):
    text = bucket['vertical_buckets'][0]['blocks'][0]['text'][:50]
    y_range = f"{bucket['start_y']}-{bucket['end_y']}"
    x_range = f"{bucket['start_x']}-{bucket['end_x']}"

    print(f'{new_idx:2d}. y={y_range:12s} x={x_range:15s} | {text}')
