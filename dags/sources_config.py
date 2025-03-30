from scrapers.az_cb import get_az_cb_links
from scrapers.ge_cb import get_ge_cb_links
from scrapers.kg_cb import get_kg_cb_links
from scrapers.kg_cb import parse_kg_article
from scrapers.rus_cb import get_rus_cb_links
from scrapers.tj_cb import get_tj_cb_links
from scrapers.tj_cb import parse_tj_article
from scrapers.uz_cb import get_uz_cb_links
from scrapers.uz_cb import parse_uz_article
from scrapers.kommersant import get_kommersant_links
from scrapers.interfax import get_interfax_links
from datetime import datetime

SOURCES_CONFIG = {
    "uz": {
        "country_code": "UZ",
        "base_url": "https://cbu.uz/ru/",
        "author_name": "Центробанк Узбекистана",
        "fetch_links_func": get_uz_cb_links,
        "parse_article_func": parse_uz_article
    },
    "tj": {
        "country_code": "TJ",
        "base_url": "https://www.nbt.tj/ru/news/",
        "author_name": "Центробанк Таджикистана",
        "fetch_links_func": get_tj_cb_links,
        "parse_article_func": parse_tj_article
    },
    "kg": {
        "country_code": "KG",
        "base_url": "https://www.nbkr.kg/all_news.jsp?lang=RUS&news_type=news-main",
        "author_name": "Центробанк Кыргызстана",
        "fetch_links_func": get_kg_cb_links,
        "parse_article_func": parse_kg_article
    },
    "az": {
        "country_code": "AZ",
        "base_url": "https://www.cbar.az/press-releases/1?language=en",
        "author_name": "Центробанк Азербайджана",
        "fetch_links_func": get_az_cb_links,
        "parse_article_func": None
    },
    "rus": {
        "country_code": "RUS",
        "base_url": "https://www.cbr.ru/news/",
        "author_name": "Центробанк РФ",
        "fetch_links_func": get_rus_cb_links,
        "parse_article_func": None
    },
    "ge": {
        "country_code": "GE",
        "base_url": "https://nbg.gov.ge/en/media/news/",
        "author_name": "Центробанк Грузии",
        "fetch_links_func": get_ge_cb_links,
        "parse_article_func": None
    },
    "interfax": {
        "country_code": "RUS",
        "base_url": "https://www.interfax.ru/news/" + datetime.today().strftime('%Y/%m/%d') + "/all/page_1",
        "author_name": "Интерфакс",
        "fetch_links_func": get_interfax_links,
        "parse_article_func": None
    },
    "kommersant": {
        "country_code": "RUS",
        "base_url": "https://www.kommersant.ru/archive/news/day",
        "author_name": "Коммерсантъ",
        "fetch_links_func": get_kommersant_links,
        "parse_article_func": None
    }
}