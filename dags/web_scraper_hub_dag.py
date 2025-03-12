import json
import time
import os
from functools import partial
from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaProducer
import dateparser
import requests
from datetime import datetime, timedelta
import newspaper
from newspaper import Article
from random import randint
from time import sleep
from newspaper import Config
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


SCRAPEOPS_API_KEY = os.environ.get("SCRAPEOPS_API_KEY")


def get_headers_list(**kwargs):
    response = requests.get(f'http://headers.scrapeops.io/v1/browser-headers?api_key={SCRAPEOPS_API_KEY}')
    json_response = response.json()
    headers_list = json_response.get('result', [])

    # сохранение в XCom
    kwargs['ti'].xcom_push(key='headers_list', value=headers_list)


def get_random_header(header_list, **kwargs):
    """Получение случайного заголовка из переданного списка"""
    random_index = randint(0, len(header_list) - 1)
    return header_list[random_index]

def prepare_article(url, header):
    config = Config()
    config.headers = header
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()
    return article


def prepare_for_kafka(country, source, title, text, summary, keywords, date, article_url, source_url):
    return {
        "country": country,
        "source": source,
        "title": title,
        "text": text,
        "summary": summary,
        "keywords": keywords,
        "date": date,
        "article_url": article_url,
        "source_url": source_url
    }


target_date = target_date = datetime.today()

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
        "base_url": "https://www.interfax.ru/news/2024/12/28/all/page_1",
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

def fetch_news_from_source(source_config, **kwargs):
    ti = kwargs['ti']
    headers_list = ti.xcom_pull(task_ids='get_headers_list', key='headers_list')
    header = get_random_header(headers_list)
    fetch_func = source_config["fetch_links_func"]
    base_url = source_config["base_url"]
    country_code = source_config["country_code"]
    author_name = source_config["author_name"]
    news_links = fetch_func(base_url, header)
    news_articles = []
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
    )
    
    for url in news_links:
        time.sleep(randint(10, 100))
        article = prepare_article(url, header)
        article.authors = author_name
        
        # если article пуст — вызываем parse_<источник>_article, если он задан
        parse_func = source_config.get("parse_article_func")
        if ((article.title == "" or article.text == "") and parse_func) or (article.authors == "Центробанк Узбекистана"):
            article_content = parse_func(url, header)
            article.title = article_content.get("title", "")
            article.text = article_content.get("text", "")
            #  может дополнительно вызвать .parse()?
            article.nlp()
            
        # Отправляем в Kafka, только если есть заголовок и текст
        if article.title != "" and article.text != "":
            news = prepare_for_kafka( country_code, article.authors, article.title, article.text, article.summary, article.keywords, str(target_date), url, base_url)
            try:
                producer.send("unclassified_news", value=news)
            except Exception as e:
                print(f"Ошибка при отправке в Kafka: {e}")
            news_articles.append(article)
    producer.flush()
    producer.close()
    print(f"Новости {author_name}:", *[art.title for art in news_articles])

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'web_scraper_hub_dag',
    default_args=default_args,
    description='Scrape news from various news sources',
    schedule_interval='@daily',
    catchup=False,
)


init_headers_task = PythonOperator(
    task_id='get_headers_list',
    python_callable=get_headers_list,
    provide_context=True,
    dag=dag,
)

news_tasks = []
for source_key, config in SOURCES_CONFIG.items():
    task_id = f"fetch_{source_key}_news"
    task = PythonOperator(
        task_id=task_id,
        python_callable=partial(fetch_news_from_source, config),
        dag=dag
    )
    news_tasks.append(task)


init_headers_task >> news_tasks