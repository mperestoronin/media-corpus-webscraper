# Данный файл содержит логику сбора новостей с сайта центробанка РФ (https://www.cbr.ru/)
# Парсинг выполняется через playwright

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def get_rus_cb_links(url, header):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        if header:
            page.set_extra_http_headers(header)
        page.goto(url)
        page.wait_for_timeout(5000)  # Ждём 5 секунд для загрузки контента

        # Получаем HTML после рендеринга JavaScript
        content = page.content()
        browser.close()

        # Парсим HTML с BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        news_items = soup.select('div.news_text')

        links = []
        for news in news_items:
            date = news.select_one('div.news_date')
            if date and date.get_text(strip=True).lower() == 'сегодня':
                link = news.find('a', class_='news_title')['href']
                if link[0] == '/':
                    links.append("https://www.cbr.ru" + link)
                else:
                    links.append(link)
            else:
                break

        return links