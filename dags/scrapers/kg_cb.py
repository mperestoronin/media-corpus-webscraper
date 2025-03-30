# Данный файл содержит логику сбора новостей с сайта центробанка Кыргызстана (https://www.nbkr.kg)
# Парсинг выполняется через bs


from datetime import datetime
from bs4 import BeautifulSoup
import dateparser
from utils.create_soup import create_soup
from utils.preprocess_text import remove_html_tags

def get_kg_cb_links(url, header, target_date=None):
    if target_date is None:
        target_date = datetime.today()

    config = {
        "selectors": {
            "news": "div.content-text",
            "date": "span:contains('Дата:')",
            "link": "a:contains('Постоянная ссылка')"
        },
        "base_url": "https://www.nbkr.kg",
        "date_format": "ru",
        "sort_required": True
    }

    soup = create_soup(url, header)
    links = set()

    # Ищем контейнер с новостями
    news_container = soup.select_one(config['selectors']['news'])
    if news_container:
        # Проходим по всем элементам <span> внутри контейнера
        for block in news_container.find_all('span'):
            text = block.get_text(strip=True)
            if text.startswith("Дата:"):
                date_text = text.replace('Дата:', '').strip()
                news_date = dateparser.parse(date_text, languages=[config['date_format']])
                if news_date and news_date.date() == target_date.date():
                    # Находим ссылку с текстом "Постоянная ссылка"
                    link_element = block.find_next('a', string=lambda text: text and 'Постоянная ссылка' in text)
                    if link_element:
                        link = link_element.get('href')
                        if link:
                            # Формируем абсолютный URL
                            full_link = f"{config['base_url'].rstrip('/')}{link}" if link.startswith("/") else link
                            links.add(full_link)
                elif news_date and news_date.date() < target_date.date():
                    # Прерываем цикл, если достигли новостей более ранней даты
                    break
    return list(links)


def parse_kg_article(url, header):
    soup = create_soup(url, header)
    title_element = soup.find("p", class_=lambda x: x and "RVPS1" in x)
    title = title_element.get_text(strip=True) if title_element else "Без названия"
    content_container = soup.find("div", class_="content-text")
    if content_container:
        content_elements = content_container.find_all("p")
        text = " ".join([element.get_text(strip=True) for element in content_elements if element.get_text(strip=True)])
    else:
        text = "Текст статьи не найден."

    text = remove_html_tags(text)
    return {
        "title": title,
        "text": text
    }