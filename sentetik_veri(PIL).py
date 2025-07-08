from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
import random
import numpy as np

def set_seed(seed_value):
    random.seed(seed_value)
    np.random.seed(seed_value)

def add_reddish_tint(image, red_factor=2, saturation_factor=0.5, variance_factor=0.7):
    """
    Görüntüye kırmızı ton ekler ve saturation/variance'ı azaltır.
    """
    # Kırmızı ton ekleme
    r, g, b = image.split()
    r = r.point(lambda i: i * red_factor)
    image = Image.merge('RGB', (r, g, b))
    
    # Saturation'ı azaltma
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation_factor)
    
    # Variance'ı azaltma (hafif bulanıklaştırma ile)
    image = image.filter(ImageFilter.GaussianBlur(radius=variance_factor)) 
    
    return image

def add_random_background(image, scale_factor=0.3):
    width, height = image.size
    bg_width, bg_height = int(width * scale_factor), int(height * scale_factor)

    selection_p_for_red_or_blue = np.random.uniform(0,1)
    random_color_list = []
    renk_id = 0
    if 0 <= selection_p_for_red_or_blue <= 0.7: # kırmızımsı görsel senaryo
        random_color_list.append(np.random.randint(35,100))
        random_color_list.append(np.random.randint(0,50))
        random_color_list.append(random_color_list[1])
        renk_id = 1
    elif 0.7 < selection_p_for_red_or_blue <= 0.85: # yeşilimsi görsel senaryo
        random_color_list.append(np.random.randint(0,40))
        random_color_list.append(np.random.randint(35,70))
        random_color_list.append(random_color_list[0])
        renk_id = 2
    elif 0.85 < selection_p_for_red_or_blue <= 1: # mavimsi görsel senaryo
        random_color_list.append(np.random.randint(0,50))
        random_color_list.append(random_color_list[0])
        random_color_list.append(np.random.randint(35,100))
        renk_id = 3

    random_color = tuple(random_color_list) # random_color_list i tuple objesine çevirdik

    background = np.full((bg_height, bg_width, 3), random_color, dtype=np.uint8)
    background_image = Image.fromarray(background)
    background_resized = background_image.resize((width, height), Image.NEAREST)
    image_rgb = image.convert("RGB")
    background_resized_rgb = background_resized.convert("RGB")
    if image_rgb.size != background_resized_rgb.size:
        background_resized_rgb = background_resized_rgb.resize(image_rgb.size)
    combined_image = Image.blend(image_rgb, background_resized_rgb, alpha=0.5)
    return combined_image, renk_id

def add_random_red_rectangle(image, probability=0.5):
    """
    Görüntüye, %50 olasılıkla kırmızı tonlarında dikdörtgen ekler.
    :param image: Girdi görüntüsü (PIL Image).
    :param probability: Dikdörtgenin eklenme olasılığı (0 ile 1 arasında bir değer).
    :return: Güncellenmiş görüntü.
    """
    if np.random.random() < probability:
        width, height = image.size
        
        rect_width = np.random.randint(5,9)  # Dikdörtgen genişliği

        rect_x_start = width - rect_width  # Dikdörtgenin başladığı x konumu
        rect_x_end = width  # Dikdörtgenin bittiği x konumu
        rect_y_start = 0  # Dikdörtgenin başladığı y konumu
        rect_y_end = height  # Dikdörtgenin bittiği y konumu

        # Çizim yapmak için bir Draw nesnesi oluştur
        draw = ImageDraw.Draw(image)

        # Dikdörtgeni kırmızının rastgele tonlarıyla doldur
        color = (np.random.randint(100, 200), np.random.randint(0, 50), np.random.randint(0, 50))  # Kırmızı tonları
        draw.rectangle([(rect_x_start, rect_y_start), (rect_x_end, rect_y_end)], fill=color)

    return image

def add_noise_to_image(image, noise_factor=0.04, probability=0.05):
    # 0.5 olasılıkla gürültü ekleme
    if np.random.random() < probability:
        image_rgb = image.convert('RGB')
        width, height = image_rgb.size
        noise = np.random.normal(scale=noise_factor, size=(height, width, 3))
        noisy_image = np.array(image_rgb) + noise * 255
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy_image)
    else:
        # Eğer gürültü eklenmeyecekse, orijinal görüntüyü döndür
        return image

