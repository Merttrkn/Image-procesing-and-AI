import cv2
import numpy as np
from ultralytics import YOLO
import os

# Yol ayarları
model_path = r"C:\Users\Mert\Desktop\yolo\runs\detect\train26\weights\best.pt"
source = r"C:\Users\Mert\Desktop\test\images"
label_path = r"C:\Users\Mert\Desktop\test\labels"
output_dir = r"C:\Users\Mert\Desktop\test\results"
os.makedirs(output_dir, exist_ok=True)

# YOLO modeli
model = YOLO(model_path)

# Renk paleti
color_palette = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
    (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)
]
class_colors = {}

def get_color_for_class(class_id):
    if class_id not in class_colors:
        color_index = class_id % len(color_palette)
        class_colors[class_id] = color_palette[color_index]
    return class_colors[class_id]

# Yazı font ayarları
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.45
thickness = 1
line_gap = 20
blank_area_height = 100

results = model.predict(source, save=True)

for result in results:
    image = cv2.imread(result.path)
    original_height, original_width = image.shape[:2]

    detection_data = []

    for box, score, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
        x1, y1, x2, y2 = map(int, box)
        confidence = f"{score:.2f}"
        class_id = int(cls)
        class_name = model.names[class_id]
        x_center = (x1 + x2) // 2

        detection_data.append({
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'x_center': x_center,
            'class_name': class_name,
            'confidence': confidence,
            'class_id': class_id,
            'gt_value': None
        })

    # Soldan sağa sırala
    detection_data.sort(key=lambda x: x['x_center'])

    # GT verilerini sırayla eşleştir
    gt_file_path = os.path.join(label_path, os.path.basename(result.path).replace('.jpeg', '.txt'))
    gt_values = []
    if os.path.exists(gt_file_path):
        with open(gt_file_path, 'r') as f:
            gt_values = [line.split()[0] for line in f.readlines()]
    for i, gt in enumerate(gt_values):
        if i < len(detection_data):
            detection_data[i]['gt_value'] = gt

    # Yazı genişliklerine göre toplam genişliği hesapla
    total_text_width = 0
    for det in detection_data:
        widest = max(
            cv2.getTextSize(det['class_name'], font, font_scale, thickness)[0][0],
            cv2.getTextSize(det['gt_value'], font, font_scale, thickness)[0][0] if det['gt_value'] else 0,
            cv2.getTextSize(det['confidence'], font, font_scale, thickness)[0][0]
        )
        total_text_width += widest + 30  # 30px aralık

    # Genişlik yetersizse padding uygula
    new_width = max(original_width, total_text_width + 10)
    combined_image = np.zeros((original_height + blank_area_height, new_width, 3), dtype=np.uint8)
    combined_image[:, :] = (255, 255, 255)  # Beyaz arka plan
    combined_image[:original_height, :original_width] = image

    for det in detection_data:
        x1, y1, x2, y2 = det['x1'], det['y1'], det['x2'], det['y2']
        x_center = det['x_center']
        color = get_color_for_class(det['class_id'])

        # Bounding box
        cv2.rectangle(combined_image, (x1, y1), (x2, y2), color, 2)

        # Yazıları ortalı şekilde kutunun altına yaz
        # Alt metin konumları (base_y başlangıç noktası)
        base_y = original_height + 20

        # 1. Class name
        text = det['class_name']
        size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.putText(combined_image, text, (x_center - size[0] // 2, base_y),
                    font, font_scale, (0, 0, 0), thickness)

        # 2. Ground truth (varsa)
        if det['gt_value']:
            text = det['gt_value']
            size, _ = cv2.getTextSize(text, font, font_scale, thickness)
            cv2.putText(combined_image, text, (x_center - size[0] // 2, base_y + line_gap),
                        font, font_scale, (0, 255, 0), thickness)

        # 3. Confidence
        text = det['confidence']
        size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        cv2.putText(combined_image, text, (x_center - size[0] // 2, base_y + 2 * line_gap),
                    font, font_scale, (0, 0, 255), thickness)

    # Görseli kaydet
    output_path = os.path.join(output_dir, os.path.basename(result.path))
    cv2.imwrite(output_path, combined_image)
