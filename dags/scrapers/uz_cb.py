# Данный файл содержит логику сбора новостей с сайта центробанка Узбекистана https://cbu.uz
# Парсинг выполняется через playwright


from datetime import datetime
import dateparser
from bs4 import BeautifulSoup
import requests
import newspaper
from newspaper import Article
from utils.create_soup import create_soup

def get_uz_cb_links(url, header, target_date=None):
    if target_date is None:
        target_date = datetime.today()

    config = {
        "selectors": {
            "news": "a.update__inner",
            "date": "div.update__date span",
            "link": None
        },
        "base_url": "https://cbu.uz",
        "date_format": "ru",
    }

    soup = create_soup(url, header)
    links = set()
    # Выбираем все элементы новостей по селектору
    news_items = soup.select(config["selectors"]["news"])
    for news in news_items:
        date_element = news.select_one(config["selectors"]["date"])
        # Если селектор ссылки не указан, используем сам элемент новости
        link_element = news if config["selectors"]["link"] is None else news.select_one(config["selectors"]["link"])
        if date_element and link_element:
            date_text = date_element.get_text(strip=True)
            news_date = dateparser.parse(date_text, languages=[config["date_format"]])
            if news_date and news_date.date() == target_date.date():
                link = link_element.get('href')
                if link:
                    # Формируем абсолютный URL, если ссылка относительная
                    full_link = f"{config['base_url'].rstrip('/')}{link}" if link.startswith("/") else link
                    links.add(full_link)
    return list(links)



def parse_uz_article(url, header):
    soup = create_soup(url, header)
    article_div = soup.find('div', class_='main_text', itemprop='articleBody')
    if not article_div:
        return ""
    article = Article(url)
    article.download()
    article.parse()
    title = article.title
    text = article_div.get_text(separator="\n", strip=True)
    return {
        "title": title,
        "text": text
    }
    
    