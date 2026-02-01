"""
Extract text from missing buckets reported by Stage 11
"""
import json
from pathlib import Path

# Missing buckets per page
missing_buckets = {
    1: [2, 4, 8, 9, 10, 11, 12, 13, 15, 16, 18],
    3: [11, 13, 18, 19, 20, 22],
    4: [1, 4, 5, 6, 9, 10],
    5: [0, 1, 2, 9, 10, 11, 12, 13, 16, 17, 18],
    6: [4, 8],
    7: [18, 19, 20, 21, 22, 23, 25, 26, 27, 32, 33, 34, 35, 39, 41, 42],
    8: [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 22, 24, 26, 27, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 45, 46, 47, 52, 53, 54, 55, 56, 58, 59, 60, 64, 67, 68, 71],
    9: [0, 1, 13, 14]
}

base_dir = Path("DeepWalk/stage_10_llm_chunks")

output = []
output.append("=" * 80)
output.append("MISSING BUCKET TEXT CONTENT")
output.append("=" * 80)
output.append("")

for page_num, bucket_ids in missing_buckets.items():
    json_file = base_dir / f"page_{page_num}_llm_ready.json"

    with open(json_file, 'r', encoding='utf-8') as f:
        page_data = json.load(f)

    output.append(f"PAGE {page_num} ({len(bucket_ids)} missing buckets)")
    output.append("=" * 80)
    output.append("")

    for bucket_id in bucket_ids:
        # Find the bucket
        bucket = next((b for b in page_data['buckets'] if b['id'] == bucket_id), None)
        if bucket:
            texts = bucket['texts']
            text_content = '\n'.join(texts)

            output.append(f"Bucket {bucket_id}:")
            output.append(f"  Position: {bucket['position']}")
            output.append(f"  Width: {bucket['width_category']}")
            output.append(f"  Y-Group: {bucket['y_group_id']}")
            output.append(f"  Chars: {bucket['char_count']}")
            output.append(f"  Text:")
            for text_line in texts:
                output.append(f"    {text_line}")
            output.append("")

    output.append("")

# Write output
output_file = Path("DeepWalk/missing_buckets_text.txt")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"Extracted missing bucket text to: {output_file}")
print(f"Total missing buckets: {sum(len(b) for b in missing_buckets.values())}")
