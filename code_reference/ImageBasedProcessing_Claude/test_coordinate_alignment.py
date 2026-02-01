"""
Test coordinate alignment between YOLO and EasyOCR on the same image
"""

import cv2
import numpy as np
from ultralytics import YOLO
import easyocr

# Load models
print("Loading models...")
yolo_model = YOLO('yolov8m-doclaynet.pt')
ocr_reader = easyocr.Reader(['en'], gpu=False)

# Test on the same image
test_image = "DeepWalk/stage_1_screenshots/page_1_DeepWalk.png"
print(f"\nTesting on: {test_image}")

# Load image
img = cv2.imread(test_image)
if img is None:
    print(f"ERROR: Could not load {test_image}")
    exit(1)

img_h, img_w = img.shape[:2]
print(f"Image dimensions: {img_w}x{img_h}\n")

print("="*80)
print("YOLO DETECTIONS")
print("="*80)

# Run YOLO
yolo_results = yolo_model(img, conf=0.5, verbose=False)
yolo_boxes = yolo_results[0].boxes

print(f"Found {len(yolo_boxes)} objects\n")

yolo_detections = []
for i, box in enumerate(yolo_boxes):
    cls_id = int(box.cls[0])
    conf = float(box.conf[0])
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
    class_name = yolo_model.names[cls_id]

    detection = {
        'source': 'YOLO',
        'type': class_name,
        'bbox': {
            'x1': int(x1), 'y1': int(y1),
            'x2': int(x2), 'y2': int(y2)
        },
        'mid_x': int((x1 + x2) / 2),
        'mid_y': int((y1 + y2) / 2),
        'width': int(x2 - x1),
        'height': int(y2 - y1),
        'confidence': conf
    }
    yolo_detections.append(detection)

    print(f"[{i}] {class_name:15s} | "
          f"BBox: ({detection['bbox']['x1']:4d},{detection['bbox']['y1']:4d})-"
          f"({detection['bbox']['x2']:4d},{detection['bbox']['y2']:4d}) | "
          f"Size: {detection['width']:4d}x{detection['height']:4d} | "
          f"Conf: {conf:.3f}")

print("\n" + "="*80)
print("EASYOCR DETECTIONS")
print("="*80)

# Run EasyOCR
ocr_results = ocr_reader.readtext(img)

print(f"Found {len(ocr_results)} text blocks\n")

ocr_detections = []
for i, (bbox, text, conf) in enumerate(ocr_results[:20]):  # Limit to first 20 for display
    # Convert EasyOCR bbox to normalized format
    xs = [point[0] for point in bbox]
    ys = [point[1] for point in bbox]

    x1, x2 = int(min(xs)), int(max(xs))
    y1, y2 = int(min(ys)), int(max(ys))

    detection = {
        'source': 'EasyOCR',
        'type': 'Text',
        'text': text[:30],  # First 30 chars
        'bbox': {
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2
        },
        'mid_x': int((x1 + x2) / 2),
        'mid_y': int((y1 + y2) / 2),
        'width': x2 - x1,
        'height': y2 - y1,
        'confidence': conf
    }
    ocr_detections.append(detection)

    if i < 10:  # Show first 10
        print(f"[{i}] Text: \"{text[:20]:20s}\" | "
              f"BBox: ({x1:4d},{y1:4d})-({x2:4d},{y2:4d}) | "
              f"Size: {detection['width']:4d}x{detection['height']:4d} | "
              f"Conf: {conf:.3f}")

if len(ocr_results) > 10:
    print(f"... and {len(ocr_results) - 10} more text blocks")

print("\n" + "="*80)
print("COORDINATE SYSTEM ANALYSIS")
print("="*80)

# Check if coordinate systems align
print(f"\nImage coordinate system:")
print(f"  Origin: Top-left (0, 0)")
print(f"  Max coordinates: ({img_w}, {img_h})")

print(f"\nYOLO coordinate ranges:")
yolo_xs = [d['bbox']['x1'] for d in yolo_detections] + [d['bbox']['x2'] for d in yolo_detections]
yolo_ys = [d['bbox']['y1'] for d in yolo_detections] + [d['bbox']['y2'] for d in yolo_detections]
if yolo_xs and yolo_ys:
    print(f"  X range: {min(yolo_xs)} to {max(yolo_xs)} (image width: {img_w})")
    print(f"  Y range: {min(yolo_ys)} to {max(yolo_ys)} (image height: {img_h})")

