import cv2
import os

# Girdi ve çıktı klasör yolları
input_folder = r"C:\Users\Mert\Desktop\su_sayac"             # Girdi klasörü
output_folder = r"C:\Users\Mert\Desktop\bitwise_images"      # Çıktı klasörü

# Çıktı klasörü yoksa oluştur
os.makedirs(output_folder, exist_ok=True)

# Desteklenen uzantılar
valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

# Klasördeki tüm dosyaları gez
for filename in os.listdir(input_folder):
    if any(filename.lower().endswith(ext) for ext in valid_extensions):
        image_path = os.path.join(input_folder, filename)
        image = cv2.imread(image_path)

        if image is None:
            print(f"Hata: {filename} okunamadı.")
            continue

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        # Görüntüyü gri tona çevir
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # CLAHE uygula
        clahe_applied = clahe.apply(gray)

        # Bitwise işlemi (negatif alma)
        inverted_image = cv2.bitwise_not(image)
        
        output_image = cv2.cvtColor(inverted_image, cv2.COLOR_GRAY2BGR)
        # Yeni dosya yolu
        output_path = os.path.join(output_folder, filename)

        # Görüntüyü kaydet
        cv2.imwrite(output_path, inverted_image)
        print(f"Kaydedildi: {output_path}")
