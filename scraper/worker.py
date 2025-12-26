# scraper/worker.py
import os
import time
import random
import pandas as pd
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_DELAY
from .sites import SITES
from .utils import clean_date_indo, filter_sentences, calculate_level


class ScraperWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)  # path file atau empty

    def __init__(self, keyword: str, min_year: int, target_n: int, output_dir: str):
        super().__init__()
        self.keyword = keyword
        self.min_year = min_year
        self.target_n = target_n
        self.output_dir = output_dir
        self.is_running = True

    def run(self):
        all_data = []
        total_collected = 0

        self.log_signal.emit(f"=== MULAI SCRAPING: '{self.keyword.upper()}' ===")
        self.log_signal.emit(f"Target: {self.target_n} berita | Min Tahun: {self.min_year}")

        for site in SITES:
            if not self.is_running or total_collected >= self.target_n:
                break

            self.log_signal.emit(f"\n---> Scraping dari: {site['name']}")
            page = 1
            consecutive_empty = 0

            while self.is_running and total_collected < self.target_n:
                if consecutive_empty >= 5:
                    self.log_signal.emit(f"    [STOP] Terlalu banyak halaman kosong di {site['name']}")
                    break

                try:
                    url = site['list_url'](self.keyword, page)
                    resp = requests.get(url, headers=HEADERS, timeout=15)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    articles = site['parse_list'](soup)
                    if not articles:
                        consecutive_empty += 1
                        page += 1
                        continue

                    found_in_page = 0
                    for art in articles:
                        if total_collected >= self.target_n or not self.is_running:
                            break

                        date_clean = clean_date_indo(art.get('raw_date', ''))
                        try:
                            year = int(date_clean.split('-')[0])
                            if year < self.min_year:
                                continue
                        except:
                            pass

                        if any(d['URL'] == art['url'] for d in all_data):
                            continue

                        try:
                            detail_resp = requests.get(art['url'], headers=HEADERS, timeout=15)
                            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                            full_text = site['parse_content'](detail_soup)

                            if len(full_text) < 150:
                                continue

                            level = calculate_level(art['title'], full_text, self.keyword)
                            context = filter_sentences(full_text, self.keyword)

                            all_data.append({
                                'Website': site['name'],
                                'Keyword': self.keyword,
                                'Level': level,
                                'Tanggal': date_clean,
                                'Judul': art['title'],
                                'Context': context,
                                'URL': art['url'],
                                'Full_Text': full_text[:3000]
                            })

                            total_collected += 1
                            found_in_page += 1
                            self.progress_signal.emit(total_collected)
                            self.log_signal.emit(f"    [OK] {art['title'][:50]}... ({date_clean})")

                            time.sleep(random.uniform(*REQUEST_DELAY))

                        except Exception as e:
                            self.log_signal.emit(f"    [ERR] Gagal ambil detail {art['url']}: {str(e)}")
                            continue

                    if found_in_page == 0:
                        consecutive_empty += 1
                    else:
                        consecutive_empty = 0

                    page += 1

                except requests.RequestException as e:
                    self.log_signal.emit(f"    [ERR] Koneksi error halaman {page}: {str(e)}")
                    consecutive_empty += 1
                    page += 1

        # Simpan hasil
        if all_data and self.is_running:
            filename = f"Result_{self.keyword}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            path = os.path.join(self.output_dir, filename)
            try:
                pd.DataFrame(all_data).to_csv(path, index=False, encoding='utf-8-sig')
                self.log_signal.emit(f"\nBERHASIL DISIMPAN: {path}")
                self.finished_signal.emit(path)
            except Exception as e:
                self.log_signal.emit(f"\nGAGAL SIMPAN: {str(e)}")
                self.finished_signal.emit("")
        else:
            self.log_signal.emit("\nTidak ada data yang berhasil dikumpulkan.")
            self.finished_signal.emit("")

    def stop(self):
        self.is_running = False
        self.log_signal.emit("Proses dihentikan oleh user...")