print(f"\nEasyOCR coordinate ranges:")
ocr_xs = [d['bbox']['x1'] for d in ocr_detections] + [d['bbox']['x2'] for d in ocr_detections]
ocr_ys = [d['bbox']['y1'] for d in ocr_detections] + [d['bbox']['y2'] for d in ocr_detections]
if ocr_xs and ocr_ys:
    print(f"  X range: {min(ocr_xs)} to {max(ocr_xs)} (image width: {img_w})")
    print(f"  Y range: {min(ocr_ys)} to {max(ocr_ys)} (image height: {img_h})")

# Check for overlaps (text inside figures)
print("\n" + "="*80)
print("OVERLAP ANALYSIS")
print("="*80)

for yolo_det in yolo_detections:
    if yolo_det['type'] not in ['Picture', 'Table']:
        continue

    overlapping_text = []
    for ocr_det in ocr_detections:
        # Check if OCR text center is inside YOLO bbox
        if (yolo_det['bbox']['x1'] <= ocr_det['mid_x'] <= yolo_det['bbox']['x2'] and
            yolo_det['bbox']['y1'] <= ocr_det['mid_y'] <= yolo_det['bbox']['y2']):
            overlapping_text.append(ocr_det)

    print(f"\n{yolo_det['type']} at ({yolo_det['mid_x']}, {yolo_det['mid_y']}):")
    print(f"  Size: {yolo_det['width']}x{yolo_det['height']}")
    print(f"  Contains {len(overlapping_text)} text blocks")

    if overlapping_text:
        for txt in overlapping_text[:3]:  # Show first 3
            print(f"    - \"{txt['text'][:40]}\"")

# Create visualization
print("\n" + "="*80)
print("CREATING VISUALIZATION")
print("="*80)

vis_img = img.copy()

# Draw YOLO detections in green
for det in yolo_detections:
    if det['type'] in ['Picture', 'Table']:
        bbox = det['bbox']
        cv2.rectangle(vis_img, (bbox['x1'], bbox['y1']),
                     (bbox['x2'], bbox['y2']), (0, 255, 0), 3)
        cv2.putText(vis_img, f"YOLO: {det['type']}",
                   (bbox['x1'], bbox['y1']-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# Draw EasyOCR detections in blue (sample - every 5th to avoid clutter)
for i, det in enumerate(ocr_detections):
    if i % 5 == 0:  # Show every 5th to reduce clutter
        bbox = det['bbox']
        cv2.rectangle(vis_img, (bbox['x1'], bbox['y1']),
                     (bbox['x2'], bbox['y2']), (255, 0, 0), 1)

output_path = "coordinate_alignment_test.png"
cv2.imwrite(output_path, vis_img)
print(f"\nVisualization saved to: {output_path}")
print("  Green boxes = YOLO detections")
print("  Blue boxes = EasyOCR text blocks (sampled)")

print("\n" + "="*80)
print("ALIGNMENT CONCLUSION")
print("="*80)

# Test if both use same coordinate system
yolo_in_bounds = all(0 <= d['bbox']['x1'] <= img_w and
                     0 <= d['bbox']['y1'] <= img_h and
                     0 <= d['bbox']['x2'] <= img_w and
                     0 <= d['bbox']['y2'] <= img_h
                     for d in yolo_detections)

ocr_in_bounds = all(0 <= d['bbox']['x1'] <= img_w and
                    0 <= d['bbox']['y1'] <= img_h and
                    0 <= d['bbox']['x2'] <= img_w and
                    0 <= d['bbox']['y2'] <= img_h
                    for d in ocr_detections)

print(f"\nYOLO detections within image bounds: {'✅ YES' if yolo_in_bounds else '❌ NO'}")
print(f"EasyOCR detections within image bounds: {'✅ YES' if ocr_in_bounds else '❌ NO'}")

if yolo_in_bounds and ocr_in_bounds:
    print("\n✅ CONCLUSION: Both tools use the same pixel coordinate system!")
    print("   Coordinates can be directly compared for reading order sorting.")
else:
    print("\n⚠️ WARNING: Coordinate systems may differ!")
    print("   Further investigation needed.")

print("\n" + "="*80)
