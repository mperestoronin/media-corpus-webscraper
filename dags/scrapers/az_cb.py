# Данный файл содержит логику сбора новостей с сайта центробанка Азербайджана https://www.cbar.az
# Парсинг выполняется через playwright


from datetime import datetime
import dateparser
from utils.create_soup import create_soup

def get_az_cb_links(url, header, target_date=None):
    """
    Парсит новости с сайта Центробанка Азербайджана (AZ).

    :param url: URL страницы с новостями.
    :param header: Заголовки запроса для получения HTML.
    :param target_date: Целевая дата для фильтрации новостей. Если None, используется сегодняшняя дата.
    :return: Список уникальных ссылок на новости за указанную дату.
    """
    if target_date is None:
        target_date = datetime.today()

    # Конфигурация для сайта Азербайджана
    config = {
        "selectors": {
            "news": "div.article_item",
            "date": "span",
            "link": "a.article_btn"
        },
        "base_url": "https://www.cbar.az",
        "date_format": "en",
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
                    link += "?language=en"
                    full_link = f"{config['base_url'].rstrip('/')}{link}" if link.startswith("/") else link
                    links.add(full_link)
            # Если новости отсортированы и текущая новость имеет дату меньше целевой, завершаем цикл
            if config["sort_required"] and news_date and news_date.date() < target_date.date():
                break
    return list(links)
