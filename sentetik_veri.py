from PIL import Image, ImageDraw, ImageFont
import os
import random
import numpy as np
from albumentations import Compose, RandomBrightnessContrast

# Rastgelelik için seed ayarı
def set_seed(seed_value):
    random.seed(seed_value)
    np.random.seed(seed_value)

# Albumentations ile farklı parlaklık ve kontrast ayarı için fonksiyon
def get_transforms_for_areas(seed):
    return {
        "digits": Compose([
            RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0, p=1.0),
        ]),
        "background": Compose([RandomBrightnessContrast(brightness_limit=0, contrast_limit=0, p=1.0)]),
    }

def add_noise_to_image(image, noise_factor=0.2, probability=0.5):
    # 0.5 olasılıkla gürültü ekleme
    if np.random.random() < probability:
        # Eğer gürültü eklenmeyecekse, orijinal görüntüyü döndür
        if isinstance(image, np.ndarray):
            image_rgb = Image.fromarray(image)  # NumPy array'den PIL Image'e dönüşüm
        else:
            image_rgb = image.convert('RGB')  # Eğer zaten PIL Image ise, bu adımı geç

        width, height = image_rgb.size
        noise = np.random.normal(scale=noise_factor, size=(height, width, 3))
        noisy_image = np.array(image_rgb) + noise * 255
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_image)
    else:
        return image  # Gürültü eklenmezse, orijinal görüntü döndürülür

def create_counter_image(output_path, image_width, image_height, digits_per_image, segment_gap, segment_height, transforms):
    # Görüntü oluşturma
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)

    # Hane boyutları ve yerleşim
    digit_width, digit_height = 30, 40  # Her bir hanenin boyutları
    gap = 15  # Haneler arasındaki boşluk
    total_width = digits_per_image * digit_width + (digits_per_image - 1) * gap  # Sayaç toplam genişliği

    # Başlangıç koordinatlarını dinamik hesaplama
    start_x = (image_width - total_width) // 2  # Haneleri yatayda ortala
    start_y = (image_height - digit_height) // 2  # Haneleri dikeyde ortala

    # Font seçimi (sayılar için)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        print("Arial font bulunamadı, varsayılan font kullanılacak.")
        font = ImageFont.load_default()

    # Sayaç hanelerini çiz
    digit_masks = []  # Kutucukların maskelerini tutacak
    for i in range(digits_per_image):  # Her bir hane için döngü
        digit_x = start_x + i * (digit_width + gap)
        digit_rect = [digit_x, start_y, digit_x + digit_width, start_y + digit_height]
        
        # Ana kutuyu çiz
        draw.rectangle(digit_rect, outline="gray", width=2)
        digit_masks.append(digit_rect)

        
        black_bar_width = random.randint(1, 3)  # Siyah dikdörtgenin genişliği
        black_bar_x1 = digit_x + digit_width - black_bar_width  # Sağ kenarın iç kısmı
        black_bar_x2 = black_bar_x1 + black_bar_width  # Siyah çubuğun genişliği
        bottom_margin = 0  # Kutunun alt kenarından boşluk bırakma
        num_segments = 3  # Siyah dikdörtgen sayısı

        # Siyah dikdörtgenlerin yerini ve boyutunu ayarla
        for j in range(num_segments):
            segment_y1 = start_y + digit_height - bottom_margin - ((j + 1) * segment_height) - (j * segment_gap)
            segment_y2 = segment_y1 + segment_height
            draw.rectangle([black_bar_x1, segment_y1, black_bar_x2, segment_y2], fill="black")

        # Rakamları rastgele seç ve yerleştir
        digit_text = random.choice("0123456789")
        bbox = draw.textbbox((0, 0), digit_text, font=font)
        text_width = bbox[2] - bbox[0]
        # text_height = bbox[3] - bbox[1]                          
        text_x = digit_x + (digit_width - text_width) // 2
        ascent, descent = font.getmetrics()
        text_y = start_y + (digit_height - ascent - descent) // 2
        draw.text((text_x, text_y), digit_text, fill="black", font=font)

    # Albumentations ile transform uygula
    np_image = np.array(image)
    digit_mask_image = np.zeros_like(np_image[:, :, 0])  # Mask için siyah-beyaz görüntü
    for rect in digit_masks:
        digit_mask_image[rect[1]:rect[3], rect[0]:rect[2]] = 255  # Kutucukları beyaz yap

    # Farklı bölgelere farklı transform uygula
    digits_area = transforms["digits"](image=np_image, mask=digit_mask_image)["image"]
    background_area = transforms["background"](image=np_image, mask=255 - digit_mask_image)["image"]

    # İki alanı birleştir
    final_image = np.where(digit_mask_image[:, :, None] == 255, digits_area, background_area)

    # Gürültü ekle
    final_image = add_noise_to_image(final_image, noise_factor=0.2, probability=0.5)

    # final_image bir numpy.ndarray olduğundan önce Image.fromarray ile dönüştür
    final_image = np.uint8(final_image)  # Bu adımda veri tipi uyumlu hale getiriliyor
    final_image = Image.fromarray(final_image)

    # Görüntüyü kaydet
    final_image.save(output_path, format="JPEG")


if __name__ == "__main__":
    seed_value = 42
    set_seed(seed_value)

    # Parametreler
    image_width = 210
    image_height = 40  # Görüntü yüksekliği
    digits_per_image = 5  # Her görüntüdeki rakam sayısı
    num_images = 100  # Üretilecek görüntü sayısı
    segment_gap = 5  # Siyah dikdörtgenler arasındaki boşluk
    segment_height = 8  # Her bir siyah dikdörtgenin yüksekliği

    # Görüntülerin kaydedileceği klasör
    output_directory = r"C:\Users\Mert\Desktop\su_sayac"
    os.makedirs(output_directory, exist_ok=True)  # Klasör yoksa oluştur

    # Transform tanımla
    transforms = get_transforms_for_areas(seed=seed_value)

    # Görüntü üretim döngüsü
    for img_idx in range(num_images):
        output_path = os.path.join(output_directory, f"water_meter_{img_idx + 1}.jpeg")
        create_counter_image(output_path, image_width, image_height, digits_per_image, segment_gap, segment_height, transforms)

        print(f"Görsel '{output_path}' konumuna başarıyla kaydedildi!")
