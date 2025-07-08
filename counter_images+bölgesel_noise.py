from PIL import Image, ImageDraw, ImageFont
import os
import random
import json
from collections import Counter
import numpy as np

def set_seed(seed_value):
    random.seed(seed_value)
    np.random.seed(seed_value)

seed_value = 42
set_seed(seed_value)

# Rastgele seçilen rakamları takip etmek için bir sayaç
digit_usage_counter = Counter()

# JSON dosyasını yükleme
with open("water_meter_parametre.json", "r") as file:
    config_data = json.load(file)

def add_noise_to_image(image, noise_factor=0.05, probability=0.5):
    if np.random.random() < probability:
        image_rgb = image.convert('RGB')
        width, height = image_rgb.size
        noise = np.random.normal(scale=noise_factor, size=(height, width, 3))
        noisy_image = np.array(image_rgb) + noise * 255
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_image)
    else:
        return image

def add_iso_noise_to_image(image, noise_factor=0.2, probability=0.3):
    if np.random.random() < probability:
        image_rgb = image.convert('RGB')
        np_image = np.array(image_rgb)
        noise = np.random.normal(scale=noise_factor, size=np_image.shape)
        noisy_image = np_image + noise * 255
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_image)
    else:
        return image
    
# JSON'dan 'combinations' ve 'font_path' değerlerini al
combinations = config_data["combinations"]
font_path = config_data["font_path"]

