# scraper/sites.py
from bs4 import BeautifulSoup
import requests
from config import HEADERS
from .utils import clean_date_indo


def _clean_body(body, tags_to_remove=None):
    """Helper untuk bersihkan body artikel dari elemen tak diinginkan"""
    if not body:
        return ""
    if tags_to_remove:
        for tag in tags_to_remove:
            for elem in body(tag):
                elem.decompose()
    return body.get_text(separator=" ", strip=True)



def parse_detik_list(soup: BeautifulSoup):
    articles = []
    for item in soup.find_all('article'):
        try:
            title_tag = item.find('h3', class_='media__title')
            if not title_tag:
                continue
            a_tag = title_tag.find('a')
            link = a_tag['href']
            title = a_tag.get_text(strip=True)

            date_span = item.find('span', {'title': True})  
            raw_date = date_span['title'] if date_span else ""

            articles.append({'url': link, 'title': title, 'raw_date': raw_date})
        except Exception:
            continue
    return articles


def parse_detik_content(soup: BeautifulSoup) -> str:
    body = soup.find('div', class_='detail__body-text')
    return _clean_body(body, ['script', 'style', 'iframe', 'div', 'a', 'figure'])



def parse_cnn_list(soup: BeautifulSoup):
    articles = []
    for item in soup.find_all('article'):
        try:
            a_tag = item.find('a', href=True)
            if not a_tag or not a_tag['href'].startswith('https://www.cnnindonesia.com/'):
                continue
            link = a_tag['href']

            title_tag = item.find('h2') or item.find('span', class_='title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            time_tag = item.find('time') or item.find('span', class_='date')
            raw_date = time_tag.get_text(strip=True) if time_tag else ""

            articles.append({'url': link, 'title': title, 'raw_date': raw_date})
        except Exception:
            continue
    return articles


def parse_cnn_content(soup: BeautifulSoup) -> str:
    body = soup.find('div', class_='detail_text') or soup.find('div', class_='news-content')
    return _clean_body(body, ['script', 'style', 'iframe', 'table', 'aside', 'figure'])



def parse_liputan6_list(soup: BeautifulSoup):
    articles = []
    for item in soup.find_all('article', class_='articles--iridescent-list--item'):
        try:
            a_tag = item.find('a', class_='ui--a', href=True) or item.find('a', href=True)
            if not a_tag:
                continue
            link = a_tag['href']
            if not link.startswith('http'):
                link = 'https://www.liputan6.com' + link

            title_tag = item.find('h4', class_='articles--iridescent-list--text-title')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            time_tag = item.find('time', class_='articles--iridescent-list--text-time')
            raw_date = time_tag['title'] if time_tag and time_tag.has_attr('title') else time_tag.get_text(strip=True) if time_tag else ""

            articles.append({'url': link, 'title': title, 'raw_date': raw_date})
        except Exception:
            continue
    return articles


def parse_liputan6_content(soup: BeautifulSoup) -> str:
    body = soup.find('div', class_='article-content-body')
    return _clean_body(body, ['script', 'style', 'iframe', 'figure', 'div.read-page--header', 'p.baca-juga'])



def parse_suara_list(soup: BeautifulSoup):
    articles = []
    for item in soup.find_all('div', class_='item-news'):
        try:
            a_tag = item.find('a', href=True)
            if not a_tag:
                continue
            link = a_tag['href']
            if not link.startswith('http'):
                link = 'https://www.suara.com' + link

            title_tag = a_tag.find('h3') or a_tag.find('h4')
            title = title_tag.get_text(strip=True) if title_tag else ""

            date_tag = item.find('span', class_='date') or item.find('time')
            raw_date = date_tag.get_text(strip=True) if date_tag else ""

            if title:
                articles.append({'url': link, 'title': title, 'raw_date': raw_date})
        except Exception:
            continue
    return articles


def parse_suara_content(soup: BeautifulSoup) -> str:
    body = soup.find('div', class_='detail-content') or soup.find('div', class_='news-detail-text')
    return _clean_body(body, ['script', 'style', 'iframe', 'figure', 'div.bacajuga', 'aside'])



SITES = [
    {
        'name': 'Detik',
        'list_url': lambda keyword, page: f"https://www.detik.com/search/searchall?query={keyword}&siteid=2&sortby=time&page={page}",
        'parse_list': parse_detik_list,
        'parse_content': parse_detik_content
    },
    {
        'name': 'CNN Indonesia',
        'list_url': lambda keyword, page: f"https://www.cnnindonesia.com/search/?query={keyword}&page={page}",
        'parse_list': parse_cnn_list,
        'parse_content': parse_cnn_content
    },
    {
        'name': 'Liputan6',
        'list_url': lambda keyword, page: f"https://www.liputan6.com/search?q={keyword}&page={page}",
        'parse_list': parse_liputan6_list,
        'parse_content': parse_liputan6_content
    },
    {
        'name': 'Suara',
        'list_url': lambda keyword, page: f"https://www.suara.com/search?q={keyword}&page={page}",
        'parse_list': parse_suara_list,
        'parse_content': parse_suara_content
    }
]