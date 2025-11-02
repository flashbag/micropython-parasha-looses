# display.py (ФІНАЛЬНА ВЕРСІЯ)
import time
from parser import ABBREVIATIONS

# --- КОНСТАНТИ UI ---
MAX_CHARS_PER_LINE = 16 
LINES_PER_PAGE = 5  
# --------------------

def format_loss_line(category, increment):
    """Форматує один рядок втрат: ABBR: +Increment."""
    abbreviated_category = ABBREVIATIONS.get(category, category[:4]) 
    display_line = f"{abbreviated_category:<5}: {increment}"
    return display_line[:MAX_CHARS_PER_LINE]


def display_data(oled, data):
    """
    Виводить дані на OLED-екран із прокручуванням (пагінацією).
    """
    datetime_str = data["datetime"]
    
    # 1. Фільтруємо втрати: залишаємо тільки ті, де інкремент не дорівнює "+0"
    filtered_losses = [
        loss for loss in data["losses"] if loss['increment'] != '+0'
    ]
    
    # *** 2. СОРТУВАННЯ ЗА СПАДАННЯМ ***
    # Сортуємо список, використовуючи числове значення інкременту (прибираємо знак '+')
    try:
        filtered_losses.sort(
            key=lambda x: int(x['increment'].lstrip('+')), # Перетворюємо "+N" на число N
            reverse=True # Сортування за спаданням
        )
    except ValueError:
        # Залишаємо список несортованим у випадку помилки перетворення
        print("WARNING: Could not sort losses by increment value.")


    total_losses = len(filtered_losses)
    total_pages = (total_losses + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    
    # ... (Обробка нульових втрат без змін) ...
    if total_losses == 0:
        oled.fill(0)
        date_only = datetime_str.split('T')[0].replace('-', '/')
        oled.text(date_only, 0, 0, 1)
        oled.text("No new increments.", 0, 20, 1)
        oled.show()
        time.sleep(3)
        return

    for page in range(total_pages):
        oled.fill(0) 
        
        # 1. РЯДОК 0 (Y=0): ДАТА 
        date_only = datetime_str.split('T')[0].replace('-', '/')
        oled.text(date_only, 0, 0, 1) 
        
        # 2. РЯДОК 1 (Y=10): Індикатор Сторінки
        page_indicator = f"PAGE {page+1}/{total_pages}" 
        oled.text(page_indicator, 0, 10, 1) 

        # 3. Вивід ВІДФІЛЬТРОВАНИХ І СОРТОВАНИХ втрат
        y_pos = 20 # Початок виводу втрат
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
             print(f"[{20 + (i - start_index) * 10}]: {format_loss_line(filtered_losses[i]['category'], filtered_losses[i]['increment'])}")
        # ----------------------------------------
        
        oled.show()
        time.sleep(3)
