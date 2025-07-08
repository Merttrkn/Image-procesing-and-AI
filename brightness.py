import os
import cv2
import numpy as np
import random

def set_seed(seed_value):
    random.seed(seed_value)
    np.random.seed(seed_value)

def random_window_size():
    """
    Rasgele bir pencere boyutu döner.
    """
    random_width = random.randint(130, 300)  # Genişlik aralığı
    random_height = random.randint(20, 60)   # Yükseklik aralığı
    return random_width, random_height

def apply_brightness_to_region(image, region, brightness_factor=2):
    """
    Belirli bir bölgeye parlaklık uygular.
    
    image: Görüntü
    region: Parlaklık uygulanacak bölgenin (x, y, genişlik, yükseklik) koordinatları
    brightness_factor: Parlaklık faktörü (1.0 normal, daha büyük değer daha parlak)
    """
    x, y, w, h = region
    sub_image = image[y:y+h, x:x+w]  # Bölgeyi seç
    sub_image = np.clip(sub_image * brightness_factor, 0, 255).astype(np.uint8)  # Bölgedeki parlaklığı değiştir
    image[y:y+h, x:x+w] = sub_image  # Değiştirilen bölgeyi geri yerleştir
    return image

def get_random_region(image_width, image_height):
    """
    Görüntü boyutlarına göre rastgele bir bölge seçer.
    """
    min_width, min_height = 20, 5
    max_width, max_height = 300, 60
    
    # Rastgele koordinatlar seç
    x = random.randint(0, image_width - min_width)
    y = random.randint(0, image_height - min_height)
    w = random.randint(min_width, min(max_width, image_width - x))
    h = random.randint(min_height, min(max_height, image_height - y))
    
    return (x, y, w, h)

def apply_random_brightness(image):
    """
    Görüntüye rastgele bir veya birden fazla bölgede farklı parlaklık uygular.
    """
    image_height, image_width, _ = image.shape
    
    # Rastgele bir sayıda bölge seç (1 ile 5 arasında)
    num_regions = random.randint(1, 5)
    
    # Belirtilen sayıda rastgele bölge seç ve her birine farklı parlaklık uygula
    for _ in range(num_regions):
        region = get_random_region(image_width, image_height)
        
        # Her bir bölge için farklı parlaklık faktörü belirle
        brightness_factor = random.uniform(1.2, 3.0)
        
        # Parlaklığı uygula
        image = apply_brightness_to_region(image, region, brightness_factor)
    
    return image

def resize_image_randomly(image):
    """
    Görüntüyü rastgele boyutlandırır.
    """
    random_width, random_height = random_window_size()
    resized_image = cv2.resize(image, (random_width, random_height))
    return resized_image

def resize_with_aspect_ratio(image, target_width, target_height):
    """
    Görüntüyü en-boy oranını koruyarak verilen genişlik ve yüksekliğe göre yeniden boyutlandırır.
    
    image: Orijinal görüntü
    target_width: İstenen maksimum genişlik
    target_height: İstenen maksimum yükseklik
    """
    original_height, original_width = image.shape[:2]
    aspect_ratio = original_width / original_height

    # Yeni boyutları hesapla
    if (target_width / target_height) > aspect_ratio:
        # Yüksekliği sınırla, genişlik oranını koru
        new_height = target_height
        new_width = int(new_height * aspect_ratio)
    else:
        # Genişliği sınırla, yükseklik oranını koru
        new_width = target_width
        new_height = int(new_width / aspect_ratio)

    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # Yeni boyutlara göre görüntüyü merkezde yastıkla (padding ekle)
    delta_w = target_width - new_width
    delta_h = target_height - new_height
    top, bottom = delta_h // 2, delta_h - (delta_h // 2)
    left, right = delta_w // 2, delta_w - (delta_w // 2)

    # Beyaz tonları için rastgele bir değer seç
    white_tone = random.randint(170, 255)  # 200-255 arası beyaz tonları
    color = [white_tone, white_tone, white_tone]  # RGB formatında beyaz ton

    # Seçilen beyaz tonuyla doldurma
    padded_image = cv2.copyMakeBorder(resized_image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return padded_image

def apply_augmentation(input_folder, output_folder):
    """
    Her görsele önce parlaklık uygulanmış halini kaydeder, sonra boyutlar değiştirilir.
    """
    images = os.listdir(input_folder)
    
    if __name__ == "__main__":
        # Rastgelelik için seed ayarla
        seed_value = 42
        set_seed(seed_value)
    
    for image_name in images:
        image_path = os.path.join(input_folder, image_name)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Unable to read image: {image_name}")
            continue
        
        # Parlaklık uygulanmış görüntüyü oluştur
        augmented_image = apply_random_brightness(image)
        
        # Rastgele hedef boyutlar
        target_width = random.randint(130, 300)
        target_height = random.randint(20, 50)

        # Görüntüyü yeniden boyutlandır (orijinal oranları koruyarak, beyaz tonları ile doldurarak)
        resized_image = resize_with_aspect_ratio(augmented_image, target_width, target_height)
        
        # Çıktıyı kaydet
        augmented_image_name = f"{os.path.splitext(image_name)[0]}_brightened.jpeg"
        augmented_output_path = os.path.join(output_folder, augmented_image_name)
        cv2.imwrite(augmented_output_path, resized_image)
        
        print(f"Saved augmented image: {augmented_image_name}")

input_folder = r"C:\Users\Mert\Desktop\su_sayac"  
output_folder = r"C:\Users\Mert\Desktop\parlaklik\images"  

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

apply_augmentation(input_folder, output_folder)