def add_iso_noise_to_image(image, noise_factor=0.002, probability=0.3):
    """
    Görüntüye ISO benzeri gürültü ekler.
    :param image: Girdi görüntüsü (PIL Image).
    :param noise_factor: Gürültü yoğunluğu (0 ile 1 arasında bir değer).
    :param probability: Gürültü ekleme olasılığı (0 ile 1 arasında bir değer).
    :return: Gürültü eklenmiş görüntü.
    """
    # 0.5 olasılıkla gürültü ekleyip eklemeyeceğine karar ver
    if np.random.random() < probability:
        image_rgb = image.convert('RGB')
        np_image = np.array(image_rgb)

        # ISO gürültüsü için rastgele pikseller ekleyin
        noise = np.random.normal(scale=noise_factor, size=np_image.shape)
        noisy_image = np_image + noise * 255

        # Gürültülü görüntüyü sınırlayın (0-255 arasında değerler)
        noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

        return Image.fromarray(noisy_image)
    else:
        # Eğer gürültü eklenmeyecekse, orijinal görüntüyü döndür
        return image

if __name__ == "__main__":
    # Rastgelelik için seed ayarla
    seed_value = 42
    set_seed(seed_value)

# Görüntü ve tasarım özellikleri
image_width = 240
image_height = 45  # Görüntü yüksekliği
digit_color = (255, 255, 255)  # Rakamların rengi (beyaz)
background_color = (0, 0, 0)  # Arka plan rengi (siyah)
separator_color = (60, 60, 80)  # Ayıraç rengi (daha koyu mavi tonları)
digit_font_size = 40  # Rakam boyutu
separator_width = 1  # Ayıraç genişliği
digit_spacing = 10  # Rakamlar arası boşluk
num_images = 100  # Üretilecek görüntü sayısı
digits_per_image = 5  # Her görüntüdeki rakam sayısı

# Görüntülerin kaydedileceği klasör
save_directory = r"C:\Users\Mert\Desktop\PIL_images"
os.makedirs(save_directory, exist_ok=True)  # Klasör yoksa oluştur

# Yazı tipi ayarları (Varsayılan font kullanılabilir)
try:
    font = ImageFont.truetype(r"C:\Users\Mert\Desktop\yolo\html\Usta_GM_03_Font_final_to_gm_model.ttf", digit_font_size)
except IOError:
    font = ImageFont.load_default()

# Görüntü üretim döngüsü
for img_idx in range(num_images):
    # Uniform dağılımla rastgele rakamlar seç
    counter_value = ''.join(random.choices("0123456789", k=digits_per_image))

    # Rakam genişliğini ve yerleşimini ayarla
    digit_width = (image_width - (digits_per_image - 1) * digit_spacing) // digits_per_image

    # Yeni bir görüntü oluştur
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    # Rakamları ve ayıraçları çiz
    x_position = 0
    for i, digit in enumerate(counter_value):
        # Metin boyutunu hesapla
        bbox = draw.textbbox((0, 0), digit, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Metni dikey olarak ortalamak için y koordinatını hesapla
        y_position = (image_height - text_height) // 2

        # Dikey koordinatları rastgele değiştir (+5px veya -5px)
        apply_offset = np.random.random() < 0.5
        random_offset_y = np.random.choice([-4, 5]) if apply_offset else 0

        # Rakamı çiz
        draw.text((x_position + (digit_width - text_width) // 2, y_position + random_offset_y),
                  digit, fill=digit_color, font=font)

        # Bir sonraki rakamın x pozisyonunu ayarla
        x_position += digit_width + digit_spacing

        # Ayıraç çiz (son rakamdan sonra ayıraç eklenmez)
        if i < len(counter_value) - 1:
            separator_x = x_position - (digit_spacing // 2) - (separator_width // 2)
            draw.rectangle([separator_x, 0, separator_x + separator_width, image_height], fill=separator_color)

    # Görüntüye kırmızı ton ekle
    image = add_reddish_tint(image, red_factor=2, saturation_factor=0.5, variance_factor=0.7)

    # Arka plan ekle (örnek: kırmızı tonlu bir arka plan eklenebilir)
    image, renk_id = add_random_background(image, scale_factor=0.3)

    # Görüntüye kırmızı dikdörtgen ekle
    image = add_random_red_rectangle(image, probability=0.5)

    # Görüntüye gaussian noise ekle
    image = add_noise_to_image(image, noise_factor=0.3, probability=0.05)

    # Görüntüye iso noise ekle
    image = add_iso_noise_to_image(image, noise_factor=0.2, probability=0.3)

    # Görüntüyü kaydet
    save_path = os.path.join(save_directory, f"sayac_{img_idx + 1}.jpeg")
    image.save (save_path)  

print(f"{num_images} görüntü '{save_directory}' konumuna kaydedildi.")


