# main.py (ФІНАЛЬНА ВЕРСІЯ: ВИПРАВЛЕНО ВСІ ПОМИЛКИ І ПОРЯДОК ФУНКЦІЙ)
import time
import gc
import network
import usocket as socket
import ssl
from machine import Pin, I2C, reset 
from ssd1306 import SSD1306_I2C 

# --- Імпорти власних модулів ---
from config import (
    OLED_WIDTH, OLED_HEIGHT, I2C_FREQ, I2C_ADDR, SDA_PIN, SCL_PIN,
    WIFI_SSID, WIFI_PASSWORD, NEWS_URL, USE_MOCK_DATA 
)
from mock_data import MOCK_HTML_CONTENT 
from parser import parse_html
from display import display_data
# ------------------------------

# --- УТИЛІТИ OLED ---
def display_log(oled_or_mock, line1, line2=""):
    """Виводить лог-повідомлення на OLED-дисплей або в консоль."""
    # Якщо передано OLED-об'єкт (а не Mock)
    if hasattr(oled_or_mock, 'fill'):
        oled_or_mock.fill(0)
        oled_or_mock.text(line1, 0, 0, 1)
        oled_or_mock.text(line2, 0, 10, 1) 
        oled_or_mock.show()
    
    print(f"[OLED Log] {line1} / {line2}")


def init_i2c_bus():
    """Ініціалізація лише шини I2C. Повертає I2C-об'єкт або MockI2C."""
    try:
        # Ініціалізація I2C
        i2c = I2C(
            0, 
            scl=Pin(SCL_PIN), 
            sda=Pin(SDA_PIN), 
            freq=I2C_FREQ
        )
        print("I2C bus initialized successfully.")
        return i2c
        
    except Exception as e:
        print(f"Error initializing I2C bus: {e}")
        # Повертаємо заглушку, якщо I2C-шина не ініціалізована
        class MockI2C:
            def scan(self): return []
        return MockI2C()


def connect_wifi(oled_display_or_bus):
    """Підключення до Wi-Fi з логуванням та обробкою критичних помилок."""
    
    display_log(oled_display_or_bus, "Connecting...")
    
    wlan = network.WLAN(network.STA_IF)
    
    # ПРИМУСОВЕ СКИДАННЯ ТА АКТИВАЦІЯ СТЕКУ
    wlan.active(False) 
    time.sleep(0.5)
    wlan.active(True) 
    time.sleep(0.5)

    try:
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    except OSError as e:
        error_msg = str(e)
        display_log(oled_display_or_bus, "WIFI Error!", f"Code: {error_msg}")
        
        if "Wifi Internal Error" in error_msg or "105" in error_msg: 
             display_log(oled_display_or_bus, "Critical Fail!", "REBOOTING...")
             time.sleep(4)
             reset() # Програмне перезавантаження при критичній помилці
        else:
             time.sleep(3)
             return False 
             
    
    timeout = 15
    while timeout > 0:
        if wlan.isconnected():
            ip_info = wlan.ifconfig()
            display_log(oled_display_or_bus, "Connected!", f"IP: {ip_info[0]}")
            time.sleep(2)
            return True
        
        display_log(oled_display_or_bus, "Connecting...", f"Wait: {timeout}s")
        time.sleep(1)
        timeout -= 1

    display_log(oled_display_or_bus, "WiFi Failed!", "Using Mock Data.")
    time.sleep(3)
    return False


def secure_http_get(url):
    """Виконує HTTPS GET-запит (у MicroPython)."""
    try:
        proto, dummy, host, path = url.split("/", 3)
        path = "/" + path
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)
        else:
            port = 443 if proto == "https" else 80

        addr = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)[0]
        s = socket.socket(addr[0], addr[1], addr[2])
        s.settimeout(5) 
        s.connect(addr[4])

        if proto == "https":
            s = ssl.wrap_socket(s, server_hostname=host)

        s.send(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: MicroPython\r\nConnection: close\r\n\r\n".encode())

        data = b''
        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            data += chunk
            if b'\r\n\r\n' in data:
                data = data.split(b'\r\n\r\n', 1)[1] 
                break

        while True:
            chunk = s.recv(1024)
            if not chunk:
                break
            data += chunk

        s.close()
        return data.decode('utf-8')

    except Exception as e:
        print(f"HTTP/S fetch error: {e}")
        return None

# --- КОНТРОЛЕР ---
def get_html_content(oled, use_mock_data_flag):
    """
    Завантажує HTML-контент або використовує заглушку.
    Повертає: (HTML-контент, чи використовується заглушка).
    """
    
    if use_mock_data_flag:
        print('NOTE: Using mock data.')
        return MOCK_HTML_CONTENT, True
    
    connection_successful = connect_wifi(oled) 
    
    html_data = None
    
    if connection_successful:
        display_log(oled, "Fetching data...")
        html_data = secure_http_get(NEWS_URL)
        
        # КРИТИЧНО: ВИМКНЕННЯ WIFI ТА ОЧИЩЕННЯ (для запобігання MemoryError)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False) 
        gc.collect()
        
        if html_data:
            display_log(oled, "Fetch success!")
            time.sleep(1)
            return html_data, False 
        else:
            display_log(oled, "Fetch Failed!", "Using Mock Data.")
            time.sleep(3)
            print('FALLBACK: Fetch failed, using mock data.')
            return MOCK_HTML_CONTENT, True 
    
    else:
        # Wi-Fi не вдалося підключити
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False) 
        gc.collect()
        print('FALLBACK: WiFi failed, using mock data.')
        return MOCK_HTML_CONTENT, True
        

def run_main_loop(i2c_bus):
    """Головний цикл, який запускає ініціалізацію OLED, парсинг та вивід."""
    
    use_mock_data_current = USE_MOCK_DATA 
    oled_display = None # Ініціалізуємо дисплей тут
    
    while True: 
        gc.collect() 
        print("\n--- STARTING DATA CYCLE ---")
        
        # 1. Спроба ініціалізації OLED (після можливого скидання Wi-Fi)
        oled_or_mock = None 
        
        if oled_display is None:
            # Спроба ініціалізувати OLED-дисплей
            try:
                oled_display = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c_bus, I2C_ADDR)
                display_log(oled_display, "OLED ready.")
                oled_or_mock = oled_display

            except Exception as e:
                # Якщо OLED не знайшлося (ENODEV), використовуємо заглушку
                print(f"Error initializing OLED device: {e}")
                
                class MockOLED:
                    def fill(self, color): print("\n--- MOCK OLED SCREEN (128x32) ---")
                    def text(self, text, x, y, color): print(f"[{y:02d}]: {text}")
                    def hline(self, x, y, w, color): print(f"[{y:02d}]: {'-' * w}") 
                    def show(self): pass 
                oled_display = MockOLED()
                oled_or_mock = oled_display
                
        else:
            oled_or_mock = oled_display

        # 2. Завантаження даних (з логікою Wi-Fi/Mock та керуванням RAM)
        html_data, use_mock_data_current = get_html_content(oled_or_mock, use_mock_data_current)
        
        # 3. Парсинг даних
        parsed_data = parse_html(html_data)
        
        # 4. Вивід на дисплей 
        display_data(oled_or_mock, parsed_data) 

        # 5. Пауза перед наступним оновленням
        print("Waiting 5 seconds before next cycle (Simulation)...")
        time.sleep(5) 

# --- ЗАПУСК ---
if __name__ == '__main__':
    # 1. Ініціалізація I2C-шини
    i2c_bus = init_i2c_bus()
    
    # 2. Запуск циклу
    run_main_loop(i2c_bus)