def create_vertical_digits_image(output_dir, digit_width=30, digit_height=40, font_path="path_to_font", background_color="white", digit_color="black"):
    """
    30x440 piksel boyutunda, 0'dan 9'a kadar rakamların alt alta sıralandığı ve 9'dan sonra 0'ın da olduğu bir görüntü oluşturur.
    """
    try:
        font = ImageFont.truetype(font_path, 40)
    except IOError:
        raise Exception("Lütfen geçerli bir yazı tipi dosyası sağlayın.")

    image_height = digit_height * 11
    image = Image.new("RGB", (digit_width, image_height), color=background_color)
    draw = ImageDraw.Draw(image)

    for i in range(10):
        y_position = i * digit_height
        draw.text((digit_width // 2, y_position + digit_height // 2), str(i), font=font, fill=digit_color, anchor="mm")

    y_position = 10 * digit_height
    draw.text((digit_width // 2, y_position + digit_height // 2), "0", font=font, fill=digit_color, anchor="mm")

    image = add_noise_to_image(image, noise_factor=0.05, probability=0.5)  # Gürültü ekleme
    image = add_iso_noise_to_image(image, noise_factor=0.2, probability=0.3)  # ISO benzeri gürültü ekleme

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "vertical_digits_30x440.jpeg")
    image.save(file_path)

def crop_and_save_random_patches(input_image_path, patch_width=30, patch_height=40, num_patches=5):
    """
    Girdi görüntüsünden rastgele 30x40 boyutunda kırpılmış parçalar oluşturur ve sınıf değerlerini döndürür.
    """
    global digit_usage_counter  # Sayaç değişkeni global olarak kullanılacak
    image = Image.open(input_image_path)
    patch_width, image_height = image.size

    cropped_images = []
    class_labels = []

    for _ in range(num_patches):
        # Rastgele y pozisyonu belirle
        if random.random() < 0.3:
            start_y = random.randint(0, 400)
        else:
            start_y = random.choice(range(0, image_height, patch_height))

        start_x = 0
        cropped_image = image.crop((start_x, start_y, start_x + patch_width, start_y + patch_height))
        cropped_images.append(cropped_image)

          # Sınıf değerini belirle
        if 0 <= start_y <= 7:
            class_value = "0"
        elif 8 <= start_y <= 33:
            class_value = "0_1"
        elif 34 <= start_y <= 50:
            class_value = "1"
        elif 51 <= start_y <= 72:
            class_value = "1_2"
        elif 73 <= start_y <= 87:
            class_value = "2"
        elif 88 <= start_y <= 113:
            class_value = "2_3"
        elif 114 <= start_y <= 127:
            class_value = "3"
        elif 128 <= start_y <= 153:
            class_value = "3_4"
        elif 154 <= start_y <= 167:
            class_value = "4"
        elif 168 <= start_y <= 193:
            class_value = "4_5"
        elif 194 <= start_y <= 207:
            class_value = "5"
        elif 208 <= start_y <= 231:
            class_value = "5_6"
        elif 232 <= start_y <= 247:
            class_value = "6"
        elif 248 <= start_y <= 269:
            class_value = "6_7"
        elif 270 <= start_y <= 288:
            class_value = "7"
        elif 289 <= start_y <= 313:
            class_value = "7_8"
        elif 314 <= start_y <= 327:
            class_value = "8"
        elif 328 <= start_y <= 353:
            class_value = "8_9"
        elif 354 <= start_y <= 367:
            class_value = "9"
        elif 368 <= start_y <= 393:
            class_value = "9_0"
        elif 394 <= start_y <= 400:
            class_value = "0"
         
        class_labels.append(class_value)
        digit_usage_counter[class_value] += 1  # Sayaçta rakamın sayısını artır

    return cropped_images, class_labels

def create_counter_image_from_patches(cropped_images, output_dir, class_labels, patch_width=30, patch_height=40, gap=5, gap_color="white", image_index=1, fixed_zeros=False, fixed_zeros_bg_color="white", fixed_zeros_digit_color="black", font_path="path_to_font"):
    """
    Kırpılmış parçaları yan yana birleştirerek bir sayaç görüntüsü oluşturur.
    """
    # İlk iki sınıf değerini varsayılan olarak 0 ayarla
    if len(class_labels) >= 2:
        class_labels[0] = 0
        class_labels[1] = 0

    num_patches = len(cropped_images)
    image_width = num_patches * patch_width + (num_patches - 1) * gap
    image_height = patch_height

    combined_image = Image.new('RGB', (image_width, image_height), color=gap_color)

    if fixed_zeros:
        zero_image = Image.new('RGB', (patch_width, patch_height), color=fixed_zeros_bg_color)
        draw = ImageDraw.Draw(zero_image)
        try:
            font = ImageFont.truetype(font_path, 40)
        except IOError:
            raise Exception("Lütfen geçerli bir yazı tipi dosyası sağlayın.")

        draw.text((patch_width // 2, patch_height // 2), "0", font=font, fill=fixed_zeros_digit_color, anchor="mm")
        cropped_images[0] = zero_image
        cropped_images[1] = zero_image

    x_offset = 0
    for img in cropped_images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width + gap

    # Label dosyasını kaydet
    labels_dir = r"C:\Users\Mert\Desktop\water_meter\labels"
    os.makedirs(labels_dir, exist_ok=True)
    label_file_path = os.path.join(labels_dir, f"counter_image_{image_index}.txt")

    with open(label_file_path, "w") as label_file:
        for i, class_id in enumerate(class_labels):
            x_start = ((image_width / num_patches) / 2) 
            x_center = (x_start + (i * (image_width / num_patches))) / image_width
            y_center = 0.5  
            width = (image_width / num_patches) / image_width
            height = 0.95
            label_file.write(f"{class_id} {x_center:.3f} {y_center:.2f} {width:.3f} {height:.2f}\n")

    combined_image = add_noise_to_image(combined_image, noise_factor=0.05, probability=0.5)
    combined_image = add_iso_noise_to_image(combined_image, noise_factor=0.2, probability=0.3)

    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"counter_image_{image_index}.jpeg")
    combined_image.save(file_path)
     
def create_multiple_counter_images_with_combinations(num_images, combinations, output_dir):
    """
    Belirtilen kombinasyonlara ve oranlara göre sayaç görselleri oluşturur.
    """
    total_percentage = sum(combo['percentage'] for combo in combinations)
    if total_percentage != 100:
        raise ValueError("Kombinasyon yüzdelerinin toplamı 100 olmalıdır.")

    for combo in combinations:
        combo['num_images'] = int(num_images * combo['percentage'] / 100)

    image_index = 1
    for combo in combinations:
        for _ in range(combo['num_images']):
            # Grup 1 için rastgele parçalar oluştur
            create_vertical_digits_image(
                output_dir, font_path=font_path,
                background_color=combo['bg_color_group1'],
                digit_color=combo['digit_color_group1']
            )
            group1_patches, group1_labels = crop_and_save_random_patches(
                os.path.join(output_dir, "vertical_digits_30x440.jpeg"),
                num_patches=combo['patch_count_group1']
            )

            # Grup 2 için rastgele parçalar oluştur
            create_vertical_digits_image(
                output_dir, font_path=font_path,
                background_color=combo['bg_color_group2'],
                digit_color=combo['digit_color_group2']
            )
            group2_patches, group2_labels = crop_and_save_random_patches(
                os.path.join(output_dir, "vertical_digits_30x440.jpeg"),
                num_patches=combo['patch_count_group2']
            )

            # Group 2 için labellama ayarını kontrol et
            if combo.get('label', True):  # Eğer label=True ise
                all_patches = group1_patches + group2_patches
                all_labels = group1_labels + group2_labels
            else:  # Eğer label=False ise sadece Group 1'i kullan
                all_patches = group1_patches + group2_patches
                all_labels = group1_labels

            # Sayaç görüntüsü oluştur ve kaydet
            create_counter_image_from_patches(
                all_patches, output_dir, all_labels,
                gap=combo['gap'], gap_color=combo['gap_color'],
                image_index=image_index,
                fixed_zeros=True,
                fixed_zeros_bg_color=combo['fixed_zeros_bg_color'],
                fixed_zeros_digit_color=combo['fixed_zeros_digit_color'],
                font_path=font_path
            )
            image_index += 1

# Tüm süreç tamamlandığında kullanım sayılarını kaydeden bir fonksiyon
def save_digit_usage_stats(output_dir):
    stats_file_path = os.path.join(r"C:\Users\Mert\Desktop\water_meter", "digit_usage_histogram.txt")
    
    # Sayaçtaki rakamları küçükten büyüğe sıralama
    sorted_digit_usage = sorted(digit_usage_counter.items(), key=lambda item: int(item[0].split('_')[0]))

    with open(stats_file_path, "w") as stats_file:
        for digit, count in sorted_digit_usage:
            stats_file.write(f"{digit}: {count} adet kullanıldı\n")


# Görüntüleri oluşturduktan sonra sayaç sonuçlarını kaydetmek için fonksiyonu çağırıyoruz:
num_images = int(input("Toplam kaç görüntü oluşturmak istiyorsunuz? "))
output_dir = r"C:\Users\Mert\Desktop\water_meter\images"

create_multiple_counter_images_with_combinations(num_images, combinations, output_dir)

# Rastgele rakam kullanımlarını kaydet
save_digit_usage_stats(output_dir)
