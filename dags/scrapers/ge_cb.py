# Данный файл содержит логику сбора новостей с сайта центробанка Грузии https://nbg.gov.ge/en
# Парсинг выполняется через playwright


from playwright.sync_api import sync_playwright
from datetime import datetime
import dateparser
from bs4 import BeautifulSoup



def get_ge_cb_links(url, header, target_date=None):
    if target_date is None:
        target_date = datetime.today()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        if header:
            page.set_extra_http_headers(header)
        page.goto(url)
        html = page.content()  # Получаем полный HTML
        browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    # Ищем все элементы с ссылками на новости
    news_items = soup.select('a[href]')
    links = []

    for news in news_items:
        date_element = news.find('p', class_='text-body1')
        if date_element:
            date_text = date_element.get_text(strip=True)
            news_date = dateparser.parse(date_text, languages=['en'])

            if news_date and news_date.date() == target_date.date():
                link = news.get('href')
                if link:
                    full_link = link if link.startswith('http') else f"https://www.nbg.gov.ge{link}"
                    links.append(full_link)
            elif news_date and news_date.date() < target_date.date():
                break

    return links