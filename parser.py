# parser.py (ФІНАЛЬНА ВЕРСІЯ)
import ure

# Нові абревіатури
ABBREVIATIONS = {
    'особового складу': 'PIDR',
    'танків': 'TANK',
    'бойових броньованих машин': 'BBMS',
    'артилерійських систем': 'ARTS',
    'РСЗВ': 'RSZV',
    'засоби ППО': 'PPOS',
    'літаків': 'PLNE',
    'гелікоптерів': 'HELI',
    'БпЛА оперативно-тактичного рівня': 'UAVS',
    'крилаті ракети': 'MSLS',
    'кораблі / катери': 'SHIP',
    'підводні човни': 'SUBM',
    'автомобільна техніка та автоцистерни': 'AUTO',
    'спеціальна техніка': 'SPEC',
}

def parse_html(html_content):
    """
    Парсить HTML-вміст та повертає словник з усіма даними, включаючи інкремент.
    """
    data = {
        "title": "Title not found.",
        "datetime": "Datetime not found.",
        "losses": []
    }

    title_pattern = ure.compile('<h1.*?class="post_title">(.*?)</h1>')
    title_match = title_pattern.search(html_content)
    if title_match: data["title"] = title_match.group(1).strip()

    date_pattern = ure.compile('<time class="article_date" datetime="(.*?)">')
    date_match = date_pattern.search(html_content)
    if date_match: data["datetime"] = date_match.group(1).strip()
    
    # --- ВИЛУЧЕННЯ ВТРАТ З ІНКРЕМЕНТОМ ---
    start_marker = "<ul>"
    end_marker = "</ul>"

    list_start = html_content.find(start_marker)
    list_end = html_content.find(end_marker)

    if list_start != -1 and list_end != -1:
        list_content = html_content[list_start + len(start_marker) : list_end]
        item_start_tag = "<li>"
        item_end_tag = "</li>"
        
        pos = 0
        while True:
            start_index = list_content.find(item_start_tag, pos)
            if start_index == -1: break
            end_index = list_content.find(item_end_tag, start_index)
            if end_index == -1: break
                
            value_start = start_index + len(item_start_tag)
            item = list_content[value_start:end_index]
            clean_item = item.strip()
            
            if '–' in clean_item:
                parts = clean_item.split('–')
                category = parts[0].strip()
                full_details = parts[1].strip()
                
                # 1. Очищення основних деталей
                cleaned_details = full_details.replace('близько', '').strip()
                cleaned_details = cleaned_details.replace(' осіб;', '').replace(' од;', '').strip()
                cleaned_details = cleaned_details.strip().rstrip(';')
                
                total = cleaned_details
                increment = "+0" # Інкремент за замовчуванням (без дужок)
                
                # 2. ЕКСТРАКЦІЯ ІНКРЕМЕНТУ (з дужок)
                if '(' in cleaned_details and ')' in cleaned_details:
                    start_inc = cleaned_details.find('(')
                    end_inc = cleaned_details.find(')')
                    
                    # Витягуємо вміст дужок та прибираємо самі дужки
                    increment_with_parens = cleaned_details[start_inc : end_inc + 1].strip()
                    increment = increment_with_parens.replace('(', '').replace(')', '')
                    
                    total = cleaned_details[:start_inc].strip()
                
                data["losses"].append({
                    'category': category, 
                    'total': ' '.join(total.split()),
                    'increment': increment  # Зберігаємо чистий інкремент (+N)
                })
                
            pos = end_index + len(item_end_tag)
    
    return data
