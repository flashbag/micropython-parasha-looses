# config.py

# --- МЕРЕЖЕВА КОНФІГУРАЦІЯ ---
# Встановіть True, щоб використовувати mock_data.py без спроби підключення до Wi-Fi.
USE_MOCK_DATA = False 

WIFI_SSID = "YOUR_WIFI_SSID" 
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# URL, з якого будуть завантажуватися дані.
NEWS_URL = "https://example.com/some-news-page" 

# --- КОНФІГУРАЦІЯ АПАРАТНОГО ЗАБЕЗПЕЧЕННЯ (OLED) ---
OLED_WIDTH = 128
OLED_HEIGHT = 32
I2C_FREQ = 400000  # 400 KHz
I2C_ADDR = 0x3C    # Типова адреса для SSD1306

# ПІНИ I2C (Ваші GPIO)
SDA_PIN = 21       
SCL_PIN = 22       

# --- КОНФІГУРАЦІЯ ІНТЕРФЕЙСУ (UI) ---
MAX_CHARS_PER_LINE = 16 
LINES_PER_PAGE = 2 
SCROLL_PAGE_DELAY_SEC = 3   # Затримка між сторінками статистики
SPLASH_SCREEN_DELAY_SEC = 5 # Затримка для заставки "GLORY TO UKRAINE!"


