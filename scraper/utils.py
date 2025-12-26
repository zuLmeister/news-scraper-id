import re
from datetime import datetime
from config import BULAN_INDO

def clean_date_indo(raw_date: str) -> str:
    """Konversi tanggal Indonesia ke format YYYY-MM-DD"""
    try:
        if not raw_date:
            return datetime.now().strftime('%Y-%m-%d')
        
        raw_date = re.sub(r'\b(WIB|WITA|WIT)\b', '', raw_date).strip()
        parts = raw_date.split()
        
        if len(parts) < 3:
            return datetime.now().strftime('%Y-%m-%d')
        
        if ',' in raw_date:
            parts = raw_date.split(',', 1)[1].strip().split()
        
        day = parts[0].zfill(2)
        month_str = parts[1][:3]
        year = parts[2]
        month = BULAN_INDO.get(month_str, '01')
        
        return f"{year}-{month}-{day}"
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')


def filter_sentences(full_text: str, keyword: str) -> str:
    """Ambil kalimat yang mengandung keyword"""
    if not full_text:
        return ""
    
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', full_text)
    relevant = [
        s.replace('\n', ' ').strip()
        for s in sentences
        if keyword.lower() in s.lower()
    ]
    return " | ".join(relevant)


def calculate_level(title: str, full_text: str, keyword: str) -> str:
    """Hitung level relevansi berita"""
    k = keyword.lower()
    t = title.lower()
    txt = full_text.lower()
    
    score = 0
    if k in t:
        score += 3
    
    count = txt.count(k)
    if count > 5:
        score += 3
    elif count > 2:
        score += 2
    elif count > 0:
        score += 1
    
    if score >= 5:
        return "High"
    elif score >= 3:
        return "Medium"
    return "Low"