# Данный файл содержит логику сбора новостей с сайта центробанка Таджикистана https://www.nbt.tj
# Парсинг выполняется через playwright


from datetime import datetime
import dateparser
from utils.create_soup import create_soup
from utils.preprocess_text import remove_html_tags
from bs4 import BeautifulSoup
import requests

def get_tj_cb_links(url, header, target_date=None):
    if target_date is None:
        target_date = datetime.today()

    config = {
        "selectors": {
            "news": "div.card",
            "date": "div.card-footer .views",
            "link": "a.nav-link"
        },
        "base_url": "https://www.nbt.tj",
        "date_format": "ru",
        "sort_required": True
    }
    
    soup = create_soup(url, header)
    links = set()
    news_items = soup.select(config["selectors"]["news"])
    for news in news_items:
        date_element = news.select_one(config["selectors"]["date"])
        link_element = news.select_one(config["selectors"]["link"])
        if date_element and link_element:
            date_text = date_element.get_text(strip=True)
            news_date = dateparser.parse(date_text, languages=[config["date_format"]])
            if news_date and news_date.date() == target_date.date():
                link = link_element.get('href')
                if link:
                    full_link = f"{config['base_url'].rstrip('/')}{link}" if link.startswith("/") else link
                    links.add(full_link)
            # Если новости отсортированы и текущая новость имеет дату меньше целевой, завершаем цикл
            if config["sort_required"] and news_date and news_date.date() < target_date.date():
                break
    return list(links)


def parse_tj_article(url, header):
    response = requests.get(url, headers=header)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    title_element = soup.select_one("h4.news__article__title")
    title = title_element.get_text(strip=True) if title_element else "Заголовок не найден"
    content_elements = soup.select("p.text-left, div[style*='text-align']")
    text = " ".join([element.get_text(strip=True) for element in content_elements if element.get_text(strip=True)])
    text = remove_html_tags(text)
    return {
        "title": title,
        "text": text
    }
