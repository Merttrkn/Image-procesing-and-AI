
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import numpy as np
import random

def set_seed(seed_value):
    random.seed(seed_value)
    np.random.seed(seed_value)

# Kaydedilecek klasör
output_folder = r"C:\Users\Mert\Desktop\noisy_images"
os.makedirs(output_folder, exist_ok=True)

# Selenium ayarları
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırır
chrome_options.add_argument("--window-size=260x60")  # Kombinasyonları sığdıracak küçük bir pencere boyutu

# ChromeDriver'ı başlatın
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# HTML dosyasını bir kez oluşturun
html_file_path = "sentetik.html"

# HTML başlangıcı (sadece genel yapıyı yazıyoruz)
with open(html_file_path, "w") as dosya:
    dosya.write("""

<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kombinasyonlar</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">

    <style>
        /* Yerel font tanımlaması */
        @font-face {
            font-family: 'Usta_GM_01';
            src: url('C:/Users/Mert/Desktop/yolo/html/Usta_GM_01_Font.ttf') format('truetype');
        }
        body {  
            display: flex;  
            justify-content: center;  
            align-items: center;  
            flex-wrap: wrap;  
            height: 100vh;  
            margin: 0;  
            background-color: white;
            font-family: 'Usta_GM_01', sans-serif; 
        }  
        .sayaç-görüntü {  
            display: flex;  
            background-color: #0f0f0f;  
            padding: 5px;  
            margin: 0px;  
        }  
        .rakam {  
            font-size: 40px;  
            color: white;  
            width: 40px;  
            height: 25px;  
            display: flex;  
            justify-content: center;  
            align-items: center;    
            margin: 2px;  
            position: relative;  
        }        
        
        .rakam:not(:last-child)::after {
            content: "";
            position: absolute;
            top: -10px;
            right: -2px;
            width: 2px;
            height: calc(100% + 20px);
            background: linear-gradient(to bottom, #555555, #222222);
            mix-blend-mode: difference;
            z-index: 1;
        }
    </style>   
</head>  
<body>  
<div class="sayaç-görüntü" id="kombinasyon-alani"></div>

<script>
  function randomizeDigitPositions() {
      const digits = document.querySelectorAll('.rakam');
      digits.forEach(digit => {
          // Her rakamın üst pozisyonunu rastgele bir değere ayarlayın
          const randomTop = Math.floor(Math.random() * 10) - 5; // -5 ile +5 px arasında
          digit.style.top = `${randomTop}px`;
      });
  }

  function applyFontStyles() {
    const digits = document.querySelectorAll('.rakam');
    
    digits.forEach(digit => {
        const digitValue = digit.textContent.trim(); // Rakama göre fontu seç

        // Dinamik font eşleştirmesi
        switch (digitValue) {
            case "0": 
            case "1":
            case "2":
            case "3":
            case "4":
            case "5":
            case "6":
            case "7":
            case "8":
            case "9":
                digit.style.fontFamily = "'Usta_GM_01', sans-serif";
                break;  
            default:
                digit.style.fontFamily = "'Roboto', sans-serif"; // Diğer rakamlar için varsayılan font
        }
    });
}

  // Sayfa yüklendiğinde rastgele pozisyonları ve font stillerini uygula
  window.onload = () => {
      randomizeDigitPositions();
      applyFontStyles();
  };

  // Kombinasyon değiştiğinde çağırılabilir
  function updateRandomDigits() {
      randomizeDigitPositions();
      applyFontStyles();
  }
</script>
</body>
</html>

""")

# HTML dosyasını açın
driver.get("file://" + os.path.abspath(html_file_path))

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

# Arka plan ekleme fonksiyonu
def add_random_background(image, red_tane, green_tane, blue_tane, scale_factor=0.3):
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
        
        rect_width = np.random.randint(5,10)  # Dikdörtgen genişliği

        rect_x_start = width - rect_width  # Dikdörtgenin başladığı x konumu
        rect_x_end = width  # Dikdörtgenin bittiği x konumu
        rect_y_start = 0  # Dikdörtgenin başladığı y konumu
        rect_y_end = height  # Dikdörtgenin bittiği y konumu

        # Çizim yapmak için bir Draw nesnesi oluştur
        draw = ImageDraw.Draw(image)

        # Dikdörtgeni kırmızının rastgele tonlarıyla doldur
        color = (random.randint(100, 200), random.randint(0, 50), random.randint(0, 50))  # Kırmızı tonları
        draw.rectangle([(rect_x_start, rect_y_start), (rect_x_end, rect_y_end)], fill=color)

    return image
    
def generate_random_numbers(num_digits, low=0, high=10):
    """
    Generates random numbers based on uniform distribution.
    :param num_digits: Number of digits to generate.
    :param low: Minimum value (inclusive).
    :param high: Maximum value (exclusive).
    :return: List of random digits.
    """
    return [str(int(np.random.uniform(low, high))) for _ in range(num_digits)]

# Save image with noise
def add_noise_to_image(image, noise_factor=0.3, probability=0.05):
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

def add_iso_noise_to_image(image, noise_factor=0.2, probability=0.3):
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

# Main loop to generate random numbers and save images
num_samples = 100  # Number of images to generate
num_digits = 5  # Number of digits in each sample
change_position_probability = 0.7  # %70 olasılıkla konumlar değişsin

red_tane = 0
green_tane = 0
blue_tane = 0

if __name__ == "__main__":
    # Rastgelelik için seed ayarla
    seed_value = 42
    set_seed(seed_value)

for index in range(num_samples):
    # Rastgele sayılar oluştur
    random_digits = generate_random_numbers(num_digits)

    # HTML kombinasyonunu oluştur
    kombinasyon_html = ''.join([f'<div class="rakam">{digit}</div>' for digit in random_digits])

    # HTML'yi güncelle ve font stillerini uygula
    driver.execute_script(f"""
        document.getElementById('kombinasyon-alani').innerHTML = '{kombinasyon_html}';
        randomizeDigitPositions();
        applyFontStyles();
    """)

    # Rastgele pozisyon değiştirme olasılığı
    if np.random.random() < change_position_probability:
        time.sleep(0.5)

    # Ekran görüntüsü al
    element = driver.find_element("id", "kombinasyon-alani")
    screenshot_path = os.path.join(output_folder, f"random_{index}.jpeg")
    element.screenshot(screenshot_path)

    # Görüntüyü işleyip kaydet
    image = Image.open(screenshot_path)
    image_with_background, renk_id = add_random_background(image, red_tane, green_tane, blue_tane, scale_factor=0.3)

    if renk_id == 0:
        print("")
    elif renk_id == 1:
        red_tane += 1
    elif renk_id == 2:
        green_tane += 1
    else:
        blue_tane += 1

    updated_image = add_random_red_rectangle(image_with_background, probability=0.5)
    iso_noisy_image = add_iso_noise_to_image(updated_image, noise_factor=0.2)
    noisy_image = add_noise_to_image(iso_noisy_image, noise_factor=0.1)
    noisy_image.save(screenshot_path)
    print(f"{index + 1} nolu görüntü oluşturuldu.")
print("kırmızımsı görsel adet: ", red_tane)
print("yeşilimsi görsel adet: ", green_tane)
print("mavimsi görsel adet: ", blue_tane)



