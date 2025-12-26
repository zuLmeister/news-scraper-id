import re
from datetime import datetime
from config import BULAN_INDO

def clean_date_indo(raw_date: str) -> str:
    """
    Convert an Indonesian date string into YYYY-MM-DD format.
    
    Strips timezone indicators `WIB`, `WITA`, and `WIT`, accepts comma-separated variants, and resolves Indonesian month abbreviations using `BULAN_INDO`. If `raw_date` is empty or cannot be parsed, returns the current date in `YYYY-MM-DD`.
    
    Parameters:
        raw_date (str): Indonesian date string (may include day, month name/abbreviation, year, and optional timezone).
    
    Returns:
        str: Date in `YYYY-MM-DD` format; current date if input is falsy or parsing fails.
    """
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
    """
    Extract sentences from the given text that contain the specified keyword.
    
    Parameters:
        full_text (str): The text to search; may contain multiple sentences and newlines.
        keyword (str): The term to match within sentences; matching is case-insensitive.
    
    Returns:
        str: The matched sentences with internal newlines replaced by spaces, trimmed, and joined by " | ". Returns an empty string if no sentences contain the keyword or if `full_text` is empty.
    """
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
    """
    Determine relevance level of a news item based on occurrences of a keyword in the title and full text.
    
    Parameters:
        title (str): The news title; matching is case-insensitive.
        full_text (str): The full news content; matching is case-insensitive.
        keyword (str): The keyword to search for.
    
    Description:
        Scoring:
          - +3 points if the keyword appears in the title.
          - In the full text, +1 point if the keyword appears at least once, +2 points if it appears more than 2 times, +3 points if it appears more than 5 times.
    
    Returns:
        str: "High" if score >= 5, "Medium" if score >= 3, "Low" otherwise.
    """
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