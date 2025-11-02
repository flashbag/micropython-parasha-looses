# main.py
import time
import gc
# --- Імпорти власних модулів ---
from mock_data import MOCK_HTML_CONTENT
from parser import parse_html
from display import display_data
# ------------------------------

# --- ІМІТАЦІЯ ТА НАЛАШТУВАННЯ ---
# Тут можна розмістити реальні ініціалізації I2C/OLED,
# але залишаємо Mock для тестування
class MockOLED:
    def fill(self, color): print("\n--- OLED SCREEN (128x64) ---")
    def text(self, text, x, y, color): print(f"[{y:02d}]: {text}")
    def show(self): print("-----------------------------\n")

oled = MockOLED()
NEWS_URL = "https://example.com/some-news-page" 
# --------------------------------

def get_html_content(url):
    """Імітація завантаження контенту."""
    print('NOTE: Using mock data, skipping network connection.')
    # У реальному коді тут буде логіка urequests/network
    return MOCK_HTML_CONTENT

def run_main_loop():
    """Головний цикл, який запускає парсинг та вивід."""
    
    # 1. Завантаження даних
    html_data = get_html_content(NEWS_URL)
    
    # 2. Парсинг даних
    parsed_data = parse_html(html_data)
    
    # 3. Вивід на дисплей (з прокручуванням)
    # Передаємо oled-об'єкт та розпарсені дані
    display_data(oled, parsed_data)

    gc.collect()

# --- ЗАПУСК ---
if __name__ == '__main__':
    run_main_loop()
