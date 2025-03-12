# Данный файл содержит логику сбора новостей с издания интерфакс (https://www.interfax.ru/)
# Парсинг выполняется через bs


from datetime import datetime
from bs4 import BeautifulSoup
import requests
import dateparser
from utils.create_soup import create_soup


def get_total_interfax_pages(soup):
    """Определяет количество страниц пагинации."""
    nav = soup.find('div', class_='nav')
    if not nav:
        return 1
    pages = nav.find('div', class_='pages')
    if not pages:
        return 1
    page_links = pages.find_all('a')
    return max(int(link.text) for link in page_links if link.text.isdigit())


def fetch_interfax_page_links(page_url):
    """Загружает ссылки с одной страницы."""
    response = requests.get(page_url)
    response.raise_for_status()
    page_html = response.text
    page_soup = BeautifulSoup(page_html, 'html.parser')
    news_divs = page_soup.find_all('div', class_='an')
    page_links = []
    base_url = page_url.split('//')[0] + '//' + page_url.split('/')[2]

    for div in news_divs:
        for item in div.find_all('div', {'data-id': True}):
            anchor = item.find('a')
            if anchor and 'href' in anchor.attrs:
                href = anchor['href']
                # Если ссылка относительная, добавляем базовый URL
                if href.startswith('/'):
                    href = base_url.rstrip('/') + href
                page_links.append(href)

    return page_links, page_soup


def get_interfax_links(url, header):
    # Загружаем первую страницу
    soup = create_soup(url, header)
    # Определяем количество страниц
    total_pages = get_total_interfax_pages(soup)
    # Извлекаем ссылки со всех страниц
    all_links = []
    for page in range(1, total_pages + 1):
        page_url = url[:-1] + str(page)
        page_links, _ = fetch_interfax_page_links(page_url)
        all_links.extend(page_links)

    return all_links