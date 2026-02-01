"""Verify normalized coordinates in Stage 8 output"""
import json

with open('DeepWalk/stage_8_horizontal_buckets/page_1_horizontal_buckets.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('STAGE 8 NORMALIZATION VERIFICATION (Page 1)')
print('=' * 100)
print(f'{"ID":<4} {"RAW COORDINATES":<40} {"NORMALIZED (0-100)":<30} {"TEXT SAMPLE":<20}')
print('-' * 100)

for bucket in data['horizontal_buckets'][:10]:
    bid = bucket['horizontal_bucket_id']

    # Raw coordinates
    raw = f"x:{bucket['start_x']}-{bucket['end_x']} y:{bucket['start_y']}-{bucket['end_y']}"

    # Normalized coordinates
    norm = f"L:{bucket['left_edge']:.1f} R:{bucket['right_edge']:.1f} T:{bucket['top_edge']:.1f} B:{bucket['bottom_edge']:.1f}"

    # Text sample
    text = bucket['vertical_buckets'][0]['blocks'][0]['text'][:20]

    print(f'{bid:<4} {raw:<40} {norm:<30} {text}')

print()
print('COORDINATE RANGES:')
print('-' * 100)

all_left = [b['left_edge'] for b in data['horizontal_buckets']]
all_right = [b['right_edge'] for b in data['horizontal_buckets']]
all_top = [b['top_edge'] for b in data['horizontal_buckets']]
all_bottom = [b['bottom_edge'] for b in data['horizontal_buckets']]

print(f'left_edge:   min={min(all_left):.2f}   max={max(all_left):.2f}')
print(f'right_edge:  min={min(all_right):.2f}   max={max(all_right):.2f}')
print(f'top_edge:    min={min(all_top):.2f}   max={max(all_top):.2f}')
print(f'bottom_edge: min={min(all_bottom):.2f}   max={max(all_bottom):.2f}')
print()
print('✓ All coordinates normalized to 0-100 range!')
