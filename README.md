# News Scraper ID 🇮🇩

Scraper berita Indonesia dari berbagai portal berita populer (detik.com, kompas.com, cnnindonesia.com, dll).

<img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python version" />
<img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Project status" />

## Fitur utama

- Mengambil judul, tanggal, kategori, isi berita, dan URL
- Mendukung beberapa portal berita besar Indonesia
- Hasil disimpan dalam format CSV yang mudah dibaca

## Portal yang saat ini didukung

| Portal              | Status     | Catatan                              |
|---------------------|------------|--------------------------------------|
| detik.com           | ✅ Aktif   | termasuk detikHealth, detikFinance   |
| kompas.com          | ✅ Aktif   | termasuk tren & olahraga             |
| cnnindonesia.com    | ✅ Aktif   |                                      |
| tribunnews.com      | ⚠️ Parsial| beberapa kategori kadang berubah     |
| liputan6.com        | ✅ Aktif   |                                      |
| viva.co.id          | 🔧 Testing | masih dalam pengembangan             |

## Instalasi

```bash
# Clone repository
git clone https://github.com/zuLmeister/news-scraper-id.git
cd news-scraper-id

# (opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

### Struktur Folder
```
news-scraper-id/
├── scraper/               
│   ├── __init__.py
│   ├── sites.py
│   ├── utils.py
│   └── worker.py
├── ui/               
│   ├── __init__.py
│   ├── main_window.py       
├── requirements.txt
└── README.md
```
