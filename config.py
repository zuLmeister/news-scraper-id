import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

BULAN_INDO = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'Mei': '05', 'Jun': '06',
    'Jul': '07', 'Aug': '08', 'Sep': '09', 'Okt': '10', 'Nov': '11', 'Des': '12'
}

REQUEST_DELAY = (0.3, 0.8)  # min, max delay antar request