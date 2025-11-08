# display.py (ФІНАЛЬНА ВЕРСІЯ - ВИКОРИСТОВУЄ config.py)
import time
from parser import ABBREVIATIONS
# Імпортуємо всі константи з config.py
from config import LINES_PER_PAGE, MAX_CHARS_PER_LINE, SPLASH_SCREEN_DELAY_SEC, SCROLL_PAGE_DELAY_SEC 

# --- КОНСТАНТИ UI ---
# MAX_CHARS_PER_LINE, LINES_PER_PAGE тепер імпортуються з config.py
# --------------------

def format_loss_line(category, increment):
    """Форматує один рядок втрат: ABBR: +Increment. Використовує збережені абревіатури."""
    # Використовуємо абревіатури з пам'яті користувача (вбудовано)
    user_abbreviations = {
        'особового складу': 'PIDR', 
        'танків': 'TANKS', 
        'бойових броньованих машин': 'BBM', 
        'артилерійських систем': 'ART', 
        'РСЗВ': 'RSZV', 
        'засоби ППО': 'PPO', 
        'літаків': 'PLANE', 
        'гелікоптерів': 'HELI', 
        'БпЛА оперативно-тактичного рівня': 'UAV', 
        'крилаті ракети': 'MSL', 
        'кораблі / катери': 'SHIP', 
        'підводні човни': 'SUBM', 
        'автомобільна техніка та автоцистерни': 'AUTO', 
        'спеціальна техніка': 'SPEC'
    }
    # Використовуємо абревіатуру користувача, або ABBREVIATIONS, якщо немає
    abbreviated_category = user_abbreviations.get(category, ABBREVIATIONS.get(category, category[:4]))
    
    # Виводимо значення без дужок
    display_line = f"{abbreviated_category:<5}: {increment}"
    return display_line[:MAX_CHARS_PER_LINE]


def display_splash_screen(oled):
    """Виводить фінальну заставку "GLORY TO UKRAINE!" на 5 секунд."""
    TEXT_LINE1 = "GLORY TO" 
    TEXT_LINE2 = "UKRAINE!" 
    
    oled.fill(0) 
    
    # Центрування тексту: (8 символів * 8 пікселів/символ = 64 пікселі)
    CENTER_OFFSET = 32
    
    # Вертикальне розташування для 32px висоти 
    oled.text(TEXT_LINE1, CENTER_OFFSET, 12, 1) 
    oled.text(TEXT_LINE2, CENTER_OFFSET, 22, 1) 
    
    # Вивід у консоль для відлагодження
    print("\n--- SPLASH SCREEN ---")
    print(TEXT_LINE1)
    print(TEXT_LINE2)
    print("---------------------\n")
    
    oled.show()
    time.sleep(SPLASH_SCREEN_DELAY_SEC) # Використовуємо константу з config.py


def display_data(oled, data):
    """
    Виводить дані на OLED-екран із прокручуванням (пагінацією) та викликає заставку.
    """
    datetime_str = data["datetime"]
    
    # 1. Фільтруємо втрати
    filtered_losses = [
        loss for loss in data["losses"] if loss['increment'] != '+0'
    ]
    
    # *** 2. СОРТУВАННЯ ЗА СПАДАННЯМ ***
    try:
        filtered_losses.sort(
            key=lambda x: int(x['increment'].lstrip('+').replace(' ', '')), 
            reverse=True
        )
    except ValueError:
        print("WARNING: Could not sort losses by increment value. Check data format.")

    total_losses = len(filtered_losses)
    total_pages = (total_losses + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    
    if total_losses == 0:
        oled.fill(0)
        date_only = datetime_str.split('T')[0].replace('-', '/')
        oled.text(date_only, 0, 0, 1)
        oled.text("No new increments.", 0, 20, 1)
        oled.show()
        time.sleep(SCROLL_PAGE_DELAY_SEC) # Використовуємо константу
        
    else:
        for page in range(total_pages):
            oled.fill(0) 
            
            # 1. РЯДОК 0 (Y=0): ДАТА + ЛІЧИЛЬНИК СТОРІНОК
            date_only = datetime_str.split('T')[0].replace('-', '/')
            page_counter = f"{page+1}/{total_pages}" 
            combined_header = f"{date_only} {page_counter:>5}"
            
            oled.text(combined_header, 0, 0, 1) 
            
            # 2. ГОРИЗОНТАЛЬНА ЛІНІЯ (РОЗДІЛЬНИК)
            oled.hline(0, 9, 128, 1) 
            
            # 3. Вивід ВТРАТ
            y_pos = 11 
            start_index = page * LINES_PER_PAGE
            end_index = min(start_index + LINES_PER_PAGE, total_losses)
            
            for i in range(start_index, end_index):
                loss = filtered_losses[i]
                final_line = format_loss_line(loss['category'], loss['increment']) 
                oled.text(final_line, 0, y_pos, 1)
                y_pos += 10 
            
            # --- КОНСОЛЬНИЙ ВИВІД ДЛЯ ВІДЛАГОДЖЕННЯ ---
            print(f"\n--- Scroll Page {page+1} of {total_pages} (Sorted) ---")
            for i in range(start_index, end_index):
                 console_y = 11 + (i - start_index) * 10 
                 loss = filtered_losses[i]
                 print(f"[{console_y}]: {format_loss_line(loss['category'], loss['increment'])}")
            # ----------------------------------------
            
            oled.show()
            time.sleep(SCROLL_PAGE_DELAY_SEC) # Використовуємо константу
        
    # ВИКЛИК ЗАСТАВКИ
    display_splash_screen(oled)

